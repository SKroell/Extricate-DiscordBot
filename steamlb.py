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
    'A1': 3659870, 'A2': 3660015, 'A3': 3660017, 'A4': 3660018, 'A5': 3660026, 'A6': 3660028, 'A7': 3660027,
    'A8': 3660761, 'A9': 3660762, 'A10': 3660763,  # Section A
    'B1': 3660024, 'B2': 3660765, 'B3': 3660766, 'B4': 3660769, 'B5': 3660770, 'B6': 3660771, 'B7': 3660772,
    'B8': 3660773, 'B9': 3660775, 'B10': 3660776,  # Section B
    'C1': 3660777, 'C2': 3660778, 'C3': 3660780, 'C4': 3660781, 'C5': 3660782, 'C6': 3660783, 'C7': 3660784,
    'C8': 3660786, 'C9': 3660787, 'C10': 3660788,  # Section C
    'D1': 3660789, 'D2': 3660791, 'D3': 3660793, 'D4': 3660794, 'D5': 3660796, 'D6': 3660800, 'D7': 3660801,
    'D8': 3660805, 'D9': 3660808, 'D10': 3660812,  # Section D
    'E1': 3660813, 'E2': 3660814, 'E3': 3660831, 'E4': 3660832, 'E5': 3660833, 'E6': 3660836, 'E7': 3660841,
    'E8': 3660845, 'E9': 3660846, 'E10': 3659658,  # Section E
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

# WR
wr_count = {}


def convert_to_nicetime(time):
    seconds = time * 0.001
    minutes = int(seconds / 60)
    seconds_rest = seconds % 60
    return '{:02}:{:06.3f}'.format(minutes, seconds_rest)


# Get times for specific leaderboard
def get_leaderboard_times(lb):
    player_times = {}
    leaderboard_id = leaderboards[lb]

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


def get_leaderboard_wr():
    return wr_count


# Calculates scores for all players
# Scores are calculated with sqrt(n)/sqrt(k/10)
# Where n is the amount of entries and k is the rank
def calculate_leaderboard_scores():
    player_scores = {}
    leaderboard_ids = leaderboards

    print("Getting leaderboard scores...")

    # Loop trough the leaderboard
    for lbid in leaderboard_ids.values():
        lb = steam_lb.get(lbid=lbid)

        # Skip if leaderboard contains no entries
        if lb is None:
            continue

        # Calculate score for player
        for score in lb.entries:
            # lb_score = math.sqrt(len(lb.entries)) / math.sqrt(score.rank / 10)
            lb_score = 1000 * math.pow(0.98, score.rank - 1)
            current_score = player_scores.get(score.steam_id, 0)
            player_scores[score.steam_id] = current_score + lb_score

            # Save WR holder
            if score.rank <= 1:
                if score.steam_id in wr_count:
                    wr_count[score.steam_id] = wr_count[score.steam_id] + 1
                else:
                    wr_count[score.steam_id] = 1

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
