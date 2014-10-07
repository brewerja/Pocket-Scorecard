#!/usr/bin/env python


def other():
    ROSTER_FILES = ['away', 'home']
    pitchers, posplayers = {}, {}

    for filename in ROSTER_FILES:
        pitchers[filename] = []
        posplayers[filename] = []
        with open(filename, 'rb') as f:
            for line in f:
                lastfirst = False
                if ',' in line:
                    line = line.replace(',', '')
                    lastfirst = True
                x = line.split()
                n = x[0]
                if lastfirst:
                    name = x[2] + ' ' + x[1]
                else:
                    name = x[1] + ' ' + x[2]
                if len(x) == 5:
                    pos = x[3] + x[4]
                else:
                    pos = x[3]
                #print n, name, pos
                if 'P' in pos:
                    pitchers[filename].append([int(n), name, pos])
                else:
                    posplayers[filename].append([int(n), name, pos])

        pitchers[filename] = sorted(pitchers[filename],   key=lambda p: p[0])
        posplayers[filename] = sorted(posplayers[filename], key=lambda p: p[0])


def print_roster(team, roster_type, name=''):
    out.write('/r_x currentpoint pop def\n')
    out.write('/r_y currentpoint exch pop def\n')
    out.write('(%s) show\n' % name)
    out.write('r_x r_y %s 6 mul sub moveto\n' % (str(1)))
    if roster_type == 'posplayers':
        players = posplayers[team]
    elif roster_type == 'pitchers':
        players = pitchers[team]
    else:
        return
    for i, p in enumerate(players):
        out.write('(%s %s %s) show\n ' % (p[0], p[1], p[2]))
        out.write('r_x r_y %s 6 mul sub moveto\n' % (str(i + 2)))

if __name__ == '__main__':

    from mlbrosters import get
    pitchers = {}
    posplayers = {}
    pitchers['away'], posplayers['away'] = get('cin')
    pitchers['home'], posplayers['home'] = get('was')
    teams_full = {'away': 'Cincinnati Reds', 'home': 'Washington Nationals'}
    teams_nick = {'away': 'REDS', 'home': 'NATIONALS'}  # UPPERCASE

    with open('output.ps', 'w') as out:
        with open('pocket_scorecard.ps', 'r') as lines:
            for line in lines:
                if 'INSERT ROSTER HERE' in line:
                    team = line.strip().split()[-2]
                    roster_type = line.strip().split()[-1]
                    print_roster(team, roster_type)
                elif 'INSERT DIVIDER HERE' in line:
                    out.write('0 height rlineto\n')
                elif 'LABEL BOXES HERE' in line:
                    team = line.strip().split()[-2]
                    out.write('/%s_team_full (%s) def\n' % (team,
                                                            teams_full[team]))
                    out.write('/%s_team_nick (%s) def\n' % (team,
                                                            teams_nick[team]))
                    out.write('/%s_team_opt %s_team_nick def\n' % (team, team))
                else:
                    out.write(line)
