#!/usr/bin/env python3
"""
Requires Python 3, OpenCV (for image processing), NumPy
USAGE: ./sudokuImageSolver_console.py to launch in console
"""

import cv2
import numpy as np
from settings import *
import Displayer.displayer as Displayer
from Sudoku.resizeSudokuImage import ResizeSudokuImage
from Extractor.extractSudokuPuzzle import ExtractSudokuPuzzle
from Sudoku_Solver.solve_sudoku_from_image import SudokuSolver



class SudokuImageSolver:
	def main(self):
		display=Displayer.Display()

		#resize sudoku image
		resized=ResizeSudokuImage(sudokuImagePath,MAXIMUM_WIDTH,MAXIMUM_HEIGHT,display)

		#extract sudoku puzzle from sudoku image
		extractedSudokuPuzzle=ExtractSudokuPuzzle(resized.sudokuImage,display)

		#The extracted sudoku puzzle is written to output_ path and read from there
		image = cv2.imread(OUTPUT_PATH)
		#The picture is resized, once to extract the puzzle, and then resize the image again to rescale intensity to get
		#the ocr engine to read the digits

		#The image read is passed on to the solver
		sudokuSol = SudokuSolver(image, display);
		
		#Destroy all windows at the end
		if(DISPLAY_IMG):
			cv2.destroyAllWindows()


sudokuImageSolver=SudokuImageSolver()
sudokuImageSolver.main()