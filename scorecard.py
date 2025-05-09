#!/usr/bin/env python

from typing import NamedTuple

from pyx import canvas, document, path, style, text, trafo, unit  # type: ignore

import mlbrosters


class Game(NamedTuple):
    away_city: str | None = None
    away_nick: str | None = None
    home_city: str | None = None
    home_nick: str | None = None
    venue: str | None = None
    date: str | None = None
    away_code: str | None = None
    home_code: str | None = None


# Set default units to pts
unit.set(defaultunit="pt")

# Text Setup
text.set(text.LatexRunner, texenc="utf8")
text.preamble(r"\usepackage[utf8]{inputenc}")
text.preamble(r"\usepackage[T1]{fontenc}")
text.preamble(r"\usepackage[sfdefault,condensed]{cabin}")

# Line and Page Setup
lw = unit.topt(style.linewidth.normal.width)
offset = lw / 2

width = unit.topt(8.5 * unit.inch)
height = unit.topt(11.0 * unit.inch)

# Width of batter's square
b = height / 4.0 / 5


def get_pitcher_panel(team_nick: str | None, roster: str | None) -> canvas:
    c = canvas.canvas()

    # Column headings
    c.text(
        2.25 * b / 2,
        3.5 * b + 2 * lw,
        " ".join(filter(None, (team_nick, "PITCHERS"))).upper(),
        [text.halign.center, text.size.footnotesize],
    )
    columns = ["L/R", "In", "Out", "IP", "H", "R", "ER", "BB", "K", "HR"]
    for i, col in enumerate(columns):
        c.text(
            2.25 * b + i * 3 / 8.0 * b + 3 / 16.0 * b,
            3.5 * b + 2 * lw,
            col,
            [text.halign.center, text.size.footnotesize],
        )

    # Roster of pitchers
    if roster:
        c.text(
            6 * b + 2,
            7 * b / 2,
            roster,
            [text.size.scriptsize, text.parbox(width / 2.0)],
        )

    # Insert starting pitcher '1'
    c.text(
        2.25 * b + 9 / 16.0 * b,
        3.25 * b,
        "1",
        [text.halign.center, text.valign.middle, text.size.large],
    )

    # Table border
    c.stroke(path.rect(0, 0, 6 * b, 7 * b / 2))

    # Table horizontal lines
    for i in range(1, 7):
        y = i * b / 2
        c.stroke(path.line(0, y, 6 * b, y))

    # Table vertical lines
    for i in range(10):
        x = 2.25 * b + i * 3 / 8.0 * b
        c.stroke(path.line(x, 0, x, 3.5 * b))

    # Panel border
    c.stroke(path.rect(offset, 0, width / 2 - offset, height / 4 - offset))
    return c


def get_diamond() -> canvas:
    dashed = style.linestyle(style.linecap.butt, style.dash([4, 8], 0.1))
    c = canvas.canvas()
    c.stroke(path.rect(0, 0, b / 3, b / 3), [style.linewidth.THIN, dashed])
    return c


def get_batter_panel(team_nick: str | None) -> canvas:
    c = canvas.canvas()

    # Outer border
    c.stroke(path.rect(offset, offset, width / 2 - offset, height / 2 - offset))

    # Horizontal batter lines
    for i in range(1, 10):
        c.stroke(path.line(0, 0.50 * height - i * b, width / 2, 0.50 * height - i * b))

    for i in range(1, 18, 2):
        c.stroke(
            path.line(
                0,
                0.50 * height - i * b / 2,
                width / 2 - 6 * b,
                0.50 * height - i * b / 2,
            )
        )

    # Vertical inning lines
    for i in range(1, 7):
        c.stroke(
            path.line(
                width / 2 - i * b,
                0.50 * height,
                width / 2 - i * b,
                0.25 * height - 4 * b,
            )
        )

    # Diamonds and numbers
    diamond = get_diamond()
    for j in range(9):
        for i in range(6):
            c.insert(
                diamond,
                [
                    trafo.rotate(45),
                    trafo.translate(
                        width / 2 - (i + 0.5) * b, height / 2 - 0.7 * b - j * b
                    ),
                ],
            )
            c.text(
                width / 2 + (i - 6) * b + 0.60,
                height / 2 - j * b - 0.60,
                "%d" % (j + 1 + 9 * i),
                [text.halign.boxleft, text.valign.top, text.size.tiny],
            )

    if team_nick:
        c.text(
            width / 2 - offset,
            height / 2 - 9 * b - offset,
            team_nick,
            [text.halign.boxright, text.valign.top, text.size.scriptsize],
        )

    return c


def get_back_panel(roster_away: str | None, roster_home: str | None) -> canvas:
    c = canvas.canvas()
    y = height / 4 - 20
    if roster_away:
        c.text(
            1 * width / 6,
            y,
            roster_away,
            [text.parbox(width / 2.0), text.size.scriptsize],
        )
    if roster_home:
        c.text(
            2 * width / 6,
            y,
            roster_home,
            [text.parbox(width / 2.0), text.size.scriptsize],
        )
    return c


def get_position_players(team_code: str) -> str:
    return mlbrosters.get_roster(team_code).get_position_players()


def get_pitchers(team_code: str) -> str:
    return mlbrosters.get_roster(team_code).get_pitchers()


def get_front_panel(game: Game) -> canvas:
    c = canvas.canvas()

    # Panel border
    c.stroke(path.rect(offset, 0, width / 2 - offset, height / 4 - offset))
    vsw = 20
    ll = 3 * b

    # Home vs. Away
    x = width / 4.0 - ll - vsw / 2.0
    y = 4 * b
    c.stroke(path.line(x, y, x + ll, y))
    if game.away_city or game.away_nick:
        away_name = " ".join(filter(None, (game.away_city, game.away_nick)))
        c.text(
            (2 * x + ll) / 2.0,
            y + 2,
            away_name,
            [text.halign.center],
        )

    c.text(width / 4.0, y, "vs.", [text.halign.center])

    x = x + ll + vsw
    c.stroke(path.line(x, y, x + ll, y))
    if game.home_city or game.home_nick:
        home_name = " ".join(filter(None, (game.home_city, game.home_nick)))
        c.text(
            (2 * x + ll) / 2.0,
            y + 2,
            home_name,
            [text.halign.center],
        )

    # At (@)
    x = width / 4.0 - ll / 2.0
    y = 3.5 * b
    c.stroke(path.line(x, y, x + ll, y))
    c.text(x - 4, y, "@", [text.halign.right])
    if game.venue:
        c.text((2 * x + ll) / 2.0, y + 2, game.venue, [text.halign.center])

    # On
    y = 3.0 * b
    c.stroke(path.line(x, y, x + ll, y))
    c.text(x - 4, y, "on", [text.halign.right])
    if game.date:
        c.text((2 * x + ll) / 2.0, y + 2, game.date, [text.halign.center])

    # Start and Finish
    x = width / 4.0 - b - vsw / 2.0
    y = 2.5 * b
    c.stroke(path.line(x, y, x + b, y))
    c.text(x - 4, y, "S:", [text.halign.right])

    x = width / 4.0 + vsw / 2.0
    c.stroke(path.line(x, y, x + b, y))
    c.text(x - 4, y, "F:", [text.halign.right])

    # Linescore
    w = b / 4
    x = width / 4.0 - 21.5 / 2 * w
    y = 0.75 * b
    c.insert(get_linescore(game), [trafo.translate(x, y)])

    return c


def get_linescore(game: Game) -> canvas:
    c = canvas.canvas()

    w = b / 4
    x, y = 0, 0
    c.stroke(path.rect(x, y, 21.5 * w, b))
    c.stroke(path.line(x, y + b / 2, x + 21.5 * w, y + b / 2))
    c.text(
        x + 2,
        y + 3 * b / 4.0,
        game.away_nick,
        [text.halign.left, text.valign.middle, text.size.footnotesize],
    )
    c.text(
        x + 2,
        y + b / 4.0,
        game.home_nick,
        [text.halign.left, text.valign.middle, text.size.footnotesize],
    )

    x += 4 * w
    for i in range(13):
        x += w
        c.stroke(path.line(x, y, x, y + b))
    for i in range(2):
        x += 1.5 * w
        c.stroke(path.line(x, y, x, y + b))

    # Column headers
    col_style = [text.halign.center, text.size.scriptsize]
    x = 5 * w + w / 2.0
    y += b + 2
    for i in range(1, 13):
        c.text(x, y, "%d" % i, col_style)
        x += w

    x += 0.25 * w
    c.text(x, y, "R", col_style)
    x += 1.5 * w
    c.text(x, y, "H", col_style)
    x += 1.5 * w
    c.text(x, y, "E", col_style)

    return c


def get_scorecard(game: Game) -> canvas:
    base = canvas.canvas()

    roster_away = get_pitchers(game.away_code) if game.away_code else None
    pp = get_pitcher_panel(game.away_nick, roster_away)
    base.insert(pp, [trafo.rotate(180), trafo.translate(width, height / 4)])

    roster_home = get_pitchers(game.home_code) if game.home_code else None
    pp = get_pitcher_panel(game.home_nick, roster_home)
    base.insert(pp, [trafo.rotate(180), trafo.translate(width, height / 2)])

    base.insert(get_batter_panel(game.away_nick))
    base.insert(
        get_batter_panel(game.home_nick),
        [trafo.rotate(180), trafo.translate(width, height)],
    )

    base.insert(get_front_panel(game), [trafo.translate(0, height * 0.5)])

    roster_away = get_position_players(game.away_code) if game.away_code else None
    roster_home = get_position_players(game.home_code) if game.home_code else None
    base.insert(
        get_back_panel(roster_away, roster_home),
        [trafo.translate(0, height * 0.75)],
    )

    return base


def write_canvas(canvas: canvas, filename: str) -> None:
    page = document.page(
        canvas, "scorecard", document.paperformat.Letter, centered=0, margin=0
    )
    d = document.document([page])
    d.writePSfile(filename)


if __name__ == "__main__":
    game = Game(
        away_city="New York",
        away_nick="Mets",
        home_city="Washington",
        home_nick="Nationals",
        venue="Nationals Park",
        date="April 28, 2025",
        away_code="mets",
        home_code="nationals",
    )
    write_canvas(get_scorecard(game), "output")
