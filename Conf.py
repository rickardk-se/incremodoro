import yaml


class Configuration:
    def __init__(self, filename):
        self.read_conf(filename)

    def read_conf(self, filename):
        with open(filename, "r") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
        self.conf = dict(
            deck_id=conf["deck_id"],
            deck_title=conf["deck_title"],
            back_template=conf["back_template"],
            back_cloze_template=conf["back_cloze_template"],
            css_file=conf["css_file"],
            # cover_path=conf["cover_path"],
            fields=conf["fields"],
            filename=conf["filename"],
            front_template=conf["front_template"],
            front_cloze_template=conf["front_cloze_template"],
            model_id=conf["model_id"],
            model_id_cloze=conf["model_id_cloze"],
            model_name=conf["model_name"],
            model_name_cloze=conf["model_name_cloze"],
            media_dir=conf["media_dir"],
        )
        self.read_templates()

    def read_templates(self):
        with open(self.conf["front_template"]) as f:
            front = f.read()
            self.conf.pop("front_template")

        with open(self.conf["back_template"]) as f:
            back = f.read()
            self.conf.pop("back_template")

        self.conf["template"] = [{"name": "Card 1", "qfmt": front, "afmt": back}]

        with open(self.conf["front_cloze_template"]) as f:
            front_cloze = f.read()
            self.conf.pop("front_cloze_template")

        with open(self.conf["back_cloze_template"]) as f:
            back_cloze = f.read()
            self.conf.pop("back_cloze_template")

        self.conf["template_cloze"] = [
            {"name": "Cloze ", "qfmt": front_cloze, "afmt": back_cloze}
        ]
        with open(self.conf["css_file"]) as f:
            self.conf["css"] = f.read()
            self.conf.pop("css_file")
