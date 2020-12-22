# Hades 
 This script takes a Spotify playlist, list and search each track on youtube and
 download it to the specified path with the script root path as parent
 
## Installing
To use **Hades** you need to create an App on the [Spotify Developers Dashboard](https://developer.spotify.com/dashboard/applications) and setup your `CLIENT_ID` and `CLIENT_SECRET` on the `hades.py` file to connect to the Spotify API.


``` shell
pip install -r requirements.txt
```

## Usage
Just go to your playlist, click on share and copy the Playlist URI.

``` shell
python hades.py [OPTIONS] 'your_playlist_uri'
```

## Options
	-e or --embed                   Download and embed youtube thumbnails into mp3                                   


