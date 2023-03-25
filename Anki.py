import hashlib
import os
import re

import genanki
import requests
from cached_property import cached_property


class ModelX(genanki.Model):
    def __init__(
        self, model_id=None, name=None, fields=None, templates=None, css="", type=0
    ):
        super().__init__(model_id, name, fields, templates, css)
        self._type = type

    def to_json(self, now_ts, deck_id):
        j = super().to_json(now_ts, deck_id)
        j["type"] = self._type
        return j


class NoteX(genanki.Note):
    def _cloze_cards(self):
        """
        returns a Card with unique ord for each unique cloze reference
        """
        card_ords = set()
        # find cloze replacements in first template's qfmt, e.g "{{cloze::Text}}"
        cloze_replacements = set(
            re.findall(
                "{{[^}]*?cloze:(?:[^}]?:)*(.+?)}}", self.model.templates[0]["qfmt"]
            )
            + re.findall("<%cloze:(.+?)%>", self.model.templates[0]["qfmt"])
        )
        for field_name in cloze_replacements:
            field_index = next(
                (i for i, f in enumerate(self.model.fields) if f["name"] == field_name),
                -1,
            )
            field_value = self.fields[field_index] if field_index >= 0 else ""
            # update card_ords with each cloze reference N, e.g. "{{cN::...}}"
            card_ords.update(
                [
                    int(m) - 1
                    for m in re.findall(r"{{c(\d+)::.+?}}", field_value)
                    if int(m) > 0
                ]
            )

        if card_ords == {}:
            card_ords = {0}

        return [genanki.Card(ord) for ord in card_ords]

    @cached_property
    def cards(self):
        if self.model._type == 1:
            return self._cloze_cards()
        else:
            return super().cards


class Deck:
    def __init__(
        self,
        media_dir,
        model_id,
        model_id_cloze,
        model_name,
        model_name_cloze,
        fields,
        template,
        template_cloze,
        css,
        filename,
        deck_id,
        deck_title,
    ):
        self.media_dir = media_dir
        self.model_id = model_id
        self.model_name = model_name
        self.model_id_cloze = model_id_cloze
        self.model_name_cloze = model_name_cloze
        self.fields = fields
        self.template = template
        self.template_cloze = template_cloze
        self.css = css
        self.deck = genanki.Deck(deck_id, deck_title)
        self.package = genanki.Package(self.deck)
        self.filename = filename
        self.media_files = set()
        self.model = ModelX(
            model_id=self.model_id,
            name=self.model_name,
            fields=self.fields,
            templates=self.template,
            css=self.css,
        )
        self.model_cloze = ModelX(
            model_id=self.model_id_cloze,
            name=self.model_name_cloze,
            fields=self.fields,
            templates=self.template_cloze,
            css=self.css,
            type=1,
        )

    def add_cards(self, rows):
        for row in rows[::-1]:  # Oldest to newest
            isbn = row.b_url.split("/")[-1]
            hashsum = hashlib.md5(
                row.highlight.encode("utf-8")
                + row.chapter.encode("utf-8")
                + row.number.encode("utf-8")
            ).hexdigest()

            if "&|" in row.note:
                row.highlight = row.note.split("&|")[1].strip()
                row.note = row.note.split("&|")[0].strip()

            if "{{c1::" in row.note:
                model = self.model_cloze
            else:
                model = self.model

            cover = row.cover.split("/")[-1] + ".jpg"
            if row.image:
                image = f"{row.h_url.split('/')[-2]}-{row.image_name}"
            else:
                image = ""

            note = NoteX(
                model=model,
                fields=[
                    row.note,
                    row.highlight,
                    row.title,
                    row.author,
                    row.chapter,
                    row.b_url,
                    row.ch_url,
                    f'<img src="{cover}">',
                    f'<img src="{image}">' if image else "",
                ],
                tags=row.tags + row.extra_tags,
                guid=hashsum,
            )
            self.deck.add_note(note)

        return None

    def download_media(self, rows):
        if not os.path.exists(self.media_dir):
            os.mkdir(self.media_dir)

        for row in rows:
            if row.image:
                file = row.image.split("/")[-1].split(")")[0]
                filename = f"{self.media_dir}{row.h_url.split('/')[-2]}-{file}"
                self.media_files.add(filename)
                if not os.path.exists(filename):
                    r = requests.get(row.image, allow_redirects=True)
                    with open(filename, "wb") as f:
                        f.write(r.content)
            filename = f"{self.media_dir}{row.isbn}.jpg"
            self.media_files.add(filename)
            if not os.path.exists(filename):
                r = requests.get(row.cover, allow_redirects=True)
                with open(filename, "wb") as f:
                    f.write(r.content)
        return None

    def compile_deck(self):
        self.package.media_files = self.media_files
        self.package.write_to_file(self.filename)
