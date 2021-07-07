import cv2
import pytesseract as tess
from PIL import Image
import re
import numpy as np
import csv
import imutils

reader = csv.reader(open('resources/dict.csv', 'r'))                            #open the .csv file of the german districts in read-mode and convert it to a 2 dimensional array of the 2 coloums: abbreviation and clear text (Example: [SU] [Rhein-Sieg-Kreis/Siegburg]
districtDict = {}                                                               #empty the dictionary variable
for row in reader:                                                              #for all elements in reader
    k, v = row                                                                  #save the abbreviation and the clear text
    districtDict[k] = v                                                         #save it into the dictionary variable




class IdentifyLicensePlate:

    def __init__(self, path, showImages = False, showDebug = False):
        self.rawImage = cv2.imread(path)                        # Bild Importieren
        self.name = (path.split("/")[1]).split(".")[0]          # aus dem Path den Datei
        self.feature = ''
        self.district = ''
        self.showImages = showImages
        self.showDebug = showDebug
        self.flag = False

    ''' This Function gets a single picture or a list of pictures convert the image/s to text and validates the format. 
    It returns the found Licenseplate number '''
    def getLicenseplateString(self):

        imgJpgList = self.findAndCropLicenseplate()                             #Calling the function for the initial Path to find and crop the Licenseplate out of the picture

        if self.showDebug == True:                                              #-----Debug------
            print("initial path")
        for img in imgJpgList:                                                  #For n elements in imgJpgList
            self.validateFormat(tess.image_to_string(img, config='--psm 13'))   #Convert the image to text in single Line Mode ('--psm13') and validate the format of the converted text
            if self.flag:                                                       #If a valid format was found...
                return self.feature                                             #...return the found Licenseplate number


        if not self.flag:                                                       #If no valid format was found...
            if self.showDebug == True:                                          #-----Debug------
                print("Nothing found on initial path!")
                print("alternative path")
            for factor in range(1,5):                                           #iterate the factor for the Edgedetection from 1 to 5 to change filter settings
                imgJpg = self.originalImgEdgeDetection(factor)                  #Call the function for the alternative Path to do an edge detection for the whole given Image
                self.validateFormat(tess.image_to_string(imgJpg))               #Convert the whole Image in default (page text detection) to text and validate if it's a valid Licenceplatenumber format
                if self.flag:                                                   #If a valid format was found...
                    return self.feature                                         #Return the Licenseplatenumber
            if not self.feature:                                                #If there was no Licenseplate recognized..
                if self.showDebug == True:                                      #-----Debug------
                    print("Nothing found on alternative path!")
        return "No licenseplate recognized!"

    '''This function looks for patterns of European Licenseplate format in a given Picture of a car and returns all the found pattern matching cutouts. 
    It is the Initial path for finding the Licenseplatenumber '''
    def findAndCropLicenseplate(self):
        img = self.rawImage                                                                 #get the Raw Image
        imgGrey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)                                     #Convert the RGB picture into a greyscale picture
        imgBlur = cv2.bilateralFilter(imgGrey, 13, 15, 15)                                  #Blur the image to soften the edges
        edged = cv2.Canny(imgBlur, 200, 700, apertureSize=3, L2gradient = True)             #Detect all edges in the image and return the edge picture

        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)    #Generate contour mask
        contours = imutils.grab_contours(contours)                                          #Find all closed contours in the image
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]                 #Keep the first 10 found contours an sort them descending by size
        screenCnt = []                                                                      #Empty array screenCnt

        for c in contours:
            # approximate the contour
            peri = cv2.arcLength(c, True)                                                   #Measure the perimeter of the contours
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)                                #Approximate the shape of the contours (corners -> x-y-Coordinates)
            # if our approximated contour has four points, then
            # we can assume that we have found our screen
            if len(approx) == 4:                                                            #If the approximated shape has 4 corners (4 * x-y-coordinates)...
                screenCnt.append(approx)                                                    #Save the found contour

        # Masking the part other than the number plate

        i = 0
        imgList = []                                                                        #Empty the array of imgList
        for count in screenCnt:                                                             #Iterate through the found shapes
            imgList.append(self.rawImage[count[:,0,1].min():count[:,0,1].max(),count[:,0,0].min() : count[:,0,0].max()]) #Cut the shapes out of the original image and append that on a list
                #cv2.imshow(str(i), self.imageList[i])
            i += 1

        editedImgList = []                                                                  #Empty the array of editedImgList
        for img in imgList:                                                                 #For every coutout in imgList
            if self.showImages == True:                                                     #-----Debug------
                cv2.imshow(self.name + str(len(img)) + 'preEdit', img)
            if img.size != 0 :                                                              #If there is an reasonable sized cutout
                #img = self.dilateErode(img)
                img = self.convertToBaW(img, 80)                                            #Convert the cutout from RGB to a greyscale image
                imgBlurred = cv2.GaussianBlur(img, (3,3), 2000)                             #Blur the cutout to soften the edges
                imgJpg = Image.fromarray(imgBlurred)                                        #Convert the blurred cutout from a Numpy array to a .jpg format
                editedImgList.append(imgJpg)                                                #Append the .jpg image on the list editedImgList

        return editedImgList                                                                #Return the list of the edited cutouts

    '''This function validates the Format of the given string whether it's a licenseplatenumber or not. It also returns the (german) district the car owner is living '''
    def validateFormat(self, text):
        if(len(text)>1):                                                                    #If the given string is bigger 1...
            if self.showDebug == True:                                                      #-----Debug------
                print("original text:"+repr(text))

            textarray = text.splitlines()                                                   #Split the lines of the given string which are indicated with '\n' into seperate strings
            feature = str()                                                                 #Empty the text output variable
            for text in textarray:                                                          #For every Line in the textArray
                text = re.sub('[^A-Za-z0-9]+', ' ', text)                                   #Replace every element which is not a character or a number with a space
                temp = re.compile("([a-zA-Z]+)[' ']([a-zA-Z]+)[' ']*([0-9]+)([a-zA-Z]*)")   #Generate a coarse pattern with 1.(0 or more characters) 2. ('Space') 3. (again 0 or more characters) 4. ('Space') 5. (0 or more numbers) 6.(possibility for another character)
                if temp.match(text):                                                        #if there is a string matching the pattern...
                    if self.showDebug == True:                                              #-----Debug------
                        print("temp.match")
                    res = temp.match(text).groups()                                         #Seperate the found patternmatchin string into different groups

                    for string in res:                                                      #For every group in the array res
                        if string == res[0]:                                                #At the first element of the res array
                            feature = feature + string                                      #Write the first group at the start of the string
                        else:                                                               #If not in the first group
                            feature = feature + " "                                         #append a 'Space' behind the fore group
                            feature = feature + string                                      #Append the next group to the string

                    if self.showDebug == True:                                              #-----Debug------
                        print("text after combining:" + feature)
                    match = re.match(r"[A-Z]{1,3}[' '][A-Z]{1,3}[' '][0-9]{1,4}|[A-Z]{1,3}[' '][A-Z]{1,3}[' '][0-9]{1,4}[' '][A-Z]",feature)    #Generate a fine pattern with 1.(1 to 3 characters) 2. ('Space') 3. (again 1 to 3 characters) 4. ('Space') 5. (1 to 4 numbers) 6. ('Space') 7. (eventually another character)
                    if match:                                                               #If the before denoised string matches the finer pattern...
                        self.feature = match.string                                         #Save the pattern matching string
                        self.district = districtDict[match.string.split(" ")[0]]            #split the matching string at the first space, and look up the corresponding district in the district dictionary
                        self.flag = True                                                    #Set the flag True to signal a succesful match
                        break                                                               #Break the for loop
                    else:
                        if self.showDebug == True:                                          #-----Debug------
                            print("no match!")
        else:
            if self.showDebug == True:                                                       #-----Debug------
                print("len < 1")

    '''This function converts a given grayscale image into a binary black and white image by a given threshold '''
    def convertToBaW(self, img, threshold):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)                                          #Convert the given image from RGB to a grayscale image
        for n in range(0, np.shape(img)[0]):                                                 #For every row in the numpy-array image...
            for m in range(0, np.shape(img)[1]):                                             #And for every coloum
                if img[n][m] > threshold:                                                    #If the value of the pixel is beyond a certain threshold...
                    img[n][m] = 255 # alle Pixel oberhalb des threshold werden weiß          #Set the value of the pixel to white (255)
                else:                                                                        #If the value of the pixel is below the threshold...
                    img[n][m] = 0                                                            #Set the pixel to black (0)
        return img                                                                           #Return the black and white image
    '''This function converts the given image by a factor to an edge detected image
    It is the alternative path for finding the Licenseplatenumber'''
    def originalImgEdgeDetection(self, factor):
        img = self.rawImage                                                                 #Get the raw image
        imgGrey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)                                     #convert the RGB Image to a grayscale image
        imgBlur = cv2.bilateralFilter(imgGrey, 13, 15, 15)                                  #Blur the image to soften the edges
        imgEdged = cv2.Canny(imgBlur, 200, 400 + factor * 100, apertureSize=3, L2gradient=True)#Detect all edges with the Canny filter and a factor
        if self.showImages == True:                                                         #-----Debug------
            cv2.imshow('corners ' +str(factor) + " " + self.name, imgEdged)
        imgJpg = Image.fromarray(imgEdged)                                                 #Convert the numpy-array image to a .jpg format
        return imgJpg                                                                      #Return the .jpg image

    '''This function finds the European standardized blue lining on the left side of the Licenseplate as a feature'''
    def get_blue(self, image):
        imgBlue = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)                                    #Convert RGB image to HSV Image to get a better color spectrum to find the feature
        lower_range = np.array([110,50,50])                                                 #Define the lower threshold for the blue color
        upper_range = np.array([130,255,255])                                               #Define the upper threshold for the blue color
        mask = cv2.inRange(imgBlue, lower_range, upper_range)                               #Look for all areas which satisfy the condition of the lower and the upper threshold
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    #Find contours in the before found areas of 'blue'
        if len(contours) > 0 :                                                              #If there where contours found...
            licensePlate = max(contours, key=cv2.contourArea)                               #Find the rectangle shape with the biggest area and save the coordinates of the corners
            x, y, w, h = cv2.boundingRect(licensePlate)                                     #Save the x-y-coordinates of the found rectangle and also width and height of the ractangle shape
            if self.showImages == True:
                cv2.rectangle(imgBlue, (x, y), (x + w, y + h), (0, 255, 0), thickness=3)       #Draw a red rectangle around the found shape
                cv2.imshow('inBlue', cv2.cvtColor(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)], cv2.COLOR_HSV2BGR))    #show the rectangle on the raw image
            if np.shape(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)])[1] > 0:       #looks for the normalized size of the blue part of the Licenseplate
                return cv2.cvtColor(imgBlue[y:y + h, x + w : int(x + h * (570 / 110) - w)], cv2.COLOR_HSV2BGR)  #return the Cutout image converted to RGB
            else:                                                                           #if there is no normalized sized rectangle shape found
                return np.empty(0)                                                          #Return an empty array
        else:                                                                               #If there where no contours found...
            return np.empty(0)                                                              #Return an empty array
        #print(np.shape(imgBlue)[0] * np.shape(imgBlue)[1])
        #print('x: ' + str(x) + ' y: ' + str(y) + 'dimension: ' + str(np.shape(imgBlue)))
        #self.imgCountry = cv2.cvtColor(imgBlue[y:y+h,x:x+w], cv2.COLOR_HSV2BGR)








