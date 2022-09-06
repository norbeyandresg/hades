#!/usr/bin/env python3

# Dependencies
import os
import re
from argparse import ArgumentParser
from urllib import request as rq
from urllib.parse import quote

import eyed3
import spotipy
from pyfiglet import figlet_format
from PyInquirer import print_json, prompt
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL

# Load envars
from dotenv import load_dotenv

load_dotenv()


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

    def normalize_str(self, string):
        return string.translate(str.maketrans('\\/:*?"<>|', "__       "))

    def get_playlist_details(self, pl_uri):
        offset = 0
        fields = "items.track.track_number,items.track.name,items.track.artists.name,items.track.album.name,items.track.album.release_date,total,items.track.album.images"
        pl_name = self.sp.playlist(pl_uri)["name"]
        pl_items = self.sp.playlist_items(
            pl_uri,
            offset=offset,
            fields=fields,
            additional_types=["track"],
        )["items"]

        pl_tracks = []
        while len(pl_items) > 0:
            for item in pl_items:
                if item["track"]:
                    track_name = self.normalize_str(item["track"]["name"])
                    artist_name = self.normalize_str(
                        item["track"]["artists"][0]["name"]
                    )
                    pl_tracks.append(
                        {
                            "uri": quote(
                                f'{track_name.replace(" ", "+")}+{artist_name.replace(" ", "+")}'
                            ),
                            "file_name": f"{artist_name} - {track_name}",
                            "track_name": track_name,
                            "artist_name": artist_name,
                            "album_name": self.normalize_str(
                                item["track"]["album"]["name"]
                            ),
                            "album_date": item["track"]["album"]["release_date"],
                            "track_number": item["track"]["track_number"],
                            "album_art": item["track"]["album"]["images"][0]["url"],
                        }
                    )

            offset = offset + len(pl_items)
            pl_items = self.sp.playlist_items(
                pl_uri,
                offset=offset,
                fields=fields,
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
            if f"{track['file_name']}.mp3" not in existing_tracks
        ]
        return tracks

    def add_track_metadata(self, track_id, metadata, path):
        audiofile = eyed3.load(f"{path}/{track_id}.mp3")
        if audiofile.tag == None:
            audiofile.initTag()

        # Add basic tags
        audiofile.tag.title = metadata["track_name"]
        audiofile.tag.album = metadata["album_name"]
        audiofile.tag.artist = metadata["artist_name"]
        audiofile.tag.release_date = metadata["album_date"]
        audiofile.tag.track_num = metadata["track_number"]

        album_art = rq.urlopen(metadata["album_art"]).read()
        audiofile.tag.images.set(3, album_art, "image/jpeg")
        audiofile.tag.save()

        # Update downloaded file name
        src = f"{path}/{track_id}.mp3"
        dst = f"{path}/{metadata['file_name']}.mp3"
        os.rename(src, dst)

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

                    self.add_track_metadata(metadata["id"], track, path)
