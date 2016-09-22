import pylast
import pandas as pd
from urllib import quote_plus,unquote_plus
import os
import codecs
from urllib import unquote_plus
import time


import logging
logger = logging.getLogger('album_processor')
hdlr = logging.FileHandler(os.path.expanduser('~')+'/item_data/log_albums')
formatter = logging.Formatter('%(asctime)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


API_KEY,API_SECRET = open('lastfm.apikey').readlines()
#datadir = 'P:/Projects/BigMusic/jared.rawdata/item_data/'
datadir = os.path.expanduser('~')+'/item_data/'

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

while True:

    input_data = pd.read_table(datadir+'songs',header=None,names=['item_id','artist','song','correction','duration','mbid','album_artist','album_name','tags','wiki'],usecols=['album_artist','album_name'])

    albums = input_data.drop_duplicates().dropna()
    new_album_idx = 0


    names_albums = ['new_album_id','artist','album','mbid','tags','wiki']
    albums_complete = {}
    line = None
    if os.path.exists(datadir+'albums'):
        for line in open(datadir+'albums','r'):
            albums_complete['\t'.join(line.decode('utf8').split('\t',3)[1:3])] = int(line[0])
    if line:
        album_id_idx = int(line.split()[0])
    else:
        album_id_idx = 0

    with open(datadir+'albums','a') as fout:
        for row in albums.itertuples():
            attempts = 0
            while attempts <= 5:
                try:
                    print row
                    album_artist = row.album_artist.decode('utf8')
                    album_name = row.album_name.decode('utf8')
                    if '\t'.join([album_artist,album_name]) in albums_complete:
                        print "COMPLETE - {}".format(row)
                        break
                        #continue

                    album = network.get_album(album_artist,album_name)

                    album_mbid = album.get_mbid()
                    #album_date = album.get_release_date()
                    album_tags = album.get_top_tags()
                    if album_tags:
                        album_tagdata = u'|'.join([u"{}:{}".format(t.item.name,t.weight) for t in album_tags])
                    else:
                        album_tagdata = None
                    album_wiki = album.get_wiki_content()
                    if album_wiki:
                        album_wiki = album_wiki.replace('\n','\\n')
                    album_id_idx +=1
                    album_id = album_id_idx


                    album_result = u'\t'.join(map(lambda x: x if x else u'', [str(album_id), album_artist, album_name, album_mbid, album_tagdata, album_wiki])).encode('utf8')

                    fout.write(album_result+'\n')
                    fout.flush()
                    break
                except Exception as e:
                    print "retrying ({})".format(e)
                    time.sleep(attempts+3)
                    attempts+=1
            if attempts == 6:
                logger.info("{} - {}".format(row,type(e)))



    print "File processed...waiting 5 minutes"
    time.sleep(300)
