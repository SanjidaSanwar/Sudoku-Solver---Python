#!/usr/bin/env python3

"""
Sudoku Image Solver uses image processing techniques to extract sudoku puzzle
Requires Python 3, OpenCV (for image processing)
USAGE: python3 sudokuImageSolver.py to launch in GUI and python3 sudokuImageSolver_console.py to launch in console
"""

import cv2
import numpy as np
from copy import deepcopy
from settings import DISPLAY_IMG, OUTPUT_PATH
import os


class Display:
	images=None
	def __init__(self,graphicalUserInterface=False):
		self.graphicalUserInterface=graphicalUserInterface
		self.images=[]

	def displayImage(self,image,title="Sudoku Puzzle"):
		if(not DISPLAY_IMG):
			return
		else:
			cv2.imshow(title,image)
			cv2.imwrite(OUTPUT_PATH, image)
			cv2.waitKey(0)


"""
This method finds the largest connected pixel structure in image and returns the seed of it
"""
def findLargestFeatureInImage(image,topLeft=None,bottomRight=None):
	img=deepcopy(image)

	height,width=image.shape[:2]

	if(topLeft is None):
		        #(x,y)
		topLeft=(0,0)
	if(bottomRight is None):
		             #(x,y)
		bottomRight=(width,height)


	if(bottomRight[0]-topLeft[0]>width or bottomRight[1]-topLeft[1]>height):
		raise ValueError("Error in findLargestFeatureInImage: coordinate of topLeft and bottomRight cannot be larger than the image it")


	maximumArea=0
	seed=None

	for y in range(topLeft[1],bottomRight[1]):
		for x in range(topLeft[0],bottomRight[0]):
			if(img.item(y,x)==255 and x<width and y<height):
				#flood fill current feature with grey
				featureArea=cv2.floodFill(img,None,(x,y),64)
				if(featureArea[0]>maximumArea):
					maximumArea=featureArea[0]
					seed=(x,y)

	feature, cornerPoints=computeBoundingBoxOfFeature(image,seed,boundingBox=False)

	return feature,cornerPoints,seed

"""
This method returns a box (or corner points if includeBoundingBox is False) bounding the connected pixels on (x,y)
1. We will first fill all features in the image with grey
2. Then we fill all the zero valued pixels in the same connected component as seed with white
3. We then fill all those grey pixels with black
4. By looping through all the pixels, we can examine the whites and compute the corner points or bounding box of it
"""
def computeBoundingBoxOfFeature(image,seed,boundingBox=True):
	sudokuImage=deepcopy(image)
	height,width=image.shape[:2]

	#https://docs.opencv.org/2.4/modules/imgproc/doc/miscellaneous_transformations.html?highlight=floodfill#floodfill
	mask=np.zeros((height+2,width+2),np.uint8)

	#flood fill all features with grey
	for y in range(height):
		for x in range(width):
			if(sudokuImage.item(y,x)==255 and x<width and y<height):
				cv2.floodFill(sudokuImage,None,(x,y),64)

	#flood fill all zero valued pixels in the same connected component as seed with white
	#after this step only the target feature will be white in the input image, everything else will be black/grey
	if(seed is not None):
		if(seed[0] is not None and seed[1] is not None):
			cv2.floodFill(sudokuImage,mask,seed,255)

	#we initialize our corner points to be the opposite of their points, 
	#for example, the coordinates for top left will be coordinates of bottom right, coordinates of top right will be coordinates of bottom left and so on
	#this allows us to make the safe assumption that if the area is negative or if the area is small, there is no digit in the image
	topLine=height; bottomLine=0; leftLine=width; rightLine=0
	topLeft=(width,height); topRight=(0,height); bottomLeft=(width,0); bottomRight=(0,0)

	for y in range(height):
		for x in range(width):
			if(sudokuImage.item(y,x)==64):
				#colour everything that is not our target feature with black colour
				cv2.floodFill(sudokuImage,mask,(x,y),0)
			#if this is our target feature, we compute the corner point/bounding box of it
			if(sudokuImage.item(y,x)==255):
				if(boundingBox):
					if(x<leftLine):
						leftLine=x

					if(x>rightLine):
						rightLine=x

					if(y<topLine):
						topLine=y

					if(y>bottomLine):
						bottomLine=y
				else:
					##Idea:
					#our initial topLeft (width,height) has the max sum of the image. topLeft should be coordinates with minimum sum
					if(x+y<sum(topLeft)):
						topLeft=(x,y)
					#our initial bottomRight (0,0) has the minimum sum of the image. bottomRight should be coordinates with maximum sum
					if(x+y>sum(bottomRight)):
						bottomRight=(x,y)
					#our initial topRight (0,height) has the minimum difference between x and y of the image. topRight should have maximum difference between x and y
					if(x-y>topRight[0]-topRight[1]):
						topRight=(x,y)
					#our initial bottomLeft (width,0) has the maximum difference between x and y of the image. bottomLeft should have minimum difference between x and y
					if(x-y<bottomLeft[0]-bottomLeft[1]):
						bottomLeft=(x,y)


	if boundingBox:
		topLeft=(leftLine,topLine)
		bottomRight=(rightLine,bottomLine)
		cornerPoints=np.array([topLeft,bottomRight],dtype="float32")
	else:
		cornerPoints=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype="float32")

	return sudokuImage,cornerPoints
