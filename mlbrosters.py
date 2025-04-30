import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast
from urllib import request

from bs4 import BeautifulSoup, Tag

BULLPEN_URL = "https://www.insidethepen.com/bullpen-usage.html"


@dataclass
class Player:
    number: int
    name: str
    bats: str
    throws: str
    mlb_id: str


class Roster:
    def __init__(self) -> None:
        self.pitchers: list[Player] = []
        self.position_players: list[Player] = []
        self.starters: list[Player] = []
        self.bullpen: list[Player] = []

    def get_pitchers(self) -> str:
        if self.starters and self.bullpen:
            return self._format(self.starters) + r"\\ \\" + self._format(self.bullpen)
        return self._format(self.pitchers)

    def get_position_players(self) -> str:
        return self._format(self.position_players, bats=True)

    def _format(self, players: list[Player], bats: bool = False) -> str:
        return r"\noindent" + r"\\".join(
            map(
                lambda p: "%s %s %s" % (p.number, p.name, p.bats if bats else p.throws),
                players,
            )
        )


@lru_cache(maxsize=2)
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
    separate_starters_and_bullpen(roster)
    return roster


def build_players(bodies: list[Tag]) -> list[Player]:
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
            name = link.get_text(strip=True)
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


def separate_starters_and_bullpen(roster: Roster) -> None:
    bullpen_ids = get_bullpen_ids()
    roster.bullpen = [p for p in roster.pitchers if p.mlb_id in bullpen_ids]
    roster.starters = [p for p in roster.pitchers if p.mlb_id not in bullpen_ids]


def get_bullpen_ids() -> set[str]:
    f = request.urlopen(BULLPEN_URL)
    soup = BeautifulSoup(f.read(), "html.parser")
    links = cast(list[Tag], soup.find_all("a", class_="usage-link"))

    bullpen_ids = set()
    for link in links:
        href = str(link.get("href", ""))
        match = re.search(r"-(\d+)\.html$", href)
        if match:
            bullpen_ids.add(match.group(1))
    return bullpen_ids


if __name__ == "__main__":
    for code in ["nationals"]:
        roster = get_roster(code)
        for p in roster.starters:
            print(p)
        print("\n")
        for p in roster.bullpen:
            print(p)
        print("\n")
        for p in roster.position_players:
            print(p)
