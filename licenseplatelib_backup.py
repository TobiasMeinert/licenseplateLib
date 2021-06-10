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
        imageBlur = cv2.GaussianBlur(self.rawImage, (3, 3), 1)  # Bild glätten
        #cv2.imshow('imageBlur', imageBlur)
        imageGrey = cv2.cvtColor(imageBlur, cv2.COLOR_RGB2GRAY)  # zu Grau (1-Dimensionale Pixel) konvertieren
        edged = cv2.Canny(imageGrey, 30, 200)
        #cv2.imshow('Kanten', edged)
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
            mask = np.zeros(imageGrey.shape, np.uint8)
            new_image = cv2.drawContours(mask, [count], 0, 255, -1, )
            cv2.imshow('mit Linien', new_image)
            new_image = cv2.bitwise_and(self.rawImage, self.rawImage, mask=mask)
            cv2.imshow('mit Cut'+ str(i),new_image)
            i = i +1

        #Sobel_x = cv2.Sobel(imageGrey, cv2.CV_16S, 1, 0)  # sobel operation in x-richtung (ableitung der Helligkeit)
        #absX = cv2.convertScaleAbs(Sobel_x)  # Betrag der Ableitung
        #ret, imageBaW = cv2.threshold(absX, 0, 255, 8)  # Binäres Schwarz-Weiß-Bild erstellen
        '''for n in range(0, np.shape(edged)[0]):
            for m in range(0, np.shape(edged)[1]):
                if edged[n][m] > 200:
                    edged[n][m] = 255
                else:
                    edged[n][m] = 0'''
        #cv2.imshow('absXGreyed', edged)
        #cv2.imshow('imageBaW', imageBaW)

        kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (self.parameter[MorphX], self.parameter[MorphY]))  #Erstellt ein Rechteck welches er als nutzt um mit morph Flächen einer Helligkeit zu finden
        imageMorph = cv2.morphologyEx(edged ,cv2.MORPH_CLOSE, kernelX)
        #cv2.imshow('imageMorph', imageMorph)
        kernelX = cv2.getStructuringElement(cv2.MORPH_RECT,(self.parameter[DilateErodeX_X], self.parameter[DilateErodeX_X]))
        kernelY = cv2.getStructuringElement(cv2.MORPH_RECT,(self.parameter[DilateErodeY_X], self.parameter[DilateErodeY_X]))
        imageDilateX = cv2.dilate(imageMorph, kernelX)
        imageErodeX = cv2.erode(imageDilateX, kernelX)
        imageDilateY = cv2.erode(imageErodeX, kernelY)
        imageErodeY = cv2.dilate(imageDilateY, kernelY)
        #cv2.imshow('Eroded', imageErodeY)

        imageBlurredAgain = cv2.GaussianBlur(imageErodeY, (15, 1), 1)

        contours, _ = cv2.findContours(imageBlurredAgain, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for item in contours:
            rect = cv2.boundingRect(item)
            x = rect[0]
            y = rect[1]
            weight = rect[2]
            height = rect[3]
            if weight > (height * self.parameter[FactorWeightToHeight]):
                # Schnittflächenbild
                chepai = self.rawImage[y:y + height, x:x + weight]

                self.imageList.append(self.rawImage[y:y + height, x:x + weight])
                #cv2.imshow(str(y),self.rawImage[y:y + height, x:x + weight])
                print('cutImage hat ein Bild ausgeschnitten')
            else:
                print('cutImage hat kein passendes Bild gefunden')

    def change_parameter(self, parameter, amount):
        self.parameter[parameter] += amount

    def set_parameter(self, parameter, value):
        self.parameter[parameter] = value

    def platetext_format(self, text):

        match = re.match(r"[A-Z]{2,5}[0-9]{1,4}|[A-Z]{1,2}[ ][A-Z]{1,3}[ ][0-9]{1,4}",text)
        #print(text)
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

            img = self.get_blue(img)
            i = i + 1
            #cv2.imshow('get_blue' + str(i),img)
            if img.size != 0 :
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                for n in range(0, np.shape(img)[0]):
                    for m in range(0, np.shape(img)[1]):
                        if img[n][m] > 70:
                            img[n][m] = 255
                img = cv2.GaussianBlur(img, (3, 3), 200)
                cv2.imshow('text' + str(len(img)), img)
                img_jpg = Image.fromarray(img)
                #print(tess.image_to_string(img_jpg))
                flag = self.platetext_format(tess.image_to_string(img_jpg))
                if flag == True:
                    self.correctImage = img
                    return True

        return False

    def get_text(self):
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
        cv2.imshow("pimmel",image)
        imgBlue = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        print(type(imgBlue))

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
            '''print('shape: ' + str(np.shape(imgBlue)))
            print('x: ' + str(x))
            print('y: ' + str(y))
            print('w: ' + str(w))
            print('h:  ' + str(h))
            print('w max ' + str(x + int( h * (520 / 110))- w))
            print( 'Ausschnitt: y  ' + str(y) + ' '+ str(y+h) + 'x: '+ str(x+w) + ' '+ str(int(x + h * (520 / 110) - w)))'''
            if x + w < int(x + h * (520 / 110) - w):
                return cv2.cvtColor(imgBlue[y:y + h, x + w:int(x + h * (520 / 110) - w)], cv2.COLOR_HSV2BGR)
            else:
                return np.empty(0)
        else:
            return np.empty(0)
        #print(np.shape(imgBlue)[0] * np.shape(imgBlue)[1])
        #print('x: ' + str(x) + ' y: ' + str(y) + 'dimension: ' + str(np.shape(imgBlue)))
        #self.imgCountry = cv2.cvtColor(imgBlue[y:y+h,x:x+w], cv2.COLOR_HSV2BGR)








