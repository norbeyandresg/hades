#!/usr/bin/env python3
import os
from argparse import ArgumentParser

from pyfiglet import figlet_format
from PyInquirer import Separator, prompt

from hades import Hades, download_base_path
from validators import PlaylistURIValidator

# Argparser
parser = ArgumentParser(description="Download Spotify playlist the easy way")


class HadesUI:
    def __init__(self, pl_uri=None):
        self.hades = Hades()

        if pl_uri:
            self.hades.download_tracks(pl_uri)
        else:
            self.reset_screen()
            self.main_menu()

    def reset_screen(self):
        os.system("clear")
        print(figlet_format("HADES", font="isometric1"))

    def main_menu(self):
        menu = [
            {
                "type": "list",
                "name": "action",
                "message": "Spotify downloader manager",
                "choices": [
                    {"name": "Download from uri/url", "value": "download_playlist"},
                    {"name": "Manage my playlists", "value": "manage_playlists"},
                    {"name": "Quit", "value": "quit"},
                    Separator(),
                    {
                        "name": "Current download path",
                        "disabled": f"{download_base_path}",
                    },
                    {
                        "name": "You can change the download path changing",
                        "disabled": "hades.py > download_base_path",
                    },
                ],
            },
        ]
        answer = prompt(menu)
        action = getattr(self, answer["action"])
        action()

    def quit(self):
        pass

    def download_playlist(self):
        input = [
            {
                "type": "input",
                "name": "pl_uri",
                "message": "Playlist uri or url to download:",
                "default": "back",
                "validate": PlaylistURIValidator,
            }
        ]
        response = prompt(input)["pl_uri"]
        if response == "back":
            self.reset_screen()
            self.main_menu()
        else:
            self.hades.download_tracks(response)

        confirm = [
            {
                "type": "confirm",
                "message": "Download complete. Continue downloading?",
                "name": "continue",
                "default": True,
            }
        ]
        response = prompt(confirm)["continue"]
        if response:
            self.reset_screen()
            self.main_menu()
        else:
            self.quit()

    def manage_playlists(self):
        playlists = self.hades.get_user_playlists()
        menu = [
            {
                "type": "checkbox",
                "name": "response",
                "message": "Select playlist to download",
                "choices": playlists,
            }
        ]
        selected_playlists = prompt(menu)["response"]

        for pl in selected_playlists:
            self.hades.download_tracks(pl)


if __name__ == "__main__":
    parser.add_argument(
        "--pl_uri", metavar="playlist_uri", type=str, help="Spotify playlist uri"
    )
    HadesUI(parser.parse_args().pl_uri)
