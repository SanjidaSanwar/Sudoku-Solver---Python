#!/usr/bin/env python3

"""
Helper file to extract the sudoku puzzle from an image using cv2 and skimage
Retrieved from: https://github.com/fzy1995/SudokuImageSolver
"""

import cv2
import numpy as np
import Displayer.displayer as Displayer
from copy import deepcopy
from skimage import exposure


class ExtractSudokuPuzzle:
	preprocessedExtracted=None
	postProcessedExtracted=None

	def __init__(self,sudokuImage,display):
		self.display=display

		grayscale=cv2.cvtColor(sudokuImage,cv2.COLOR_BGR2GRAY)
		preprocessed=self.preprocessImage(grayscale)
		
		#Find sudoku puzzle with the largest contour and largest feature 
		image, quadrangle=self.findSudokuPuzzleGrid(preprocessed,sudokuImage)

		#Compute the maximum height and width of sudoku puzzle based of the 4 corners
		maxWidth,maxHeight=self.computeMaxWidthAndHeightOfSudokuPuzzle(quadrangle)

		#Warps the sudoku puzzle to get a top down view
		warpedSudokuPuzzle=self.extractSudokuPuzzleAndWarpPerspective(quadrangle,maxWidth,maxHeight,sudokuImage)

		#Resize the extracted sudoku puzzle, convert it to grayscale and rescale intensity of it
		postProcessed=self.postProcessExtractedSudokuPuzzle(warpedSudokuPuzzle)

		self.preprocessedExtracted=self.postProcessExtractedSudokuPuzzle(warpedSudokuPuzzle,postProcess=False)
		self.postProcessedExtracted=postProcessed
		#self.image=warpedSudokuPuzzle
		

	"""
	1. apply bilateral filter to removes noise while keeping the edges sharp using a function called pixel difference(oherwise all the pixels get blurred)
	2. Erosion to close the small holes in the object
	3. Change the image into black and white using adaptive threshold
	4. Return the threshold 
	"""
	def preprocessImage(self,sudokuImage):
		blurred=cv2.bilateralFilter(sudokuImage,5,75,75)

		kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
		#removes small holes, smoothen the contour in the image
		closed=cv2.morphologyEx(blurred,cv2.MORPH_CLOSE,kernel)
		
		div=np.float32(blurred)/(closed)
		normalized=np.uint8(cv2.normalize(div,div,0,255,cv2.NORM_MINMAX))
		#perform adaptive threshold to turn the image into binary image (anything that's larger than threshold get turned into different colour)
		threshold=cv2.adaptiveThreshold(normalized,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
		#invert it such that the object in white is now the lines
		threshold=cv2.bitwise_not(threshold)

		if((threshold==0).all()):
			threshold=cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11,2)

		#self.display.displayImage(threshold)

		return threshold



	"""
	We assume that our sudoku puzzle has four points and has the largest grid in the image.
	Hence, by finding the largest contour which has 4 points, we can safely say that it is the sudoku puzzle that we are finding.

	This method find the largest contour in the preprocessedSudokuImage that has 4 points and return the contour
	"""
	def findLargestContour(self,preprocessedSudokuImage):
		# originalSudokuImage=deepcopy(originalSudokuImage)

		#find contours in the binary image of sudokuImage and obtain the end points of them in a list (without hierarchical relationships)
		contours,hierarchy=cv2.findContours(preprocessedSudokuImage,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
		#the minimum area that is required in order to be considered as a potential contour for sudoku image is 300 (subject to change)
		minArea=300
		maxArea=0
		largestContour=None
		for contour in contours:
			currentArea=cv2.contourArea(contour)
			if(currentArea>minArea):
				#find the perimeter of the closed contour
				currentPerimeter=cv2.arcLength(contour,True)
				#obtain an approximate to the current contour
				currentApproximate=cv2.approxPolyDP(contour,0.02*currentPerimeter,True)
				#if current area is the largest area and it has four points (a square grid), this is the grid of sudoku image puzzle we are searching for
				if(currentArea>maxArea and len(currentApproximate)==4):
					maxArea=currentArea
					largestContour=currentApproximate

		# cv2.drawContours(originalSudokuImage,[largestContour],-1,(0,255,0),3)
		# self.display.displayImage(originalSudokuImage)

		return largestContour,maxArea


	def findSudokuPuzzleGrid(self,preprocessedSudokuImage,originalSudokuImage):
		originalSudokuImage=deepcopy(originalSudokuImage)

		height,width=preprocessedSudokuImage.shape[:2]
		sudokuImageArea=height*width


		#Find largest conotur to find puzzle
		largestContour,largestContourArea=self.findLargestContour(preprocessedSudokuImage)


		#Find largest feature to find puzzle
		feature,cornerPoints,seed=Displayer.findLargestFeatureInImage(preprocessedSudokuImage)

		#Needs to be converted to tuple to draw the rectangle box 
		featureCornerPoints=cornerPoints.astype(int)
		featureCornerPoints=featureCornerPoints.tolist()
		topLeft,topRight,bottomRight,bottomLeft=featureCornerPoints
		topLeft=tuple(topLeft); topRight=tuple(topRight); bottomRight=tuple(bottomRight); bottomLeft=tuple(bottomLeft)
		#Largest feature area is extracted
		largestFeatureArea=cv2.contourArea(cornerPoints)

		try:
			ratio=largestFeatureArea/largestContourArea
		except(ZeroDivisionError):
			if(largestFeatureArea==0):
				print("Error in findSudokuPuzzleGrid: Unable to extract sudoku puzzle from image.")
				exit()
			else:	
				ratio=0 

		#We can't use just either largest feature or largest contour 
		#because in some cases we can't expect to find the grid using just largest featur, we need the largest contour as well
		#If ratio is 0, or any other number between 0.95 and 1.5 it use largest feature area
		if(ratio<0.95 or ratio>1.5):
			cv2.line(originalSudokuImage,topLeft,topRight,(0,0,255),4)
			cv2.line(originalSudokuImage,bottomLeft,bottomRight,(0,0,255),4)
			cv2.line(originalSudokuImage,topLeft,bottomLeft,(0,0, 255),4)
			cv2.line(originalSudokuImage,topRight,bottomRight,(0,0, 255),4)
			self.display.displayImage(originalSudokuImage)
			return cornerPoints
		else: #else use largest contour
			cv2.drawContours(originalSudokuImage,[largestContour],-1,(0,0, 255),4)
			self.display.displayImage(originalSudokuImage)
			return originalSudokuImage,self.getQuadrangleVertices(largestContour)



	"""
	Obtain the corner points of sudoku puzzle grid and store it in quadrangle
	Reference to https://www.pyimagesearch.com/2014/05/05/building-pokedex-python-opencv-perspective-warping-step-5-6/ (A great and interesting article on how to build a pokedex from scratch)
	"""
	def getQuadrangleVertices(self,sudokuGrid):
		#Convert the corners of the contour from a 3d to 2d array.

		if(len(sudokuGrid)==0):
 			return None

		corners=sudokuGrid.reshape(len(sudokuGrid),2)

		# Create a rectangle of zeros in the form of 
		# [[0. 0.]     <-top left
 		# [0. 0.]	   <-top right
 		# [0. 0.]      <-bottom right
 		# [0. 0.]]     <-bottom left
		quadrangle=np.zeros((4,2),dtype="float32")

		#turn corners into a single dimension by summing the two values in each array up
		s=corners.sum(axis=1)
		#initialize rectangle to be in the order of top left, top right, bottom right, bottom left

		#top left has smallest sum, bottom right has largest sum
		quadrangle[0]=corners[np.argmin(s)]
		quadrangle[2]=corners[np.argmax(s)]
		
		difference=np.diff(corners,axis=1)
		#top right have minimum difference, bottom left have maximum difference
		quadrangle[1]=corners[np.argmin(difference)]
		quadrangle[3]=corners[np.argmax(difference)]

		return quadrangle

	"""
	Returns the maximum width and height of the image
	"""
	def computeMaxWidthAndHeightOfSudokuPuzzle(self,quadrangle):
		topLeft,topRight,bottomRight,bottomLeft=quadrangle

		#distance =  sqrt( (x2-x1)^2 + (y2-y1)^2 )
		upperWidth=np.sqrt( ((topRight[0]-topLeft[0])**2) + ((topRight[1]-topLeft[1])**2) )
		bottomWidth=np.sqrt( ((bottomRight[0]-bottomLeft[0])**2) + ((bottomRight[1]-bottomLeft[1])**2) )

		leftHeight=np.sqrt( ((topLeft[0]-bottomLeft[0])**2) + ((topLeft[1]-bottomLeft[1])**2) )
		rightHeight=np.sqrt( ((topRight[0]-bottomRight[0])**2) + ((topRight[1]-bottomRight[1])**2) )

		maximumWidth=max(int(upperWidth),int(bottomWidth))
		maximumHeight=max(int(leftHeight),int(rightHeight))

		return maximumWidth,maximumHeight


	"""
	Extract the puzzle and compute a transformation to get top-down view, then apply this transformation to originial image
	Reference to https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html (OpenCV tutorial)
	"""
	def extractSudokuPuzzleAndWarpPerspective(self,quadrangle,maximumWidth,maximumHeight,originalSudokuImage):
		originalSudokuImage=deepcopy(originalSudokuImage)
		
		#map the screen to a top down view
		destinationPoints=np.array([ [0,0],[maximumWidth-1,0],[maximumWidth-1,maximumHeight-1],[0,maximumHeight-1] ],dtype="float32")
		#Compute perspective transform
		M=cv2.getPerspectiveTransform(quadrangle,destinationPoints)
		#Apply transformation                           
		warp=cv2.warpPerspective(originalSudokuImage,M,(maximumWidth,maximumHeight))

		return warp

		#Convert the warped image to grayscale and rescale the intensity
	def postProcessExtractedSudokuPuzzle(self,warpedSudokuPuzzle,postProcess=True):
		if(postProcess):
			#Convert warped image to grayscale
			postProcessed= cv2.cvtColor(warpedSudokuPuzzle, cv2.COLOR_BGR2GRAY)
			#Adjust intensity of pixels to have min and max value of 0 and 255
			postProcessed=exposure.rescale_intensity(postProcessed,out_range=(0,255))
			postProcessed = cv2.resize(postProcessed,(450, 450),interpolation=cv2.INTER_AREA)
			self.display.displayImage(postProcessed)
		else:
			postProcessed = cv2.resize(warpedSudokuPuzzle,(450, 450),interpolation=cv2.INTER_AREA)
		return postProcessed
