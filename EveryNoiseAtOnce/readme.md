# scrape_eno.py

Scrapes all data from from [Every Noise at Once](http://everynoise.com/engenremap.html).

Description from that page: 
> This is an ongoing attempt at an algorithmically-generated, readability-adjusted scatter-plot of the musical genre-space, based on data tracked and analyzed for 1387 genres by The Echo Nest. The calibration is fuzzy, but in general down is more organic, up is more mechanical and electric; left is denser and more atmospheric, right is spikier and bouncier.

This simple script collects the full list of genres as recorded there, plus the artists associated with each genre, and writes everything to a pandas-friendly TSV. We treat the font sizes of each artist as association weights between artists and genres.

Currently this ignores all location-based information of genres/artists. 

Example output:

    genre	artist	weight
    a cappella	Rockapella	0.00894614421184
    a cappella	Tonic Sol-Fa	0.00888650325043
    a cappella	Straight No Chaser	0.00882686228902
    a cappella	The Bobs	0.00876722132761
    a cappella	Naturally 7	0.00876722132761
    ...
    zydeco	Tom Rigney	0.0036443148688
    zydeco	The Mudbugs Cajun & Zydeco Band	0.0036443148688
    zydeco	Luderin Darbone & The Hackberry Ramblers	0.0036443148688
    zydeco	The Rosinators	0.0036443148688
    zydeco	Lil' Band o' Gold	0.0036443148688
