import pylast
import pandas as pd
from urllib import quote_plus,unquote_plus
import os
import codecs
from urllib import unquote_plus
import multiprocessing
from multiprocessing import Process, Queue
import sys
import time

import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(os.path.expanduser('~')+'/item_data/log')
formatter = logging.Formatter('%(asctime)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

API_KEY,API_SECRET = open('lastfm.apikey').readlines()
datadir = os.path.expanduser('~')+'/item_data/'
itemlist_dir = os.path.expanduser('~')+'/lastfm_itemlist.txt'
#itemlist_dir = 'P:/Projects/BigMusic/jared.rawdata/lastfm_itemlist.txt'

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

#item_data = pd.read_table(itemlist_dir,header=None,names=['item_id','item_type','artist','artist_id','album','song','item_url','top_tag','total_scrobbles','unique_listeners'],nrows=None)#.sort_values(by='total_scrobbles',ascending=False)

#item_data = item_data[item_data['item_type']!=1][['item_id','item_type','artist','song']]

names_songs = ['item_id','artist','song','new_album_id','correction','duration','mbid','tags','wiki']
songs_complete = set()
if os.path.exists(datadir+'songs'):
    for line in open(datadir+'songs','r'):
        songs_complete.add(int(line[:line.find('\t')]))


names_artists = ['item_id','artist','correction','mbid','tags','bio']
artists_complete = set()
if os.path.exists(datadir+'artists'):
    for line in open(datadir+'artists','r'):
        artists_complete.add(int(line[:line.find('\t')]))

# names_albums = ['new_album_id','artist','album','mbid','release_data','tags','wiki']
# albums_complete = {}
# line = None
# if os.path.exists(datadir+'albums'):
#     for line in open(datadir+'albums','r'):
#         line.split('\t',3)[:3]
#         albums_complete['\t'.join([line[1:3]])] = int(line[0])
# if line:
#     album_id_idx = int(line[0])
# else:
#     album_id_idx = 0

def WSError_check(command):
    try:
        return command.__call__()
    except pylast.WSError as e:
        if ' not found' in e.details:
            return None

def feed(queue, parlist):
    for par in parlist:
        queue.put(par)

def calc(queueIn, queueOut):
    while True:
        try:
            par = queueIn.get(block=True)
            if par is None:
                queueIn.put(None)
                break
            try:
                res = process(par)
            except:
                logger.info("process : Exception raised : {} ({})".format(par, sys.exc_info()))
                res = None

            queueOut.put(res)

        except:
            logger.info("calc : Exception raised : {}" .format(sys.exc_info()))
            break

def write(queue, song_handle,artist_handle):
    while True:
        try:
            res = queue.get(timeout=2)
            if res is not None:
                if res[0] == 'song':
                    song_handle.write(res[1].encode('utf8')+'\n')
                    song_handle.flush()
                elif res[0] == 'artist':
                    artist_handle.write(res[1].encode('utf8')+'\n')
                    artist_handle.flush()

        except:
            logger.info("write: Exception raised:" , sys.exc_info())
            break



#item_list = list(zip(item_data['item_id'],item_data['item_type'],item_data['artist'],item_data['song']))

def process(row):
    print row
    item_id,item_type,artist,song = row
    attempts = 0
    while attempts <= 5:
        try:
            if item_type==2:
                if item_id in songs_complete:
                    raise Exception('song already processed ({})'.format(artist,song))

                trk = network.get_track(artist=unquote_plus(artist),title=unquote_plus(song))
                album = WSError_check(trk.get_album)
                trk_correction = WSError_check(trk.get_correction)
                trk_duration = WSError_check(trk.get_duration)
                #listener_count = trk.get_listener_count()
                #playcount = trk.get_playcount()
                trk_mbid = WSError_check(trk.get_mbid)
                trk_wiki = WSError_check(trk.get_wiki_content)
                if trk_wiki:
                    trk_wiki = trk_wiki.replace('\n','\\n')
                trk_tags = WSError_check(trk.get_top_tags)
                if trk_tags:
                    trk_tagdata = u'|'.join([u"{}:{}".format(t.item.name,t.weight) for t in trk_tags])
                else:
                    trk_tagdata = None

                if album:
                    album_artist = album.artist.name
                    album_title = album.title
                    album_key = '\t'.join([album_artist,album_title])

                else:
                    album_artist = None
                    album_title = None
                    album_key = None


                song_result = '\t'.join(map(lambda x: x if x else u'', [str(item_id), artist, song, trk_correction, str(trk_duration), trk_mbid, album_artist, album_title, trk_tagdata, trk_wiki]))
                if attempts>0:
                    logger.info('network error resolved after {} extra attempts ({},{})'.format(attempts, artist,song))
                return 'song',song_result

            elif item_type == 0:

                if item_id in artists_complete:
                    raise Exception('artists already processed ({})'.format(artist))

                a = network.get_artist(unquote_plus(artist))
                try:
                    bio = a.get_bio_content()
                except AttributeError:
                    bio = None
                if bio:
                    bio = bio.replace('\n','\\n')
                correction = a.get_correction()
                mbid = a.get_mbid()
                tags = a.get_top_tags()
                if tags:
                    tagdata = u'|'.join([u"{}:{}".format(t.item.name,t.weight) for t in tags])
                else:
                    tagdata = None

                artist_result = u'\t'.join(map(lambda x: x if x else u'', [str(item_id), artist, correction, mbid, tagdata, bio]))
                return 'artist', artist_result

        except pylast.NetworkError as e:
            logger.info('network error ({},{}); will try {} more times'.format(artist,song,5-attempts))
            time.sleep(5+attempts)
            attempts += 1
    raise(e)

if __name__ == '__main__':
    nthreads = 16
    batch_size=100000
    batch_start=0

    # [['item_id','item_type','artist','song']]
    #item_list = list(zip(item_data['item_id'],item_data['item_type'],item_data['artist'],item_data['song']))

    #with codecs.open(datadir+'songs','a','utf-8') as songs, codecs.open(datadir+'artists','a','utf-8') as artists, codecs.open(datadir+'albums','a','utf-8') as albums:
    with open(datadir+'songs','a') as songs, open(datadir+'artists','a') as artists:
        #, open(datadir+'albums','a') as albums:

        while True:
            #clist = item_list[batch_start:batch_start+batch_size]
            item_data = pd.read_table(itemlist_dir,header=None,names=['item_id','item_type','artist','artist_id','album','song','item_url','top_tag','total_scrobbles','unique_listeners'],nrows=batch_size,skiprows=batch_start)

            item_data = item_data[item_data['item_type']!=1][['item_id','item_type','artist','song']]

            clist = list(zip(item_data['item_id'],item_data['item_type'],item_data['artist'],item_data['song']))


            if len(clist) == 0:
                break
            #clist.append(None)

            logger.info("Batch started ({} rows starting at {})".format(batch_size,batch_start))

            workerQueue = Queue()
            writerQueue = Queue()
            feedProc = Process(target = feed , args = (workerQueue, clist))
            calcProc = [Process(target = calc, args = (workerQueue, writerQueue)) for i in range(nthreads)]
            writProc = Process(target = write, args = (writerQueue, songs, artists))


            feedProc.start()
            for p in calcProc:
                p.start()
            writProc.start()

            feedProc.join()
            for p in calcProc:
                p.join()

            writProc.join()

            batch_start += batch_size
            logger.info("Batch COMPLETED ({} rows starting at {})".format(batch_size,batch_start))
            #time.sleep(10)




"""
# previewing data
names_songs = ['item_id','artist','song','new_album_id','correction','duration','mbid','tags','wiki']
print '-'*200
print pd.read_table('songs',header=None,names=names_songs).head()
print '-'*200
names_artists = ['item_id','artist','correction','mbid','tags','bio']
print pd.read_table('artists',header=None,names=names_artists).head()
print '-'*200
names_albums = ['new_album_id','artist','album','mbid','release_date','tags','wiki']
print pd.read_table('albums',header=None,names=names_albums).head()
print '-'*200
"""






