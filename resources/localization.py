import gettext


class LocalisationManager:
    def __init__(self):
        gettext.bindtextdomain('note_manager', 'locales')
        gettext.textdomain('note_manager')
        self.lang = gettext

    def set_locale(self, lang_code):
        self.lang = gettext.translation('messages', localedir='locales', languages=[lang_code])
        self.lang.install()

    def gettext(self, msg):
        return self.lang.gettext(msg)


language_manager = LocalisationManager()
def _(message):
    return language_manager.gettext(message)
