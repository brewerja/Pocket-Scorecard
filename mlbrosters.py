from dataclasses import dataclass
from urllib import request
from bs4 import BeautifulSoup, Tag, ResultSet, PageElement, NavigableString
from typing import cast, Optional

# NEED TO UPDATE BULLPEN_URL
BULLPEN_URL = "http://www.baseballpress.com/bullpen-usage"
# https://www.insidethepen.com/bullpen-usage.html
# https://www.fangraphs.com/roster-resource/depth-charts/blue-jays


@dataclass
class Player:
    number: int
    name: str
    bats: str
    throws: str
    mlb_id: str


class Roster:
    def __init__(self):
        self.pitchers = []
        self.position_players = []


def get_roster(team: str) -> Roster:
    """Return the players and their numbers for a given MLB roster.

    team: string of MLB team (i.e. 'yankees' or 'cubs' or 'nationals')

    Returns a Roster object with two lists of players: pitchers and position players.
    """

    f = request.urlopen(f"https://www.mlb.com/{team}/roster")
    soup = BeautifulSoup(f.read(), "html.parser")

    # There should be 4 tbody sets. The first is pitchers.
    bodies = cast(list[Tag], soup.find_all("table", {"class": "roster__table"}))
    roster = Roster()
    roster.pitchers = build_players(bodies[0:1])
    roster.position_players = build_players(bodies[1:])
    return roster


def build_players(bodies: list[Tag], posplayers: bool = True) -> list[Player]:
    rows = cast(list[Tag], BeautifulSoup(str(bodies), "html.parser").find_all("tr"))

    players = []
    for row in rows[1:]:
        if row.td:
            info_td = row.find("td", class_="info")
            if not info_td or not isinstance(info_td, Tag):
                continue

            jersey_span = info_td.find("span", class_="jersey")
            if not jersey_span or not isinstance(jersey_span, Tag):
                continue
            n = parse_num(jersey_span.get_text(strip=True))

            link = info_td.find("a")
            if not link or not isinstance(link, Tag):
                continue
            name = link.get_text(strip=True)  # Use get_text() instead of .string
            href = link.get("href")
            if not href or not isinstance(href, str):
                continue
            mlb_id = href.split("/")[-1]

            bat_throw_td = row.find("td", class_="bat-throw")
            if not bat_throw_td or not isinstance(bat_throw_td, Tag):
                continue

            bats, throws = bat_throw_td.get_text(strip=True).split("/")
            players.append(Player(n, name, bats, throws, mlb_id))

    return sorted(players, key=lambda p: p.number)


def parse_num(num: str) -> int:
    if num:
        try:
            return int(num)
        except ValueError:
            print("VALUE ERROR", num)
            return 66
    return 100


def get_bullpen_ids():
    f = request.urlopen(BULLPEN_URL)
    soup = BeautifulSoup(f.read(), "html.parser")
    div = soup.find_all("div", {"class": "bullpen-usage"})
    bullpen_ids = set()
    names = []
    for d in div:
        rows = d.table.find_all("tr")
        for r in rows:
            cols = r.find_all("td")
            for c in cols:
                if c.a:
                    bullpen_ids.add(c.a["data-mlb"])
                    names.append(c.a.contents[0])
    return bullpen_ids


def separate_starters_and_bullpen(pitchers):
    bullpen_ids = get_bullpen_ids()
    bullpen = [p for p in pitchers if p[3] in bullpen_ids]
    starters = [p for p in pitchers if p[3] not in bullpen_ids]
    return starters, bullpen


if __name__ == "__main__":
    for code in ["nationals"]:
        roster = get_roster(code)
        # starters, bullpen = separate_starters_and_bullpen(pitchers)
        for p in roster.pitchers:
            print(p)
        print("\n")
        # for p in bullpen:
        # print(p)
        print("\n")
        for p in roster.position_players:
            print(p)
