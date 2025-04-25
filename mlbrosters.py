from bs4 import BeautifulSoup
from urllib import request

BASE_URL = "http://mlb.com/team/roster_active.jsp"
BULLPEN_URL = "http://www.baseballpress.com/bullpen-usage"


def get(team):
    """Return the players and their numbers for a given MLB roster.

    team: string of MLB team (i.e. 'nyy' or 'chc' or 'was')

    Returns a tuple of two lists (pitchers, position_players). Each list
    contains tuples of a player's number and his name (i.e. (u'34', u'Bryce
    Harper')."""

    f = request.urlopen("%s?c_id=%s" % (BASE_URL, team))
    soup = BeautifulSoup(f.read(), "html.parser")

    bodies = soup.findAll("table", {"class": "data roster_table"})

    # There should be 4 tbody sets. The first is pitchers.
    pitchers = build_players(bodies[0], False)
    position_players = build_players(bodies[1:])

    return pitchers, position_players


def build_players(bodies, posplayers=True):
    rows = BeautifulSoup(str(bodies), "html.parser").findAll("tr")

    players = []
    for row in rows[1:]:
        if row.td:
            n = row.td.string
            if n == "—":
                n = "66"
            link = row.find("td", class_="dg-name_display_first_last").a
            name = link.string
            mlb_id = link["href"].split("/")[-2]
            bats, throws = row.find("td", class_="dg-bats_throws").string.split("/")
            players.append((n, name, bats if posplayers else throws, mlb_id))

    return sorted(players, key=lambda p: parse_num(p[0]))


def parse_num(num):
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
    div = soup.findAll("div", {"class": "bullpen-usage"})
    bullpen_ids = set()
    names = []
    for d in div:
        rows = d.table.findAll("tr")
        for r in rows:
            cols = r.findAll("td")
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
    for code in ["ari"]:
        pitchers, position_players = get(code)
        starters, bullpen = separate_starters_and_bullpen(pitchers)
        for p in starters:
            print(p)
        print("\n")
        for p in bullpen:
            print(p)
        print("\n")
        for p in position_players:
            print(p)
