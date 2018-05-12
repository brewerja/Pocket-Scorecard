#!/usr/bin/env python

from collections import namedtuple
from pyx import *

import mlbrosters

Game = namedtuple('Game', ('away_city, away_nick, away_code, '
                           'home_city, home_nick, home_code, '
                           'venue, date'))

# Set default units to pts
unit.set(defaultunit='pt')

# Text Setup
text.set(text.LatexRunner)
text.preamble(r'\usepackage[sfdefault,condensed]{cabin}')
text.preamble(r'\usepackage[T1]{fontenc}')

# Line and Page Setup
lw = unit.topt(style.linewidth.normal.width)
offset = lw / 2

width = unit.topt(8.5 * unit.inch)
height = unit.topt(11.0 * unit.inch)

# Width of batter's square
b = height / 4. / 5


def get_pitcher_panel(roster, team_nickname):
    c = canvas.canvas()

    # Column headings
    c.text(2.25 * b / 2, 3.5 * b + 2 * lw,
           '%s PITCHERS' % team_nickname.upper(),
           [text.halign.center, text.size.footnotesize])
    columns = ['L/R', 'In', 'Out', 'IP', 'H', 'R', 'ER', 'BB', 'K', 'HR']
    for i, col in enumerate(columns):
        c.text(2.25 * b + i * 3 / 8. * b + 3 / 16. * b,
               3.5 * b + 2 * lw,
               col, [text.halign.center, text.size.footnotesize])

    # Roster of pitchers
    c.text(6 * b + 2, 7 * b / 2, roster,
           [text.size.scriptsize, text.parbox(width / 2.)])

    # Insert starting pitcher '1'
    c.text(2.25 * b + 9 / 16. * b,
           3.25 * b, '1',
           [text.halign.center, text.valign.middle, text.size.large])

    # Table border
    c.stroke(path.rect(0, 0, 6 * b, 7 * b / 2))

    # Table horizontal lines
    for i in range(1, 7):
        y = i * b / 2
        c.stroke(path.line(0, y, 6 * b, y))

    # Table vertical lines
    for i in range(10):
        x = 2.25 * b + i * 3 / 8. * b
        c.stroke(path.line(x, 0, x, 3.5 * b))

    # Panel border
    c.stroke(path.rect(offset, 0,
                       width / 2 - offset, height / 4 - offset))
    return c


def get_diamond():
    dashed = style.linestyle(style.linecap.butt, style.dash([4, 8], 0.1))
    d = canvas.canvas()
    d.stroke(path.rect(0, 0, b / 3, b / 3), [style.linewidth.THIN, dashed])
    return d


def get_batter_panel():
    c = canvas.canvas()

    # Outer border
    c.stroke(path.rect(offset, offset,
                       width / 2 - offset, height / 2 - offset))

    # Horizontal batter lines
    for i in range(1, 10):
        c.stroke(path.line(0,         0.50 * height - i * b,
                           width / 2, 0.50 * height - i * b))

    for i in range(1, 18, 2):
        c.stroke(path.line(0,                 0.50 * height - i * b / 2,
                           width / 2 - 6 * b, 0.50 * height - i * b / 2))

    # Vertical inning lines
    for i in range(1, 7):
        c.stroke(path.line(width / 2 - i * b, 0.50 * height,
                           width / 2 - i * b, 0.25 * height - 4 * b))

    # Diamonds and numbers
    diamond = get_diamond()
    for j in range(9):
        for i in range(6):
            c.insert(diamond, [trafo.rotate(45),
                               trafo.translate(width / 2 - (i + 0.5) * b,
                                               height / 2 - 0.7 * b - j * b)])
            c.text(width / 2 + (i - 6) * b + 0.60,
                   height / 2 - j * b - 0.60,
                   '%d' % (j + 1 + 9 * i),
                   [text.halign.boxleft, text.valign.top, text.size.tiny])

    return c


def get_back_panel(game):
    c = canvas.canvas()
    y = height / 4 - 20
    c.text(1 * width / 6, y, get_roster(game.away_code),
           [text.parbox(width / 2.), text.size.scriptsize])
    c.text(2 * width / 6, y, get_roster(game.home_code),
           [text.parbox(width / 2.), text.size.scriptsize])
    return c


def get_roster(team_code, posplayers=True):
    pitchers, pplayers = mlbrosters.get(team_code)
    if posplayers:
        return roster_list(pplayers)
    starters, bullpen = mlbrosters.separate_starters_and_bullpen(pitchers)
    return roster_list(starters) + r'\\ \\' + roster_list(bullpen)


def roster_list(players):
    return r'\noindent' + r'\\'.join(
        map(lambda p: '%s %s %s' % (p[0], p[1], p[2]), players))


def get_front_panel(game):
    c = canvas.canvas()

    # Panel border
    c.stroke(path.rect(offset, 0,
                       width / 2 - offset, height / 4 - offset))
    vsw = 20
    ll = 3 * b

    # Home vs. Away
    x = width / 4. - ll - vsw / 2.
    y = 4 * b
    c.stroke(path.line(x, y, x + ll, y))
    c.text((2 * x + ll) / 2., y + 2,
           '%s %s' % (game.away_city, game.away_nick), [text.halign.center])

    c.text(width / 4., y, 'vs.', [text.halign.center])

    x = x + ll + vsw
    c.stroke(path.line(x, y, x + ll, y))
    c.text((2 * x + ll) / 2., y + 2,
           '%s %s' % (game.home_city, game.home_nick), [text.halign.center])

    # At (@)
    x = width / 4. - ll / 2.
    y = 3.5 * b
    c.stroke(path.line(x, y, x + ll, y))
    c.text(x - 4, y, '@', [text.halign.right])
    c.text((2 * x + ll) / 2., y + 2, game.venue, [text.halign.center])

    # On
    y = 3.0 * b
    c.stroke(path.line(x, y, x + ll, y))
    c.text(x - 4, y, 'on', [text.halign.right])
    c.text((2 * x + ll) / 2., y + 2, game.date, [text.halign.center])

    # Start and Finish
    x = width / 4. - b - vsw / 2.
    y = 2.5 * b
    c.stroke(path.line(x, y, x + b, y))
    c.text(x - 4, y, 'S:', [text.halign.right])

    x = width / 4. + vsw / 2.
    c.stroke(path.line(x, y, x + b, y))
    c.text(x - 4, y, 'F:', [text.halign.right])

    # Linescore
    w = b / 4
    x = width / 4. - 21.5 / 2 * w
    y = 0.75 * b
    c.insert(get_linescore(game), [trafo.translate(x, y)])

    return c


def get_linescore(game):
    c = canvas.canvas()

    w = b / 4
    x, y = 0, 0
    c.stroke(path.rect(x, y, 21.5 * w, b))
    c.stroke(path.line(x, y + b / 2, x + 21.5 * w, y + b / 2))
    c.text(x + 2, y + 3 * b / 4., game.away_nick,
           [text.halign.left, text.valign.middle])
    c.text(x + 2, y + b / 4., game.home_nick,
           [text.halign.left, text.valign.middle])

    x += 4 * w
    for i in range(13):
        x += w
        c.stroke(path.line(x, y, x, y + b))
    for i in range(2):
        x += 1.5 * w
        c.stroke(path.line(x, y, x, y + b))

    # Column headers
    col_style = [text.halign.center, text.size.scriptsize]
    x = 5 * w + w / 2.
    y += b + 2
    for i in range(1, 13):
        c.text(x, y, '%d' % i, col_style)
        x += w

    x += 0.25 * w
    c.text(x, y, 'R', col_style)
    x += 1.5 * w
    c.text(x, y, 'H', col_style)
    x += 1.5 * w
    c.text(x, y, 'E', col_style)

    return c


def get_scorecard(game):
    base = canvas.canvas()

    roster = get_roster(game.away_code, False)
    pp = get_pitcher_panel(roster, game.away_nick)
    base.insert(pp, [trafo.rotate(180), trafo.translate(width, height / 4)])

    roster = get_roster(game.home_code, False)
    pp = get_pitcher_panel(roster, game.home_nick)
    base.insert(pp, [trafo.rotate(180), trafo.translate(width, height / 2)])

    bp = get_batter_panel()
    base.insert(bp)
    base.insert(bp, [trafo.rotate(180), trafo.translate(width, height)])

    base.insert(get_front_panel(game), [trafo.translate(0, height * 0.5)])
    base.insert(get_back_panel(game), [trafo.translate(0, height * 0.75)])

    return base


def write_canvas(canvas, filename):
    page = document.page(canvas, 'scorecard',
                         document.paperformat.Letter, centered=0, margin=0)
    d = document.document([page])
    d.writePSfile(filename)


if __name__ == '__main__':
    game = Game('Los Angeles', 'Dodgers', 'la',
                'Chicago',     'Cubs',    'chc',
                'Wrigley Field', 'October 20, 2017')
    write_canvas(get_scorecard(game), 'output')
