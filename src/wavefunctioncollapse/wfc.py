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

import abc
from enum import auto, Enum
from typing import List, Set

import numpy as np


class Neig(Enum):
    """Possible directions for a neighbour."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


# The opposite direction of a neighbour.
OPPOSITE_NEIG = {
    Neig.UP: Neig.DOWN,
    Neig.DOWN: Neig.UP,
    Neig.LEFT: Neig.RIGHT,
    Neig.RIGHT: Neig.LEFT
}

# The change in indices per neighbour.
DELTA_IND = {
    Neig.UP: (-1, 0),
    Neig.DOWN: (1, 0),
    Neig.LEFT: (0, -1),
    Neig.RIGHT: (0, 1)
}


class Tile():
    """Prototype for a tile in the wave function collapse algorithm."""

    def __init__(self, name, visual,
                 neig_up, neig_dn, neig_lt, neig_rt) -> None:
        """Create a tile.

        Args:
            name (str): The name of the tile.
            visual (str): The visual representation of the tile. (For output in the console.)
            neig_up (List[str]): The ids of the tiles that can be above this tile.
            neig_dn (List[str]): The ids of the tiles that can be below this tile.
            neig_lt (List[str]): The ids of the tiles that can be left of this tile.
            neig_rt (List[str]): The ids of the tiles that can be right of this tile.
        """
        self.name = name
        self.visual = visual
        self.neighs = {
            Neig.UP: neig_up,
            Neig.DOWN: neig_dn,
            Neig.LEFT: neig_lt,
            Neig.RIGHT: neig_rt
        }

    def __eq__(self, __value) -> bool:
        return self.id == __value.id

    @abc.abstractmethod
    def __hash__(self) -> int:
        return self.id

    @property
    def id(self) -> int:
        raise NotImplementedError


class WaveFuctionCollapse():
    """The wave function collapse algorithm."""

    def __init__(self, tiles, size):
        self.tiles = tiles
        self.tiles_by_id = {tile.id: tile for tile in self.tiles}
        self._verify_tileset()
        self.size = size
        self.grid = [[
            None for i in range(size[0])]
            for j in range(size[1])]
        self.possible_tiles: List[List[Set[int]]] = [[
            {tile.id for tile in tiles} for i in range(size[0])]
            for _ in range(size[1])]
        self.propagated = [[False for i in range(size[0])]
                           for _ in range(size[1])]

    def _verify_tileset(self):
        """Verify that the tileset is valid.

        i.e. that all tiles neighours must also have this tile as a neighbour."""
        for tile in self.tiles:
            for neig in Neig:
                for other_tile in tile.neighs[neig]:
                    if tile.id not in self.tiles_by_id[other_tile
                                                       ].neighs[OPPOSITE_NEIG[neig]]:
                        raise ValueError(
                            f"Invalid tileset: {tile.id} not in " +
                            f"{self.tiles_by_id[other_tile].neighs[OPPOSITE_NEIG[neig]]}" +
                            f" of {other_tile}")

    def __str__(self) -> str:
        """Return the current state of the grid as a multi-line string."""
        out = ''
        for row in self.grid:
            for tile in row:
                if tile is None:
                    out += '?'
                else:
                    out += self.tiles_by_id[tile].visual
            out += '\n'
        return out

    def _get_entropies(self):
        """Return the entropies through the grid.

        This is not a true entropy, but rather the number of possible tiles for each cell.
        It will be np.inf if the cell is fixed.
        """
        entropies = []
        for ix, row in enumerate(self.possible_tiles):
            new_row = []
            for iy, tileset in enumerate(row):
                if self.grid[ix][iy] is None:
                    new_row.append(len(tileset))
                else:
                    new_row.append(np.inf)
            entropies.append(new_row)
        return entropies

    def _is_done(self):
        """Return whether all cells are fixed."""
        return all(
            all(len(tileset) == np.inf for tileset in row)
            for row in self.possible_tiles)

    def _propagate(self, ind):
        """Propagate the constraints imposed by this fixed tile or its potential tiles
        to its neighbours."""
        if self.propagated[ind[0]][ind[1]]:
            return
        for neig in Neig:
            delta_ind = DELTA_IND[neig]
            ind_neig = tuple(np.add(ind, delta_ind))
            # print(ind_neig)
            if (ind_neig[0] < 0 or ind_neig[0] >= self.size[1] or
                    ind_neig[1] < 0 or ind_neig[1] >= self.size[0]):
                # this neighbour is outside the grid
                continue
            self.possible_tiles[ind_neig[0]][ind_neig[1]] &= \
                self._get_possible_tiles_for_neig(ind, neig)
            self.propagated[ind[0]][ind[1]] = True
            self._propagate(ind_neig)

    def _get_possible_tiles_for_neig(self, ind, neig):
        """What tiles could be placed at the neighbour in direction neig of the tile at ind?"""
        own_tile = self.grid[ind[0]][ind[1]]
        possible_tiles = set()
        if own_tile is None:
            # multiple possible tiles
            for pt in self.possible_tiles[ind[0]][ind[1]]:
                possible_tiles |= set(self.tiles_by_id[pt].neighs[neig])
        else:
            possible_tiles = set(self.tiles_by_id[own_tile].neighs[neig])
        # delta_ind = DELTA_IND[neig]
        # ind_neig = tuple(np.add(ind, delta_ind))
        # print(f"Possible tiles for {ind_neig} in direction {neig} based on {ind}:")
        # print('>' + ','.join([tile_id for tile_id in possible_tiles]) + '<')
        return possible_tiles

    def generate(self):
        """Generate a grid using the wave function collapse algorithm."""
        i = 0
        i_max = self.size[0] * self.size[1]
        while not self._is_done():
            entropies = np.array(self._get_entropies())
            # print(entropies)

            min_entropy = np.min(entropies)
            if min_entropy == np.inf:
                break
            print(min_entropy)
            if min_entropy == 0:
                raise RuntimeError("Entropy is 0")

            potential_positions = np.argwhere(entropies == min_entropy)
            # print(potential_positions)
            ind = potential_positions[np.random.randint(
                len(potential_positions))]
            print(ind)

            tileset = self.possible_tiles[ind[0]][ind[1]]
            print(','.join(list(tileset)))
            tile_id = np.random.choice(list(tileset))
            print(tile_id)

            self.grid[ind[0]][ind[1]] = tile_id
            self.possible_tiles[ind[0]][ind[1]] = set([tile_id])
            self._propagate(ind)
            self.propagated = [[False for i in range(self.size[0])]
                               for _ in range(self.size[1])]
            print(str(self) + '\n')

            i += 1
            if i > i_max:
                raise RuntimeError(f"Max iterations reached ({i_max})")
        return self.grid
