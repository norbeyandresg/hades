#!/usr/bin/env python3

# Dependencies
import os
import re
from argparse import ArgumentParser
from urllib import request as rq
from urllib.parse import quote

import spotipy
from pyfiglet import figlet_format
from PyInquirer import print_json, prompt
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_dl import YoutubeDL

# Argparser
parser = ArgumentParser(description="Download Spotify playlist the easy way")

# Download path variable
# if you want to change the download path use absolute path
# example: /home/user/music
download_base_path = "./downloads"


class Hades:
    def __init__(self):
        # Envars
        self.__CLIENT_ID = os.environ.get("CLIENT_ID")
        self.__CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
        self.__USER_ID = os.environ.get("USER_ID")

        self.auth_manager = SpotifyClientCredentials(
            client_id=self.__CLIENT_ID, client_secret=self.__CLIENT_SECRET
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_ydl_opts(self, path):
        return {
            "format": "bestaudio/best",
            "outtmpl": f"{path}/%(id)s.%(ext)s",
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
        }

    def get_user_playlists(self):
        return [
            {"value": pl.get("uri"), "name": pl.get("name")}
            for pl in self.sp.user_playlists(self.__USER_ID).get("items")
        ]

    def get_playlist_details(self, pl_uri):
        offset = 0
        pl_name = self.sp.playlist(pl_uri)["name"]
        pl_items = self.sp.playlist_items(
            pl_uri,
            offset=offset,
            fields="items.track.name,items.track.artists.name, total",
            additional_types=["track"],
        )["items"]

        pl_tracks = []
        while len(pl_items) > 0:
            for item in pl_items:
                if item["track"]:
                    track_name = (
                        item["track"]["name"].replace("/", "_").replace('"', " ")
                    )
                    artist_name = (
                        item["track"]["artists"][0]["name"]
                        .replace("/", "_")
                        .replace('"', " ")
                    )
                    pl_tracks.append(
                        {
                            "uri": quote(
                                f'{track_name.replace(" ", "+")}+{artist_name.replace(" ", "+")}'
                            ),
                            "track_name": f"{track_name} - {artist_name}",
                        }
                    )

            offset = offset + len(pl_items)
            pl_items = self.sp.playlist_items(
                pl_uri,
                offset=offset,
                fields="items.track.name,items.track.artists.name, total",
                additional_types=["track"],
            )["items"]

        return {"pl_name": pl_name, "pl_tracks": pl_tracks}

    def create_download_directory(self, dir_name):
        path = f"{download_base_path}/{dir_name}"

        if os.path.exists(path):
            return path

        try:
            os.makedirs(path)
            return path
        except OSError:
            print("Creation of the download directory failed")

    def check_existing_tracks(self, playlist, path):
        existing_tracks = os.listdir(path)
        tracks = [
            track
            for track in playlist["pl_tracks"]
            if f"{track['track_name']}.mp3" not in existing_tracks
        ]
        return tracks

    def download_tracks(self, pl_uri):
        pl_details = self.get_playlist_details(pl_uri)
        path = self.create_download_directory(pl_details["pl_name"])
        tracks = self.check_existing_tracks(pl_details, path)
        print(
            f"\033[1m\033[33m[info] Downloading {len(tracks)} tracks from {pl_details['pl_name']}\033[0m"
        )
        with YoutubeDL(self.get_ydl_opts(path)) as ydl:
            for track in tracks:
                html = rq.urlopen(
                    f"https://www.youtube.com/results?search_query={track['uri']}"
                )
                video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

                if video_ids:
                    url = "https://www.youtube.com/watch?v=" + video_ids[0]
                    metadata = ydl.extract_info(url, download=False)
                    downloaded_track = ydl.download([url])

                    # Update downloaded file name
                    src = f"{path}/{metadata['id']}.mp3"
                    dst = f"{path}/{track['track_name']}.mp3"
                    os.rename(src, dst)
