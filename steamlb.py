import requests
from bs4 import BeautifulSoup
import typing


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
