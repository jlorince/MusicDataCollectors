import urllib2 as ul
from bs4 import BeautifulSoup
import codecs
import pandas as pd

root = "http://everynoise.com/engenremap.html"

html = ul.urlopen(root).read()
soup = BeautifulSoup(html)

genres = soup.find_all("div",{'class':"genre scanme"})

### Example:
"""
<div class="genre scanme" id="item1" onclick='playx("5Btx4IjlpIjemwHLsnOLFJ", "a cappella", this);' scan="true" style="color: #749806; top: 2967px; left: 637px; font-size: 101%" title="e.g. Straight No Chaser &quot;I'm Yours / Somewhere Over The Rainbow&quot;">a cappella<a class="navlink" href="engenremap-acappella.html" onclick="event.stopPropagation();">»</a> </div>
"""

with codecs.open('eno_data.tsv','w','utf8') as outfile:
    for genre in genres:

        url = genre.find('a').get('href')
        genre_name = genre.getText()[:-2] # ignore the little ">>" link symbol

        # get full URL so we can download artist list for the genre
        full_url = "http://everynoise.com/"+url

        # load artist list page
        html = ul.urlopen(full_url).read()
        soup = BeautifulSoup(html)

        artists = soup.find_all('div',{'class':'genre scanme'})
        for artist in artists:
            artist_name = artist.getText()[:-2]

            # we want to extract the font size attribute, which we'll assume
            #represents relative importance of artist in the current genre
            style_text = artist.get('style')
            fontsize= style_text[style_text.find('font-size'):].split()[1][:-1]

            output = [genre_name,artist_name,fontsize]
            print output
            outfile.write('\t'.join(output)+'\n')

# load our data into pandas, convert font sizes to weights, sort, and save final data
data = pd.read_table('eno_data.tsv',header=None,names=['genre','artist','raw_weight'])
data['weight'] = data.groupby('genre').apply(lambda grp: grp['raw_weight']/grp['raw_weight'].sum()).values
data = data.drop('raw_weight',axis=1)
data.sort(['genre','weight'],ascending=[True,False]).to_csv('eno_data_clean.tsv',sep='\t',index=False)








