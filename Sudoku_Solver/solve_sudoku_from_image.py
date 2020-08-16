#!/usr/bin/python3

import imutils
import cv2
import pytesseract
import sys
import Sudoku_Solver.sudoku_solver as ss


class SudokuSolver:
    def __init__(self,imageToSolve,display):
        # compute size of single field of 9x9 array of image
        self.inner_rect_width = int(500/9)

        self.columns = "123456789"
        self.rows = "ABCDEFGHI"

        self.sudoku = {}
        self.original_positions = []
        self.image = imageToSolve

        self.display=display

        # Check if sudoku is not fullscreen
        tmp_image = imutils.resize(self.image, height=500)


        contours, hierarchy = self.findContoursAndHierarchy(tmp_image);
        #Find largest rect in image
        self.findLargestRect(contours);

        # resize image to 500x500
        resizedImage = imutils.resize(self.image, height=500)

        #self.display.displayImage(resizedImage)

        # create copy of original image
        self.original_image = resizedImage.copy()

        contours, hierarchy = self.findContoursAndHierarchy(resizedImage);
        #Store digits
        self.storeDetectedDigits(resizedImage,contours);
        #Fill remaining spaces with 0s
        self.fillEmptySpaces();
        #Print solution on original image
        self.printSolution();


        self.display.displayImage(self.original_image)

        # save image with solution
        #cv2.imwrite("./____________solvedSudoku_newProj.jpg", self.original_image)
        #img = cv2.imread("./____________solvedSudoku_newProj.jpg")
        #cv2.imshow('img', img)
        #cv2.waitKey(0)


# Helper image to return contours and hierarchy of an image
    def findContoursAndHierarchy(self,image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray,127,255,0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours,hierarchy;

# Find largest rectangle in image
    def findLargestRect(self,contours): 
        highest = 0
        bounding_rect = None
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            rect_size = w*h
            if rect_size < 250000 and rect_size > 100000 and rect_size > highest:
                highest = rect_size
                bounding_rect = cv2.boundingRect(cnt)

        # if highest rectangle is found crop image
        if not highest == 0:
            x,y,w,h = bounding_rect
            self.image = tmp_image[y:y+h, x:x+w]
        #return image






    def storeDetectedDigits(self,image,contours):        
        # iterate detected numbers
        for cnt in contours:

            # get parameters of bounding rectangle of detected part of image
            x,y,w,h = cv2.boundingRect(cnt)

            # compute size of detected part
            rect_size = w*h

            # check if detected part of image is of appropriate size
            if rect_size <= 2000 and rect_size > 400:

                # compute coordinates of center of rectangle
                x_middle = int(x+(w/2))
                y_middle = int(y+(h/2))

                # compute coordinates of rectangle
                x_coord = int(x_middle/self.inner_rect_width)
                y_coord = int(y_middle/self.inner_rect_width)

                # crop image part where a digit is detected
                tmp_image = image[y-2:y+h+2, x-2:x+w+2]
                gray = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # use tesseract to detect digits from cropped image parts
                config = ("--oem 2 --psm 10")
                detected_digit = pytesseract.image_to_string(blurred, lang="eng", config=config)

                # store detected digit
                self.sudoku[self.rows[y_coord]+self.columns[x_coord]] = str(detected_digit)

                #cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
                #cv2.rectangle(image, (x_middle,y_middle), (x_middle,y_middle), (255,0,0), 2)
                #font = cv2.FONT_HERSHEY_PLAIN
                #cv2.putText(image, str(x_coord)+":"+str(y_coord), (x,y), font, 1, (0,0,0), 1, cv2.LINE_AA)

    def fillEmptySpaces(self):
        # fill empty spaces with 0
        for r in self.rows:
            for c in self.columns:
                key = r+c
                if not key in self.sudoku:
                    self.sudoku[key] = str(0)
                else:
                    self.original_positions.append(r+c)


    def printSolution(self):
        # generate string from detected sudoku
        detected_sudoku_string = ss.generate_string_from_sudoku(self.sudoku)

        # solve sudoku
        solved_sudoku = ss.solve_sudoku(detected_sudoku_string)

        # check if sudoku was valid and can be solved
        if solved_sudoku == False:
            print("Not Solvable")
            sys.exit(0)

        # print solution into image
        font = cv2.FONT_HERSHEY_COMPLEX
        for x in range(0,9):
            for y in range(0,9):
                row = self.rows[y]
                col = self.columns[x]
                if row+col in self.original_positions:
                    continue
                pos_x = x*self.inner_rect_width+15
                pos_y = y*self.inner_rect_width+45
                cv2.putText(self.original_image, solved_sudoku[row+col], (pos_x,pos_y), font, 1.5, (255,0,0), 1, cv2.LINE_AA)


