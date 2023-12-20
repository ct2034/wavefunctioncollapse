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
import os
import imageio

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
        self._graphics = {}

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self.name
    
    def graphics(self, seed=None):
        if seed not in self._graphics:
            self._graphics[seed] = self.cache_graphics(seed)
        return self._graphics[seed]

    def cache_graphics(self, seed):
        seed = (seed + hash(self)) % (2**32 - 1)
        rng = np.random.RandomState(seed)
        # print(seed)
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
        oversample = 4
        img = PIL.Image.new('RGB', (self.res * oversample, self.res * oversample), 0)
        draw = ImageDraw.Draw(img)
        mid = self.res // 2 * oversample
        col = (255, 255, 255)
        # for _ in range(rng.randint(1, 2)):
        rng_col = np.random.RandomState(
            self.__hash__() % (2**32 - 1)) 
        mid_col = (
            col[0] + rng_col.randint(-150, 0),
            col[1] + rng_col.randint(-150, 0),
            col[2] + rng_col.randint(-150, 0)
        )
        rand_mid = (
            mid + rng.normal(0, self.res // 12) * oversample,
            mid + rng.normal(0, self.res // 12) * oversample
        )
        width = self.res // 30 * oversample

        if any(connectors.values()):
            draw.ellipse(
                [rand_mid[0] - width//2, 
                rand_mid[1] - width//2, 
                rand_mid[0] + width//2, 
                rand_mid[1] + width//2], 
                fill=mid_col)
        for n in Neig:
            if connectors[n]:
                if n == Neig.UP:
                    side = (mid, 0)
                elif n == Neig.DOWN:
                    side = (mid, self.res * oversample)
                elif n == Neig.LEFT:
                    side = (0, mid)
                elif n == Neig.RIGHT:
                    side = (self.res * oversample, mid)
                # draw line in bits
                n = self.res * oversample // 2
                for i in range(n):
                    bit_col = (
                        mid_col[0] + (col[0] - mid_col[0]) * i // n,
                        mid_col[1] + (col[1] - mid_col[1]) * i // n,
                        mid_col[2] + (col[2] - mid_col[2]) * i // n
                    )
                    start = (
                        rand_mid[0] + i * (side[0] - rand_mid[0]) // n,
                        rand_mid[1] + i * (side[1] - rand_mid[1]) // n
                    )
                    end = (
                        rand_mid[0] + (i + 1) * (side[0] - rand_mid[0]) // n,
                        rand_mid[1] + (i + 1) * (side[1] - rand_mid[1]) // n
                    )
                    draw.line([start, end], fill=bit_col, width=width)
                draw.ellipse(
                    [side[0] - width//2, 
                    side[1] - width//2, 
                    side[0] + width//2, 
                    side[1] + width//2], 
                    fill=col)
                    
        img = img.resize((self.res, self.res), PIL.Image.LANCZOS)
        return img
                
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

    # directory for saving the progress images
    IMG_FOLDER = "img"
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER)
    else:
        for f in os.listdir(IMG_FOLDER):
            os.remove(os.path.join(IMG_FOLDER, f))

    def progress_callback(wfc, i, i_max):
        digits = len(str(i_max))
        str_i = str(i).zfill(digits)
        image = wfc.graphics()
        cv2.imshow("image", np.array(image))
        # time.sleep(0.1)
        cv2.imwrite(os.path.join(IMG_FOLDER, f"{str_i}.png"), np.array(image))
        cv2.waitKey(1)

    wfc.generate(progress_callback)

    with imageio.get_writer(os.path.join(IMG_FOLDER, 'wfc.gif'), mode='I') as writer:
        for filename in sorted(os.listdir(IMG_FOLDER)):
            image = imageio.imread(os.path.join(IMG_FOLDER, filename))
            writer.append_data(image)
    cv2.waitKey(0)

    print("\n\n")
    print("done")
    print(str(wfc))



if __name__ == '__main__':
    main()
