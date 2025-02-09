class Rows:
    def __init__(self):
        self.all = []
        self.bookmarks = []
        self.highlights = []
        self.missing_tags = []
        self.empty_highlights = []
        self.no_match = []

    def add_row(self, row):
        hl = len(row.highlight)
        nl = len(row.note)
        self.all.append(row)
        if hl == 1 and not row.note:
            self.bookmarks.append(row)
        elif all((hl, nl)) and not row.tags:
            self.missing_tags.append(row)
        elif all((hl, nl, row.tags)):
            self.highlights.append(row)
        elif hl and not nl:
            self.empty_highlights.append(row)
        else:
            self.no_match.append(row)


class Row:
    __slots__ = (
        "title",
        "chapter",
        "date",
        "b_url",
        "ch_url",
        "h_url",
        "highlight",
        "color",
        "note",
        "tags",
        "image",
        "image_name",
        "isbn",
        "cover",
        "author",
        "number",
        "extra_tags",
    )

    def __init__(
        self,
        title,
        chapter,
        date,
        b_url,
        ch_url,
        h_url,
        highlight,
        color,
        note,
        number,
    ):
        self.title = title
        self.author = "Unknown"
        self.chapter = chapter
        self.date = date
        self.b_url = b_url
        self.ch_url = ch_url.replace(
            "www.safaribooksonline.com", "learning.oreilly.com"
        )
        self.h_url = h_url.replace("www.safaribooksonline.com", "learning.oreilly.com")
        self.highlight = highlight
        if "img:" in note:
            self.image = note.split("img:")[-1]
            self.image_name = self.image.split("/")[-1]
            note = note.split("img:")[0]
        elif "![](" in note:
            self.image = note.split("![](")[-1].strip(")")
            self.image_name = self.image.split("/")[-1].strip(") ")
            note = note.split("![](")[0]
        else:
            self.image = ""
            self.image_name = ""
        if " #" in note:
            self.note = note.split(" #")[0]
            self.tags = note.split(" #")[1].split()
        else:
            self.note = note
            self.tags = []
        self.note = note.split(" #")[0]
        self.isbn = ch_url.split("/")[-2]
        self.cover = "https://learning.oreilly.com/library/cover/" + self.isbn
        self.number = number
        self.extra_tags = [self.isbn]

    def __str__(self):
        return f"{self.note}\t{self.highlight}\t{self.h_url}"


def make_record(row):
    records = []
    notes = row[7].split("||")
    for number, note in enumerate(notes):
        n = "#" + str(number)
        note = note.strip()
        records.append(
            Row(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                n,
            )
        )
    return records
