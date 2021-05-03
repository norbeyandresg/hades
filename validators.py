#!/usr/bin/env python3

import regex
from prompt_toolkit.validation import ValidationError, Validator


class PlaylistURIValidator(Validator):
    def validate(self, document):
        if document.text == "back":
            return "back"
        ok = regex.match("^(spotify:playlist:)([a-zA-Z0-9]+)(.*)$", document.text)
        if not ok:
            raise ValidationError(
                message="Please provide a valid playlist uri (example: 'spotify:playlist:<id>')",
                cursor_position=len(document.text),  # move cursor to end
            )
