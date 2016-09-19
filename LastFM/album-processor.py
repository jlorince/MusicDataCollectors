import pylast
import pandas as pd
from urllib import quote_plus,unquote_plus
import os
import codecs
from urllib import unquote_plus
import multiprocessing as mp


API_KEY,API_SECRET = open('lastfm.apikey').readlines()
outfile = 'data/lastfm_top_similar_artists_new'
datadir = 'P:/Projects/BigMusic/jared.rawdata/item_data/'

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


names_albums = ['new_album_id','artist','album','mbid','release_data','tags','wiki']
albums_complete = {}
line = None
if os.path.exists(datadir+'albums'):
    for line in open(datadir+'albums','r'):
        line.split('\t',3)[:3]
        albums_complete['\t'.join([line[1:3]])] = int(line[0])
if line:
    album_id_idx = int(line[0])
else:
    album_id_idx = 0




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
