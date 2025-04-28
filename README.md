# Pocket-Scorecard by John Brewer

This is a project to create a full featured baseball scorecard that is compact enough to fit in your pocket.

This project uses ideas from two other projects:

1. [PocketMod](https://pocketmod.com/howto)
2. [Reisner Scorekeeping](http://www.reisnerscorekeeping.com/how)

The scorecard will work with a variety of scorekeeping methods, but works best using the Reisner Scorekeeping system.

For printing, ensure that the printer does not scale the file and prints at 100%. The card is oriented so that lines outside the printable area of whatever printer you are using are less important. For best results, take care when folding.

## Requirements

1. Working Tex installation

    See [MacTex installation](https://www.tug.org/mactex/mactex-download.html) (6.0 GB)

    Mac ps2pdf install: `brew install pstoedit`

2. Python 3.11 and uv

## Usage

1. Edit the `__main__` method to set paramaters on the `Game` namedtuple.
2. `uv run scorecard.py`
3. `ps2pdf output.ps`
