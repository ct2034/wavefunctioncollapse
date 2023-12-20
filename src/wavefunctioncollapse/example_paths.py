#!/usr/bin/env python3

# wavefunctioncollapse
# Copyright (C) 2023 Christian Henkel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from .wfc import Tile, WaveFuctionCollapse

sys.setrecursionlimit(16385)


class ConsoleTile(Tile):
    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self.name


def main():
    tiles = [
        ConsoleTile(
            '+', '┼',
            neig_dn=['+', '|', 'J', 'L'],
            neig_up=['+', '|', 'r', '7'],
            neig_lt=['+', '-', 'r', 'L'],
            neig_rt=['+', '-', '7', 'J']
        ),
        ConsoleTile(
            '-', '─',
            neig_dn=[' '],
            neig_up=[' '],
            neig_lt=['+', '-', 'r', 'L'],
            neig_rt=['+', '-', '7', 'J']
        ),
        ConsoleTile(
            '|', '│',
            neig_dn=['+', '|', 'J', 'L'],
            neig_up=['+', '|', 'r', '7'],
            neig_lt=[' '],
            neig_rt=[' ']
        ),
        ConsoleTile(
            ' ', ' ',
            neig_dn=[' ', '-', 'r', '7'],
            neig_up=[' ', '-', 'J', 'L'],
            neig_lt=[' ', '|', 'J', '7'],
            neig_rt=[' ', '|', 'r', 'L']
        ),
        ConsoleTile(
            'r', '┌',
            neig_dn=['|', 'J', '+', 'L'],
            neig_up=[' '],
            neig_lt=[' '],
            neig_rt=['-', 'J', '+', '7'],
        ),
        ConsoleTile(
            '7', '┐',
            neig_dn=['|', 'J', '+', 'L'],
            neig_up=[' '],
            neig_lt=['-', 'r', '+', 'L'],
            neig_rt=[' '],
        ),
        ConsoleTile(
            'J', '┘',
            neig_dn=[' '],
            neig_up=['|', 'r', '+', '7'],
            neig_lt=['-', 'r', '+', 'L'],
            neig_rt=[' '],
        ),
        ConsoleTile(
            'L', '└',
            neig_dn=[' '],
            neig_up=['|', 'r', '+', '7'],
            neig_lt=[' '],
            neig_rt=['-', '7', '+', 'J'],
        ),
    ]

    wfc = WaveFuctionCollapse(tiles, (30, 10))
    wfc.generate()

    print("\n\n")
    print("done")
    print(str(wfc))


if __name__ == '__main__':
    main()
