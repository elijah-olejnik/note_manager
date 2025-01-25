import gettext


class LocalisationManager:
    """The class LocalisationManager handles
    localisation using the gettext library
    """
    def __init__(self):
        gettext.bindtextdomain('note_manager', 'locales')
        gettext.textdomain('note_manager')
        self.lang = gettext

    def set_locale(self, lang_code):
        """The function sets locale for strings from a given locale code."""
        self.lang = gettext.translation('messages', localedir='locales', languages=[lang_code])
        self.lang.install()

    def gettext(self, msg):
        """The function wraps gettext() method."""
        return self.lang.gettext(msg)


language_manager = LocalisationManager()
def _(message):
    """The function _ gives a translation for string
    to a chosen language in a LocalisationManager class object.
    """
    return language_manager.gettext(message)
