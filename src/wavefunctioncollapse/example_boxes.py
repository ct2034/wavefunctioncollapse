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

from .wfc import WaveFuctionCollapse, Tile


class ConsoleTile(Tile):
    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self.name


def main():
    tiles = [
        ConsoleTile('k', '⚫',
                    neig_dn=['k', 'u'],
                    neig_up=['k', 'd'],
                    neig_lt=['k', 'r'],
                    neig_rt=['k', 'l']),

        ConsoleTile('w', '⚪',
                    neig_dn=['w', 'd'],
                    neig_up=['w', 'u'],
                    neig_lt=['w', 'l'],
                    neig_rt=['w', 'r']),

        ConsoleTile('d', '⏬',
                    neig_dn=['k'],
                    neig_up=['w'],
                    neig_lt=['d', 'c'],
                    neig_rt=['d', 'c']),

        ConsoleTile('u', '⏫',
                    neig_dn=['w'],
                    neig_up=['k'],
                    neig_lt=['u', 'c'],
                    neig_rt=['u', 'c']),

        ConsoleTile('l', '⏪',
                    neig_dn=['l', 'c'],
                    neig_up=['l', 'c'],
                    neig_lt=['k'],
                    neig_rt=['w']),

        ConsoleTile('r', '⏩',
                    neig_dn=['r', 'c'],
                    neig_up=['r', 'c'],
                    neig_lt=['w'],
                    neig_rt=['k']),

        ConsoleTile('c', '💠',  # corner
                    neig_dn=['l', 'r'],
                    neig_up=['l', 'r'],
                    neig_lt=['u', 'd'],
                    neig_rt=['u', 'd']),
    ]

    wfc = WaveFuctionCollapse(tiles, (15, 15))
    wfc.generate()

    print("done")
    print(str(wfc))


if __name__ == '__main__':
    main()
