from flask_babel import get_translations, get_locale


class Translator:

    def __init__(self) -> None:
        if get_locale() != "en":
            cache = get_translations()
            self.trans_to_origin = {value: key for key, value in cache._catalog.items()}
            self.origin_to_trans = get_translations()._catalog
        else:
            self.trans_to_origin = {}
            self.origin_to_trans = {}

    def translate_reverse(self, entry):
        return self.trans_to_origin.get(entry, entry)

    def translate(self, entry):
        return self.origin_to_trans.get(entry, entry)
