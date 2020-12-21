#!/usr/bin/env python3

# Dependencies
import os
import re
import spotipy
from youtube_dl import YoutubeDL
from urllib import request as rq
from argparse import ArgumentParser
from spotipy.oauth2 import SpotifyClientCredentials

# Argparser
parser = ArgumentParser(description="Download Spotify playlist the easy way")


class Hades:
    # Spotify app credentials
    __CLIENT_ID = ""
    __CLIENT_SECRET = ""

    def __init__(self, pl_uri):
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.__CLIENT_ID, client_secret=self.__CLIENT_SECRET
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        self.pl_uri = pl_uri

    def get_ydl_opts(self, path):
        return {
            "format": "bestaudio/best",
            "outtmpl": f"./{path}/%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
        }

    def get_playlist_details(self):
        offset = 0
        pl_name = self.sp.playlist(self.pl_uri)["name"]
        pl_items = self.sp.playlist_items(
            self.pl_uri,
            offset=offset,
            fields="items.track.name,items.track.artists.name, total",
            additional_types=["track"],
        )["items"]

        pl_tracks = []
        while len(pl_items) > 0:
            for item in pl_items:
                track_name = item["track"]["name"].replace(" ", "+")
                artist_name = item["track"]["artists"][0]["name"].replace(" ", "+")
                pl_tracks.append(f"{track_name}+{artist_name}".encode("utf8"))

            offset = (offset + len(pl_items),)
            pl_items = self.sp.playlist_items(
                self.pl_uri,
                offset=offset,
                fields="items.track.name,items.track.artists.name, total",
                additional_types=["track"],
            )["items"]

        return {"pl_name": pl_name, "pl_tracks": pl_tracks}

    def create_download_directory(self, dir_name):
        path = f"./{dir_name}"

        if os.path.exists(path):
            return path

        try:
            os.mkdir(path)
            return path
        except OSError:
            print("Creation of the download directory failed")

    def download_tracks(self):
        pl_details = self.get_playlist_details()
        path = self.create_download_directory(pl_details["pl_name"])

        with YoutubeDL(self.get_ydl_opts(path)) as ydl:
            for track in pl_details["pl_tracks"]:
                html = rq.urlopen(
                    f"https://www.youtube.com/results?search_query={track}"
                )
                video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

                if video_ids:
                    url = "https://www.youtube.com/watch?v=" + video_ids[0]
                    ydl.download([url])


if __name__ == "__main__":
    parser.add_argument(
        "playlist_uri", metavar="PL_URI", type=str, help="Spotify playlist uri"
    )

    args = parser.parse_args()
    if args.playlist_uri:
        hades = Hades(args.playlist_uri)
        hades.download_tracks()
    else:
        print("Please provide a playlist uri to download")
