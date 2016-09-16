import pylast
import pandas as pd
from urllib import quote_plus,unquote_plus
import os
import codecs
from urllib import unquote_plus
import multiprocessing
from multiprocessing import Process, Queue
import sys


API_KEY,API_SECRET = open('lastfm.apikey').readlines()
outfile = 'data/lastfm_top_similar_artists_new'
datadir = 'P:/Projects/BigMusic/jared.rawdata/item_data/'

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

item_data = pd.read_table('P:/Projects/BigMusic/jared.rawdata/lastfm_itemlist.txt',header=None,names=['item_id','item_type','artist','artist_id','album','song','item_url','top_tag','total_scrobbles','unique_listeners'],nrows=10000)#.sort_values(by='total_scrobbles',ascending=False)

item_data = item_data[item_data['item_type']!=1][['item_id','item_type','artist','song']]

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
                print("process: %s / Exception raised:" , par, sys.exc_info())
                res = None
                break

            queueOut.put(res)

        except:
            print("calc: Exception raised:" , sys.exc_info())
            break

def write(queue, song_handle,artist_handle,album_handle):
    while True:
        try:
            res = queue.get(timeout=2)
            if res is not None:
                if len(res)==2:
                    song_handle.write(res[0].encode('utf8')+'\n')
                    album_handle.write(res[1].encode('utf8')+'\n')
                else:
                    artist_handle.write(res.encode('utf8')+'\n')

                fhandle.flush()
        except:
            print("write: Exception raised:" , sys.exc_info())
            break



#item_list = list(zip(item_data['item_id'],item_data['item_type'],item_data['artist'],item_data['song']))

def process(row):
    item_id,item_type,artist,song = row
    if item_type==2:

        if item_id in songs_complete:
            return None

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

            # album_id = albums_complete.get(album_key)
            # if not album_id:
            #     album_mbid = album.get_mbid()
            #     album_date = album.get_release_date()
            #     album_tags = album.get_top_tags()
            #     if album_tags:
            #         album_tagdata = u'|'.join([u"{}:{}".format(t.item.name,t.weight) for t in album_tags])
            #     else:
            #         album_tagdata = None
            #     album_wiki = album.get_wiki_content()
            #     if album_wiki:
            #         album_wiki = album_wiki.replace('\n','\\n')
            #     album_id_idx += 1
            #     album_id = album_id_idx
            #     albums_complete[album_key] = album_id_idx

            #     album_result = u'\t'.join(map(lambda x: x if x else u'', [str(album_id), album_artist, album_title, album_mbid, album_date, album_tagdata, album_wiki]))
        else:
            album_key = None
        #else:
        #    album_id = -999


        song_result = '\t'.join(map(lambda x: x if x else u'', [str(item_id), artist, song, trk_correction, str(trk_duration), trk_mbid, trk_tagdata, trk_wiki]))
        return song_result,album_key

    elif item_type == 0:

        if item_id in artists_complete:
            return None

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
        return artist_result

if __name__ == '__main__':
    nthreads = 4
    batch_size=1000
    batch_start=0

    # [['item_id','item_type','artist','song']]
    item_list = list(zip(item_data['item_id'],item_data['item_type'],item_data['artist'],item_data['song']))

    #with codecs.open(datadir+'songs','a','utf-8') as songs, codecs.open(datadir+'artists','a','utf-8') as artists, codecs.open(datadir+'albums','a','utf-8') as albums:
    with open(datadir+'songs','a') as songs, open(datadir+'artists','a') as artists, open(datadir+'albums','a') as albums:


        while True:
            clist = item_list[batch_start:batch_start+batch_size]
            if len(clist) == 0:
                break
            clist.append(None)

            print("*** BATCH of %d AT %d" % (batch_size, batch_start))

            workerQueue = Queue()
            writerQueue = Queue()
            feedProc = Process(target = feed , args = (workerQueue, clist))
            calcProc = [Process(target = calc, args = (workerQueue, writerQueue)) for i in range(nthreads)]
            writProc = Process(target = write, args = (writerQueue, songs,artists,albums))


            feedProc.start()
            for p in calcProc:
                p.start()
            writProc.start()

            feedProc.join()
            for p in calcProc:
                p.join()

            writProc.join()


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






