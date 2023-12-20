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

import pytest

from wavefunctioncollapse.wfc import Tile, WaveFuctionCollapse


class MockTile(Tile):
    @property
    def id(self):
        return self.name
    
    def __hash__(self) -> int:
        return hash(self.id)

@pytest.fixture()
def tileset_valid():
    """A simple valid tileset."""
    return [
        MockTile('a', 'a', ['b'], ['b'], ['b'], ['b']),
        MockTile('b', 'b', ['a'], ['a'], ['a'], ['a'])
    ]

@pytest.fixture()
def tileset_invalid():
    """A simple invalid tileset."""
    return [
        MockTile('a', 'a', ['b'], ['b'], ['b'], ['b']),
        MockTile('b', 'b', [], ['a'], ['a'], ['a'])
    ]

def test_tileset_valid(tileset_valid):
    """Test a valid tileset."""
    wfc = WaveFuctionCollapse(tileset_valid, (2, 2))
    wfc.generate()

def test_tileset_invalid(tileset_invalid):
    """Test an invalid tileset."""
    with pytest.raises(ValueError):
        wfc = WaveFuctionCollapse(tileset_invalid, (2, 2))
        wfc.generate()
    
def test_generation(tileset_valid):
    """Test if the generation works."""
    wfc = WaveFuctionCollapse(tileset_valid, (2, 2))
    grid = wfc.generate()

    # Check size.
    assert len(grid) == 2
    assert len(grid[0]) == 2
    assert len(grid[1]) == 2

    # There are only two options how this grid can look like.
    if grid[0][0] == 'a':
        assert grid[0][1] == 'b'
        assert grid[1][0] == 'b'
        assert grid[1][1] == 'a'
        assert str(wfc) == 'ab\nba\n'
    else:
        assert grid[0][1] == 'a'
        assert grid[1][0] == 'a'
        assert grid[1][1] == 'b'
        assert str(wfc) == 'ba\nab\n'