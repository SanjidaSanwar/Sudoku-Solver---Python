#!/usr/bin/env python3

import os
from random import randint, shuffle

#InputFileDetails
sudokuImageFolder="dataset/sudokuImage"
filename="image5.jpg"
sudokuImagePath=os.path.join(sudokuImageFolder,filename)
OUTPUT_PATH = "./dataset/sudokuImage/"+"image5_solution.jpg"

#Decides whether image should be displayed when in console mode
DISPLAY_IMG=True

MAXIMUM_HEIGHT=900
MAXIMUM_WIDTH=900
