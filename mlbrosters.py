from bs4 import BeautifulSoup
from urllib import request

BASE_URL = 'http://mlb.com/team/roster_active.jsp'


def get(team):
    """Return the players and their numbers for a given MLB roster.

    team: string of MLB team (i.e. 'nyy' or 'chc' or 'was')

    Returns a tuple of two lists (pitchers, position_players). Each list
    contains tuples of a player's number and his name (i.e. (u'34', u'Bryce
    Harper')."""

    f = request.urlopen('%s?c_id=%s' % (BASE_URL, team))
    soup = BeautifulSoup(f.read(), 'html.parser')

    bodies = soup.findAll('table', {'class': 'data roster_table'})

    # There should be 4 tbody sets. The first is pitchers.
    pitchers = build_players(bodies[0], False)
    position_players = build_players(bodies[1:])

    return pitchers, position_players


def build_players(bodies, posplayers=True):
    rows = BeautifulSoup(str(bodies), 'html.parser').findAll('tr')

    players = []
    for row in rows[1:]:
        if row.td:
            n = row.td.string
            name = row.find('td', class_='dg-name_display_first_last').a.string
            bats, throws = row.find('td',
                                    class_='dg-bats_throws').string.split('/')
            players.append((n, name, bats if posplayers else throws))

    return sorted(players, key=lambda p: parse_num(p[0]))


def parse_num(num):
    if num:
        try:
            return int(num)
        except ValueError:
            print('VALUE ERROR', num)
            return '28'
    return 100


if __name__ == '__main__':
    for code in ['chc', 'la']:
        pitchers, position_players = get(code)
        for p in pitchers + position_players:
            print(p)
        print('\n')
