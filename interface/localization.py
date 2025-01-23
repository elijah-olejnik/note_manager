import gettext


class LocalisationManager:
    def __init__(self):
        self.lang = gettext

    def set_locale(self, lang_code):
        self.lang = gettext.translation('messages', localedir='locales', languages=[lang_code])
        self.lang.install()

    def gettext(self, msg):
        return self.lang.gettext(msg)


loc_mgr = LocalisationManager()
def _(message):
    return loc_mgr.gettext(message)
