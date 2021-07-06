import cv2
# Bild lesen
rawImage = cv2.imread("pictures/volvo.jpeg")

 # Gaußsche Unschärfe, Bild glätten, Störgeräusche entfernen
image = cv2.GaussianBlur(rawImage, (3, 3), 1)


 # Bild Graustufen
image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

 # Sobel-Operator (X-Richtung)
Sobel_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
# Sobel_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)
absX = cv2.convertScaleAbs (Sobel_x) # Zurückkonvertieren in uint8 Die Funktion convertScaleAbs ist eine Funktion zur Konvertierung der Bittiefe, mit der alle Arten von Daten in CV_8UC1 konvertiert werden können
# absY = cv2.convertScaleAbs(Sobel_y)
# dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
image = absX



 # Binarisierung: Bei der Binärisierung des Bildes wird der Grauwert der Pixel im Bild auf 0 oder 255 gesetzt, und das Bild wird nur in Schwarzweiß angezeigt.
ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)


 # Schließvorgang: Durch den Schließvorgang kann der Zielbereich zu einem Ganzen verbunden werden, was für die nachfolgende Konturextraktion praktisch ist.
kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 10))
image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernelX)



 # Expansionskorrosion (morphologische Behandlung)
kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 25))
image = cv2.dilate(image, kernelX)
image = cv2.erode(image, kernelX)
image = cv2.erode(image, kernelY)
image = cv2.dilate(image, kernelY)



 # Glätten, Medianfilterung
# image = cv2.medianBlur(image, 15)
image = cv2.GaussianBlur(image,(15,1),1)
# cv2.imshow("...2.", image)



 # Kontur finden
contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for item in contours:
    rect = cv2.boundingRect(item)
    x = rect[0]
    y = rect[1]
    weight = rect[2]
    height = rect[3]
    if weight > (height * 2):
                 # Schnittflächenbild
        chepai = rawImage[y:y + height, x:x + weight]
        cv2.imshow('chepai' + str(x), chepai)

 # Umriss zeichnen
image = cv2.drawContours(rawImage, contours, -1, (0, 0, 255), 3)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()