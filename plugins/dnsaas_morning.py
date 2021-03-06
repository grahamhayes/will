import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class GreatingPlugin(WillPlugin):

    @hear("^(good )?(morn?)\b")
    @hear("^(good )?(morning?)\b")
    def morning(self, message):
        self.say("mornin', %s" % message.sender.nick, message=message)

    @hear("^(good ?|g')?('?night)\b")
    def good_night(self, message):
        now = datetime.datetime.now()
        if now.weekday() == 4:  # Friday
            self.say("have a good weekend!", message=message)
        else:
            self.say("have a good night!", message=message)
