# Plex Anime Tags
This script is a way to update Plex's genres and Collection tags for Anime, by normalizing tags from anidb.net. The 
script relies on MongoDB for caching (as Anidb is serious on IP banning people) and a few customizable CSVs for mapping and 
normalizing genres.

## How to use
* Install requirements via `pip install -r requirements.txt`
* Rename settings.ini.example to settings.ini
* Update the values within for your Plex url, authentication token, and Anime library.\*
* Run `python main.py`

\* If you have Anime and normal shows mixed in, the script will take much longer to execute. 

The script utilizes heavy rate limiting to ensure no IP ban occurs. This rate cannot be changed, so go grab a bite to eat 
while you wait for this to finish running. Any anime that was not found in Anidb will be written to a log file.  


## Common Issues
* Some anime isn't found but I see it on anidb.net?
    - You may need to fetch the latest data dump [here](http://anidb.net/api/anime-titles.dat.gz) and place into  data/anime-titles.dat.
* Not all tags I want are getting sent to Plex?
    - You either need to lower the min_tag_weight in settings.ini or update the genres.csv to include that as an allowed genre.  


