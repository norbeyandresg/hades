# Hades 
 This script takes a Spotify playlist, list and search each track on youtube and
 download it to the specified path with the script root path as parent
 
## Installing
To use **Hades** you need to create an App on the [Spotify Developers Dashboard](https://developer.spotify.com/dashboard/applications) and setup your `CLIENT_ID` and `CLIENT_SECRET` as environment variables to connect to the Spotify API. In order to list and download your own playlists you also need to setup your `USER_ID` in your environment variables.


``` shell
pip install -r requirements.txt
```

## Usage
Just go to your playlist, click on share and copy the Playlist URI. 
To use the shell interface run

``` shell
python hades_ui.py
```


you can also pass your `playlist_uri` as a param

``` shell
python hades_ui.py --pl_uri [playlist_uri]
```
