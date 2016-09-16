import pylast
import pandas as pd
from urllib import quote_plus,unquote_plus


API_KEY,API_SECRET = open('../lastfm.apikey').readlines()
outfile = 'data/lastfm_top_similar_artists_new'

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

item_data = pd.read_table('P:/Projects/BigMusic/jared.rawdata/lastfm_itemlist.txt',header=None,names=['item_id','item_type','artist','artist_id','album','song','item_url','top_tag','total_scrobbles','unique_listeners'])

item_data = item_data[item_data['item_type']==2][['artist','song']]

