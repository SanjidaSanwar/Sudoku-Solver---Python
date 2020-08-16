## Sudoku Solver 

## Dependencies:
1. Numpy
2. Tesseract-eng
3. Scikit-image
4. Imutils

## Command to Run: 
The command to run the software is: ./sudokuImageSolver.py 

Video of the code running is included at the end of the presentation (7:46)

## Introduction:

This project takes an image of a sudoku puzzle printed on paper and solves it.

## The Challenge:
The algorithm needs to be fed a real-time snapshot via a phone camera or a scanned image of a sudoku puzzle page.

The program uses OpenCV's edge detection feature to find the game board. Once these edges have been detected, the program uses an algorithm t determine the discrete input boxes from the edges as well as the different line thickness for the unique groups. This is doubly important for variants where the 1-N character groups are not always a uniform box (ie. Jigsaw).

The program uses an OCR (Optical Character Recognition) engine called Tesseract to determine which unique character is where on the game grid (for both answers and clues) so that these can then be passed on to the solving algorithm.



Resources: 
* http://sudokugrab.blogspot.com/2009/07/how-does-it-all-work.html
* https://en.wikipedia.org/wiki/Thresholding_%28image_processing%29
* https://en.wikipedia.org/wiki/Connected-component_labeling
* https://en.wikipedia.org/wiki/Hough_transform
* http://www.robots.ox.ac.uk/%7Evgg/presentations/bmvc97/criminispaper/
* https://en.wikipedia.org/wiki/Optical_character_recognition
* https://en.wikipedia.org/wiki/Pattern_recognition
* https://en.wikipedia.org/wiki/Artificial_neural_network
