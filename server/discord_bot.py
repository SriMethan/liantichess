import logging
import os

import discord
from discord.ext.commands import Bot

#from lobby_broadcast import lobby_broadcast

log = logging.getLogger("discord")
log.setLevel(logging.INFO)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
SERVER_ID = 634298688663191582
PYCHESS_LOBBY_CHANNEL_ID = 653203449927827456
GAME_SEEK_CHANNEL_ID = 823862902648995910
TOURNAMENT_CHANNEL_ID = 861234739820888074
ANNOUNCEMENT_CHANNEL_ID = 865964574507008000

ROLES = {
    "gladiator": 867894147900637215,
    "crazyhouse": 658544490830757919,
    "capablanca": 658544637467951124,
    "grand": 658544867269541899,
    "atomic": 867889563087274034,
    "hoppelpoppel": 867889843357876254,
    "xiangqi": 658544904011644938,
    "shogi": 658544950677340161,
    "shogun": 675143932912599041,
    "seirawan": 658753848982110209,
    "shako": 658544983623860235,
    "janggi": 695975424433455145,
    "makruk": 658545040234119178,
    "sittuyin": 658545093011046420,
    "orda": 702977517018939444,
    "synochess": 730903272080277524,
    "shinobi": 867889352704131132,
    "empire": 867892839493009478,
    "chess": 658545185571209221,
    "chak": 940232991182041098,
    "chennis": 940233624048009236,
}

CATEGORIES = {
    "chess": (
        "chess",
        "chess960",
        "crazyhouse",
        "crazyhouse960",
        "placement",
        "atomic",
        "atomic960",
    ),
    "fairy": (
        "capablanca",
        "capablanca960",
        "capahouse",
        "capahouse960",
        "seirawan",
        "seirawan960",
        "shouse",
        "grand",
        "grandhouse",
        "shako",
        "shogun",
        "hoppelpoppel",
    ),
    "army": ("orda", "synochess", "shinobi", "empire", "ordamirror", "chak", "chennis"),
    "makruk": ("makruk", "makpong", "cambodian", "sittuyin", "asean"),
    "shogi": ("shogi", "minishogi", "kyotoshogi", "dobutsu", "gorogoroplus", "torishogi"),
    "xiangqi": ("xiangqi", "manchu", "janggi", "minixiangqi"),
}

intents = discord.Intents(messages=True, guilds=True, message_content=True)


class DiscordBot(Bot):
    def __init__(self, lobbysockets, *args, **kwargs):
        Bot.__init__(self, *args, **kwargs)

        self.lobbysockets = lobbysockets

        # Get the pychess-lobby channel
        self.pychess_lobby_channel = self.get_channel(PYCHESS_LOBBY_CHANNEL_ID)
        log.debug("pychess_lobby_channel is: %s", self.pychess_lobby_channel)

        self.game_seek_channel = self.get_channel(GAME_SEEK_CHANNEL_ID)
        log.debug("game_seek_channel is: %s", self.game_seek_channel)

        self.tournament_channel = self.get_channel(TOURNAMENT_CHANNEL_ID)
        log.debug("tournament_channel is: %s", self.tournament_channel)

        self.announcement_channel = self.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        log.debug("announcement_channel is: %s", self.announcement_channel)

    async def on_message(self, msg):
        log.debug("---on_message() %s", msg)
        if msg.author.id == self.user.id or msg.channel.id != PYCHESS_LOBBY_CHANNEL_ID:
            log.debug("---self.user msg OR other channel.id -> return")
            return

        if self.lobby_ws is None:
            log.debug("---self.lobby_ws is None -> return")
            return

        log.debug("+++ msg is OK -> send_json()")
        await lobby_broadcast(
            self.lobbysockets,
            {"type": "lobbychat", "user": "", "message": "%s: %s" % (msg.author.name, msg.content)},
        )

    async def send_to_discord(self, msg_type, msg, user=None):
        if msg_type == "lobbychat" and user and user != "Discord-Relay":
            log.debug("+++ lobbychat msg: %s %s", user, msg)
            await self.pychess_lobby_channel.send("**%s**: %s" % (user, msg))

        elif msg_type == "create_seek":
            log.debug("+++ create_seek msg: %s", msg)
            await self.game_seek_channel.send("%s" % msg)

        elif msg_type == "create_tournament":
            log.debug("+++ create_tournament msg: %s", msg)
            await self.tournament_channel.send("%s" % msg)

        elif msg_type == "notify_tournament":
            log.debug("+++ notify_tournament msg: %s", msg)
            await self.announcement_channel.send("%s %s" % (self.get_role_mentions(msg), msg))

    def get_role_mentions(self, message):
        guild = self.get_guild(SERVER_ID)
        gladiator_role = guild.get_role(ROLES["gladiator"])
        log.debug("guild, role, mention: %s %s %s", guild, gladiator_role, gladiator_role.mention)

        variant = message.split()[0].strip("*")

        if variant in CATEGORIES["shogi"]:
            role = guild.get_role(ROLES["shogi"])

        elif variant in CATEGORIES["makruk"]:
            role = guild.get_role(ROLES["makruk"])

        elif variant == "janggi":
            role = guild.get_role(ROLES["janggi"])

        elif variant in CATEGORIES["xiangqi"]:
            role = guild.get_role(ROLES["xiangqi"])

        elif variant == "grand":
            role = guild.get_role(ROLES["grand"])

        elif variant == "shako":
            role = guild.get_role(ROLES["shako"])

        elif variant.startswith("atomic"):
            role = guild.get_role(ROLES["atomic"])

        elif variant.startswith("crazyhouse") or variant in (
            "shouse",
            "capahouse",
            "capahouse960",
            "grandhouse",
        ):
            role = guild.get_role(ROLES["crazyhouse"])

        elif variant.startswith("capablanca"):
            role = guild.get_role(ROLES["capablanca"])

        elif variant.startswith("seirawan"):
            role = guild.get_role(ROLES["seirawan"])

        elif variant == "hoppelpoppel":
            role = guild.get_role(ROLES["hoppelpoppel"])

        elif variant == "shogun":
            role = guild.get_role(ROLES["shogun"])

        elif variant.startswith("orda"):
            role = guild.get_role(ROLES["orda"])

        elif variant == "synochess":
            role = guild.get_role(ROLES["synochess"])

        elif variant == "shinobi":
            role = guild.get_role(ROLES["shinobi"])

        elif variant == "empire":
            role = guild.get_role(ROLES["empire"])

        elif variant == "chak":
            role = guild.get_role(ROLES["chak"])

        elif variant == "chennis":
            role = guild.get_role(ROLES["chennis"])

        else:
            role = guild.get_role(ROLES["chess"])

        return "%s %s" % (gladiator_role.mention, role.mention)
