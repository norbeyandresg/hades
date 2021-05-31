#!/usr/bin/env python3

import regex
from prompt_toolkit.validation import ValidationError, Validator


class PlaylistURIValidator(Validator):
    def validate(self, document):
        if document.text == "back":
            return "back"
        uriCheck = regex.match("^(spotify:playlist:)([a-zA-Z0-9]+)(.*)$", document.text)
        urlCheck = regex.match("^(https:\/\/open.spotify.com\/playlist\/)([a-zA-Z0-9]+)(.*)$", document.text)
        if not (uriCheck or urlCheck):
            raise ValidationError(
                message="Please provide a valid playlist uri (example: 'spotify:playlist:<id>' or 'https://open.spotify.com/playlist/<id>)",
                cursor_position=len(document.text),  # move cursor to end
            )
