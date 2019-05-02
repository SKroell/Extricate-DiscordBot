import requests
from bs4 import BeautifulSoup
import typing
import discord
import datetime
import math
import os

icon_url = "https://cdn.discordapp.com/avatars/542096662894608405/c2dbfde314c1f2a12da25ea489a0e98c.webp"
steam_url = "https://store.steampowered.com/app/1012970/Extricate/"

# Leaderboard Stuff
leaderboards = {
    'A1': 3236666, 'A2': 3236720, 'A3': 3236721, 'A4': 3236723, 'A5': 3236724, 'A6': 3236725, 'A7': 3236726, 'A8': 3236727, 'A9': 3236728, 'A10': 3236729, # Section A
    'B1': 3236730, 'B2': 3236731, 'B3': 3236732, 'B4': 3236733, 'B5': 3236734, 'B6': 3236735, 'B7': 3236736, 'B8': 3236737, 'B9': 3236738, 'B10': 3236739,  # Section B
    'C1': 3236741, 'C2': 3236742, 'C3': 3236743, 'C4': 3236744, 'C5': 3236745, 'C6': 3236746, 'C7': 3236747, 'C8': 3236748, 'C9': 3236749, 'C10': 3236750,  # Section C
    'D1': 3236751, 'D2': 3236752, 'D3': 3236753, 'D4': 3236754, 'D5': 3236756, 'D6': 3236757, 'D7': 3236758, 'D8': 3236759, 'D9': 3236760, 'D10': 3236761,  # Section D
    'E1': 3236762, 'E2': 3236763, 'E3': 3236764, 'E4': 3236765, 'E5': 3236766, 'E6': 3236767, 'E7': 3236768, 'E8': 3236769, 'E9': 3236770, 'E10': 3236771,  # Section E
}

leaderboards_exp = {
    'A1_EXP': 3272402, 'A2_EXP': 3272403, 'A3_EXP': 3272404, 'A4_EXP': 3272405, 'A5_EXP': 3272406, 'A6_EXP': 3272407, 'A7_EXP': 3272408, 'A8_EXP': 3272409, 'A9_EXP': 3272410, 'A10_EXP': 3272412,  # Section A EXP
    'B1_EXP': 3272414, 'B2_EXP': 3272416, 'B3_EXP': 3272417, 'B4_EXP': 3272418, 'B5_EXP': 3272419, 'B6_EXP': 3272420, 'B7_EXP': 3272421, 'B8_EXP': 3272422, 'B9_EXP': 3272424, 'B10_EXP': 3272425,  # Section B EXP
    'C1_EXP': 3272427, 'C2_EXP': 3272428, 'C3_EXP': 3272429, 'C4_EXP': 3272430, 'C5_EXP': 3272431, 'C6_EXP': 3272432, 'C7_EXP': 3272433, 'C8_EXP': 3272435, 'C9_EXP': 3272436, 'C10_EXP': 3272437,  # Section C EXP
    'D1_EXP': 3272439, 'D2_EXP': 3272440, 'D3_EXP': 3272441, 'D4_EXP': 3272442, 'D5_EXP': 3272443, 'D6_EXP': 3272444, 'D7_EXP': 3272445, 'D8_EXP': 3272446, 'D9_EXP': 3272447, 'D10_EXP': 3272448,  # Section D EXP
    'E1_EXP': 3272449, 'E2_EXP': 3272450, 'E3_EXP': 3272452, 'E4_EXP': 3272453, 'E5_EXP': 3272454, 'E6_EXP': 3272455, 'E7_EXP': 3272456, 'E8_EXP': 3272457, 'E9_EXP': 3272458, 'E10_EXP': 3272459,  # Section E EXP
}

# Discord emotes instead of numbers
lb_index = [
    ":trophy:",
    ":second_place:",
    ":third_place:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
    ":keycap_ten:",
]


def convert_to_nicetime(time):
    seconds = time * 0.001
    minutes = int(seconds / 60)
    seconds_rest = seconds % 60
    return '{:02}:{:06.3f}'.format(minutes, seconds_rest)


# Get times for specific leaderboard
def get_leaderboard_times(lb, exp=False):
    player_times = {}
    leaderboard_id = leaderboards_exp[lb] if exp else leaderboards[lb]

    print("Getting leaderboard scores for " + lb + "...")

    lb = steam_lb.get(lbid=leaderboard_id)

    # Skip if leaderboard contains no entries
    if lb is None:
        return

    # Calculate score for player
    for entry in lb.entries:
        player_times[entry.steam_id] = entry.score

    # Return playerscores
    return player_times


# Calculates scores for all players
# Scores are calculated with sqrt(n)/sqrt(k/10)
# Where n is the amount of entries and k is the rank
def calculate_leaderboard_scores(exp):
    player_scores = {}
    leaderboard_ids = leaderboards_exp if exp else leaderboards

    print("Getting leaderboard scores...")

    # Loop trough the leaderboard
    for lbid in leaderboard_ids.values():
        lb = steam_lb.get(lbid=lbid)

        # Skip if leaderboard contains no entries
        if lb is None:
            continue

        # Calculate score for player
        for score in lb.entries:
            lb_score = math.sqrt(len(lb.entries)) / math.sqrt(score.rank / 10)
            current_score = player_scores.get(score.steam_id, 0)
            player_scores[score.steam_id] = current_score + lb_score

    # Return playerscores
    return player_scores


def sort_entries(entries, high_first=True):
    entries = [(v, k) for k, v in entries.items()]
    entries.sort()
    if high_first:
        entries.reverse()  # Highest first
    return [(k, v) for v, k in entries]


def create_lb_embed(msg, title):
    now = datetime.datetime.now()
    embed = discord.Embed(title=title, description=msg, color=0xd30106)
    embed.set_author(name="Extricate Game", url=steam_url, icon_url=icon_url)
    embed.set_footer(text="Updated: " + now.strftime("%Y-%m-%d %H:%M") + "(UTC)")
    return embed


# Get steam username from SteamID
def get_username(steam_api_key, steam_id=None):
    request = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/" \
        f"?key={steam_api_key}" \
        f"&steamids={steam_id}" \
        f"&format=xml"

    xml = requests.get(request)
    _bs = BeautifulSoup(xml.content, features="lxml")
    return _bs.find("personaname").text


class SteamLeaderboard:
    def __init__(self, app_id, steam_api_key):
        self.leaderboards = []
        self.app_id = app_id
        self.steam_api_key = steam_api_key

    def get(self, *, lbid=None) -> typing.Optional["Leaderboard"]:

        # Find using id
        if lbid is not None:

            # Leaderboards ids has to be of type int
            if not isinstance(lbid, int):
                raise ValueError("lbid must be an int")

            return Leaderboard(self.app_id, lbid=lbid, steam_api_key=self.steam_api_key)

        return None


class Leaderboard:
    def __init__(self, app_id=None, lbid=None, *, steam_api_key=None):
        if app_id and lbid:
            self.lbid = lbid
            self.app_id = app_id
            self.name = None
            self.display_name = None
            self.entries = None
            self.steam_api_key = steam_api_key
        else:
            raise ValueError("No app_id or lbid specified")

        next_request_url = f"https://partner.steam-api.com/ISteamLeaderboards/GetLeaderboardEntries/v1/" \
            f"?key={self.steam_api_key}" \
            f"&appid={self.app_id}" \
            f"&leaderboardid={self.lbid}&rangestart=0&rangeend=100&datarequest=RequestGlobal&format=xml"

        self.entries = []
        while next_request_url:
            xml = requests.get(next_request_url)
            _bs = BeautifulSoup(xml.content, features="lxml")
            for entry in _bs.find_all("entry"):
                self.entries.append(Entry(entry))
            next_request_url = None


# Leaderboard entry
class Entry:
    def __init__(self, soup):
        self.steam_id = soup.steamid.text
        self.score = int(soup.score.text)
        self.rank = int(soup.rank.text)
        self.ugcid = soup.ugcid.text

    def __repr__(self):
        return f"<Entry #{self.rank} {self.steam_id}: {self.score} pts>"


steam_lb = SteamLeaderboard(1012970, os.environ['steam_api_key'])
