import cv2
import pytesseract as tess
from PIL import Image
import re
import string
import numpy as np
import csv
import imutils

MorphX = 1
MorphY = 2
DilateErodeX_X = 3
DilateErodeX_Y = 4
DilateErodeY_X = 5
DilateErodeY_Y = 6
FactorWeightToHeight = 7

reader = csv.reader(open('resources/dict.csv', 'r'))
districtDict = {}
for row in reader:
    k, v = row
    districtDict[k] = v



parListe = [MorphX, MorphY, DilateErodeX_X, DilateErodeX_Y, DilateErodeY_X, DilateErodeY_Y, FactorWeightToHeight]


class IdentifyLicensePlate:

    def __init__(self, path):
        self.rawImage = cv2.imread(path)  # Bild Importieren
        self.path = path
        self.imageList = []
        self.feature = ''
        # param:
        self.parameter = {
            MorphX: 35,
            MorphY: 10,
            DilateErodeX_X: 30,
            DilateErodeX_Y: 5,
            DilateErodeY_X: 5,
            DilateErodeY_Y: 30,
            FactorWeightToHeight: 3,
        }

    def cut_image(self):

        #cv2.imshow('imageBlur', imageBlur)
        #img = cv2.resize(self.rawImage, (720, 480))
        imageGrey = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)  # zu Grau (1-Dimensionale Pixel) konvertieren
        #imageBlur = cv2.GaussianBlur(imageGrey, (3, 3), 1)  # Bild glätten
        imageBlur = cv2.bilateralFilter(imageGrey, 13, 15, 15)
        #cv2.imshow('pimmel' + self.path, imageBlur)
        edged = cv2.Canny(imageBlur, 30, 200, L2gradient = True)
        #cv2.imshow('Kanten' + self.path, edged)
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
        for count in screenCnt:

            self.imageList.append(self.rawImage[count[:,0,1].min():count[:,0,1].max(),count[:,0,0].min() : count[:,0,0].max()])
            #cv2.imshow(str(i), self.imageList[i])
            i += 1


    def change_parameter(self, parameter, amount):
        self.parameter[parameter] += amount

    def set_parameter(self, parameter, value):
        self.parameter[parameter] = value

    def platetext_format(self, text):
        print(text)
        text = re.sub('[^A-Za-z0-9]+', ' ', text)
        match = re.match(r"[A-Z]{2,5}[0-9]{1,4}|[A-Z]{1,2}[ ][A-Z]{1,3}[ ][0-9]{1,4}",text)
        if match:
            #print('match: ' +match.string)
            self.feature = match.string
            self.kreis = districtDict[match.string.split(" ")[0]]
            return True
        else:
            return False

    def textRecognition(self):
        flag = False
        i=0 #debug
        for img in self.imageList:
            i = i + 1
            #cv2.imshow('get_blue' + str(i),img)
            cv2.imshow(self.path + str(len(img)) + 'pre findBlue', img)
            #img = self.get_blue(img)
            if img.size != 0 :
                img = self.convertToBaW(img, 70)              # Tobi?
                img = cv2.GaussianBlur(img, (3, 3), 200)
                #cv2.imshow(self.path + str(len(img)) + 'post findBlue', img)
            img_jpg = Image.fromarray(img)
            #print(tess.image_to_string(img_jpg))
            flag = self.platetext_format(tess.image_to_string(img_jpg))
            if flag == True:
                self.correctImage = img
                return True

        return False

    def get_text(self):
        print(self.path)
        flag = False
        while(flag == False):
            self.cut_image()
            flag = self.textRecognition()
            if flag == False:
                self.imageList = []
                self.feature = 'Nothing Found!'
            break
        return self.feature

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

    def convertToBaW(self, img, threshold):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        for n in range(0, np.shape(img)[0]):
            for m in range(0, np.shape(img)[1]):
                if img[n][m] > threshold:
                    img[n][m] = 255                 # alle Pixel oberhalb des threshold werden weiß
        return img






