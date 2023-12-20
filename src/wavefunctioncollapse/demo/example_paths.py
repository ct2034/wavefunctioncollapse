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
import time

from wavefunctioncollapse.wfc import Tile, WaveFuctionCollapse, Neig

import cv2
import numpy as np
import PIL.Image
from PIL import ImageFont, ImageDraw

sys.setrecursionlimit(16385)


class ConsoleTile(Tile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.res = 60
        self._graphics = None

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self.name
    
    def graphics(self, seed=None):
        if self._graphics is None:
            self.cache_graphics(seed)
        return self._graphics

    def cache_graphics(self, seed):
        np.random.seed(seed)
        # print("graphics for", self.name)

        # based on image, create a clear image, that we want
        connectors = {n: False for n in Neig}  # where to draw connectors
        if self.name == '+':
            connectors = {n: True for n in Neig}
        elif self.name == '-':
            connectors[Neig.LEFT] = True
            connectors[Neig.RIGHT] = True
        elif self.name == '|':
            connectors[Neig.UP] = True
            connectors[Neig.DOWN] = True
        elif self.name == 'r':
            connectors[Neig.DOWN] = True
            connectors[Neig.RIGHT] = True
        elif self.name == '7':
            connectors[Neig.DOWN] = True
            connectors[Neig.LEFT] = True
        elif self.name == 'J':
            connectors[Neig.UP] = True
            connectors[Neig.LEFT] = True
        elif self.name == 'L':
            connectors[Neig.UP] = True
            connectors[Neig.RIGHT] = True

        # print("connectors", connectors)
        
        # draw our tile
        img = PIL.Image.new('1', (self.res, self.res), 0)
        draw = ImageDraw.Draw(img)
        mid = self.res // 2
        rand_mid = (
            mid + np.random.normal(0, self.res // 16.),
            mid + np.random.normal(0, self.res // 16.)
        )
        width = self.res // 20

        if any(connectors.values()):
            draw.ellipse(
                [rand_mid[0] - width//2, 
                rand_mid[1] - width//2, 
                rand_mid[0] + width//2, 
                rand_mid[1] + width//2], 
                fill=1)
        for n in Neig:
            if connectors[n]:
                if n == Neig.UP:
                    end_bit = (mid, 0)
                elif n == Neig.DOWN:
                    end_bit = (mid, self.res)
                elif n == Neig.LEFT:
                    end_bit = (0, mid)
                elif n == Neig.RIGHT:
                    end_bit = (self.res, mid)
                draw.line([end_bit, rand_mid], fill=1, width=width, joint='curve')
                draw.ellipse(
                    [end_bit[0] - width//2, 
                     end_bit[1] - width//2, 
                     end_bit[0] + width//2, 
                     end_bit[1] + width//2], 
                    fill=1)
        self._graphics = img
                
    @property
    def graphics_size(self):
        return self.res


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
            neig_dn=[' ', '-', 'r', '7'],
            neig_up=[' ', '-', 'J', 'L'],
            neig_lt=['+', '-', 'r', 'L'],
            neig_rt=['+', '-', '7', 'J']
        ),
        ConsoleTile(
            '|', '│',
            neig_dn=['+', '|', 'J', 'L'],
            neig_up=['+', '|', 'r', '7'],
            neig_lt=[' ', '|', 'J', '7'],
            neig_rt=[' ', '|', 'r', 'L']
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
            neig_up=[' ', '-', 'J', 'L'],
            neig_lt=[' ', '|', 'J', '7'],
            neig_rt=['-', 'J', '+', '7'],
        ),
        ConsoleTile(
            '7', '┐',
            neig_dn=['|', 'J', '+', 'L'],
            neig_up=[' ', '-', 'J', 'L'],
            neig_lt=['-', 'r', '+', 'L'],
            neig_rt=[' ', '|', 'r', 'L'],
        ),
        ConsoleTile(
            'J', '┘',
            neig_dn=[' ', '-', 'r', '7'],
            neig_up=['|', 'r', '+', '7'],
            neig_lt=['-', 'r', '+', 'L'],
            neig_rt=[' ', '|', 'r', 'L'],
        ),
        ConsoleTile(
            'L', '└',
            neig_dn=[' ', '-', 'r', '7'],
            neig_up=['|', 'r', '+', '7'],
            neig_lt=[' ', '|', 'J', '7'],
            neig_rt=['-', '7', '+', 'J'],
        ),
    ]

    wfc = WaveFuctionCollapse(tiles, (32, 18))

    cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('image',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    def progress_callback(wfc, _, __):
        image = wfc.graphics()
        cv2.imshow("image", np.array(image))
        time.sleep(0.1)
        cv2.waitKey(1)

    wfc.generate(progress_callback)
    cv2.waitKey(0)

    print("\n\n")
    print("done")
    print(str(wfc))



if __name__ == '__main__':
    main()
