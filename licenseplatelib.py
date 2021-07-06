import cv2
import pytesseract as tess
from PIL import Image
import re
import numpy as np
import csv
import imutils

reader = csv.reader(open('resources/dict.csv', 'r'))
districtDict = {}
for row in reader:
    k, v = row
    districtDict[k] = v




class IdentifyLicensePlate:

    def __init__(self, path):
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
        print("findAndCrop")
        for img in imgJpgList:                                                  #For n elements in imgJpgList
            self.validateFormat(tess.image_to_string(img, config='--psm 13'))   #Convert the image to text in single Line Mode ('--psm13') and validate the format of the converted text
            if self.flag:                                                       #If a valid format was found...
                return self.feature                                             #...return the found Licenseplate number


        print("originalImgEdgeDetection")
        if not self.flag:
            for factor in range(1,5):
                imgJpg = self.originalImgEdgeDetection(factor)
                self.validateFormat(tess.image_to_string(imgJpg))
                if self.flag:
                    return self.feature
        return "No licenseplate recognized"

    def findAndCropLicenseplate(self):                                                      #This Function finds, in a given Picture of a car the Licenseplate,
        img = self.rawImage
        #cv2.imshow('imageBlur', imageBlur)
        #img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        imgGrey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)                                     # zu Grau (1-Dimensionale Pixel) konvertieren
        #cv2.imwrite('Results/COLOR_RGB2GRAY.jpeg',imgGrey)                                 #Zum Bild Speichern
        #imageBlur = cv2.GaussianBlur(imageGrey, (3, 3), 1)                                 # Bild glätten
        imgBlur = cv2.bilateralFilter(imgGrey, 13, 15, 15)
        #cv2.imwrite('Results/bilateralFilter.jpeg', imgBlur)                               #Zum Bild Speichern
        #imageBlur = cv2.medianBlur(imageGrey, 3)
        #cv2.imshow('Bilateral' + self.name, imgBlur)
        edged = cv2.Canny(imgBlur, 100, 200, apertureSize=3, L2gradient = True)
        #cv2.imshow('Kanten' + self.name, edged)                                            #Zum Bild Speichern
        #cv2.imwrite('Results/Canny.jpeg', edged)
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        screenCnt = []
        for c in contours:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)
            # if our approximated contour has four points, then
            # we can assume that we have found our screen
            if len(approx) == 4:
                screenCnt.append(approx)

        # Masking the part other than the number plate

        i = 0
        imgList = []
        for count in screenCnt:
            imgList.append(self.rawImage[count[:,0,1].min():count[:,0,1].max(),count[:,0,0].min() : count[:,0,0].max()])
                #cv2.imshow(str(i), self.imageList[i])
            i += 1

        editedImgList = []
        for img in imgList:
            if self.showImages == True:
                cv2.imshow(self.name + str(len(img)) + 'preEdit', img)   #Für Presentation zeigen
            if img.size != 0 :
                #img = self.dilateErode(img)
                img = self.convertToBaW(img, 80)
                imgBlurred = cv2.GaussianBlur(img, (3,3), 2000)
                #img = cv2.medianBlur(img, 3)
                #bilateralSigma = 2
                #img = cv2.bilateralFilter(img, 9, bilateralSigma, bilateralSigma)
                #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
                imgJpg = Image.fromarray(imgBlurred)
                editedImgList.append(imgJpg)

        return editedImgList

    def validateFormat(self, text):
        if(len(text)>1):
            #print("original text:" + text)
            text = re.sub('[^A-Za-z0-9]+', ' ', text)
            #print(text)
            temp = re.compile("([a-zA-Z]+)[' ']([a-zA-Z]+)[' ']*([0-9]+)([a-zA-Z]*)")
            feature = str()
            if temp.match(text):
                res = temp.match(text).groups()
                #print(res)

                for string in res:
                    if string == res[0]:
                        feature = feature + string
                    else:
                        feature = feature + " "
                        feature = feature + string

                #print("text after combining:" + feature)
                match = re.match(r"[A-Z]{1,3}[' '][A-Z]{1,3}[' '][0-9]{1,4}|[A-Z]{1,3}[' '][A-Z]{1,3}[' '][0-9]{1,4}[' '][A-Z]",feature)
                if match:
                    #print('match: ' +match.string)
                    self.feature = match.string
                    self.district = districtDict[match.string.split(" ")[0]]
                    #print("hat gematched")
                    return True
                else:
                    #print("hat nicht gematched")
                    return False
        else:
            return False

    def convertToBaW(self, img, threshold):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        for n in range(0, np.shape(img)[0]):
            for m in range(0, np.shape(img)[1]):
                if img[n][m] > threshold:
                    img[n][m] = 255 # alle Pixel oberhalb des threshold werden weiß
                else:
                    img[n][m] = 0
        return img

    def get_blue(self, image):
        # Bild einlesen und in HSV-Farbraum konvertieren
        #cv2.imshow("pimmel",image)
        imgBlue = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        #print(type(imgBlue))

        # Farbraum definieren (Blau)
        lower_range = np.array([110,50,50])
        upper_range = np.array([130,255,255])

        # blaue Bereiche finden und größten mit Rechteck markieren
        mask = cv2.inRange(imgBlue, lower_range, upper_range)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0 :
            licensePlate = max(contours, key=cv2.contourArea)

            # Box wird umm blauen Bereich im Bild gezeichnet
            x, y, w, h = cv2.boundingRect(licensePlate)
            cv2.rectangle(imgBlue, (x, y), (x + w, y + h), (0, 255, 0), thickness=3)
            #cv2.imshow( 'Pimmel ',imgBlue)
            #cv2.imshow('inBlue', cv2.cvtColor(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)], cv2.COLOR_HSV2BGR))
            #print('shape: ' + str(np.shape(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)])[1]))
            #print('x: ' + str(x))
            #print('y: ' + str(y))
            #print('w: ' + str(w))
            #print('h:  ' + str(h))
            #print('w max ' + str(x + int( h * (520 / 110))- w))
            #print( 'Ausschnitt: y  ' + str(y) + ' '+ str(y+h) + ' x: '+ str(x+w) + ' '+ str(int(x + h * (520 / 110) - w)))
            if np.shape(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)])[1] > 0:
                #cv2.imshow("pimmel",imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)])
                return cv2.cvtColor(imgBlue[y:y + h, x + w : int(x + h * (570 / 110) - w)], cv2.COLOR_HSV2BGR)
            else:
                return np.empty(0)
        else:
            return np.empty(0)
        #print(np.shape(imgBlue)[0] * np.shape(imgBlue)[1])
        #print('x: ' + str(x) + ' y: ' + str(y) + 'dimension: ' + str(np.shape(imgBlue)))
        #self.imgCountry = cv2.cvtColor(imgBlue[y:y+h,x:x+w], cv2.COLOR_HSV2BGR)








