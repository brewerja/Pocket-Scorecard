from BeautifulSoup import BeautifulSoup
import urllib

BASE_URL = 'http://mlb.com/team/roster_active.jsp'


def get(team):
    """Return the players and their numbers for a given MLB roster.

    team: string of MLB team (i.e. 'nyy' or 'chc' or 'was')

    Returns a tuple of two lists (pitchers, position_players). Each list
    contains tuples of a player's number and his name (i.e. (u'34', u'Bryce
    Harper')."""

    f = urllib.urlopen('%s?c_id=%s' % (BASE_URL, team))
    soup = BeautifulSoup(f.read())

    table = soup.find('table', {'class': 'team_table_results'})
    bodies = table.findAll('tbody')

    # There should be 4 tbody sets. The first is pitchers.
    pitchers = build_players(bodies[0], 'throws')
    position_players = build_players(bodies[1:], 'bats')

    return pitchers, position_players


def build_players(bodies, handed):
    body = BeautifulSoup(str(bodies)).findAll('tr')
    rows = [map(str, row.findAll("td")) for row in body]
    players = []
    for row in rows:
        n = BeautifulSoup(row[0]).find('td').string
        if r'&#042;' in row[1]:  # Catch an asterisk.
            continue
        name = BeautifulSoup(row[1]).find('a').string
        bats, throws = BeautifulSoup(row[2]).find('td').string.split('-')
        if handed == 'bats':
            players.append((n, name, bats))
        else:
            players.append((n, name, throws))

    return sorted(players, key=lambda p: parse_num(p[0]))


def parse_num(num):
    if num:
        return int(num)
    return 100


if __name__ == '__main__':
    pitchers, position_players = get('cin')
    print pitchers
    print position_players
