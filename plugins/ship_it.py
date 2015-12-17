import random
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ShipItPlugin(WillPlugin):

    SHIPIT_IMAGES = [
        "http://images.cheezburger.com/completestore/2011/11/2/aa83c0c4-2123-4bd3-8097-966c9461b30c.jpg",
        "http://images.cheezburger.com/completestore/2011/11/2/46e81db3-bead-4e2e-a157-8edd0339192f.jpg",
        "http://28.media.tumblr.com/tumblr_lybw63nzPp1r5bvcto1_500.jpg",
        "http://i.imgur.com/DPVM1.png",
        "http://d2f8dzk2mhcqts.cloudfront.net/0772_PEW_Roundup/09_Squirrel.jpg",
        "http://www.cybersalt.org/images/funnypictures/s/supersquirrel.jpg",
        "http://www.zmescience.com/wp-content/uploads/2010/09/squirrel.jpg",
        "http://img70.imageshack.us/img70/4853/cutesquirrels27rn9.jpg",
        "http://img70.imageshack.us/img70/9615/cutesquirrels15ac7.jpg",
        "https://dl.dropboxusercontent.com/u/602885/github/sniper-squirrel.jpg",
        "http://1.bp.blogspot.com/_v0neUj-VDa4/TFBEbqFQcII/AAAAAAAAFBU/E8kPNmF1h1E/s640/squirrelbacca-thumb.jpg",
        "https://dl.dropboxusercontent.com/u/602885/github/soldier-squirrel.jpg",
        "https://dl.dropboxusercontent.com/u/602885/github/squirrelmobster.jpeg",
        "https://i.memecaptain.com/gend_images/zyCwXg.jpg",
        "http://i.giphy.com/143vPc6b08locw.gif"
    ]

    NOIDEA_IMAGES = [
        "http://i3.kym-cdn.com/photos/images/original/000/234/137/5c4.jpg",
        "http://i.giphy.com/xDQ3Oql1BN54c.gif",
        "http://lolbook.com/cache/VxLHGgTCbhMK.gif",
    ]

    @hear("ship(ping)? it")
    def shit_ip(self, message):
        self.reply(message, random.choice(self.SHIPIT_IMAGES))

    @hear("no idea what (I|i)( am)? doing")
    def no_idea(self, message):
        self.reply(message, random.choice(self.NOIDEA_IMAGES))
