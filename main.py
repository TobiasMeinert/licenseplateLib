import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob
tFront = ILP("Bilder/tobias_front.jpeg")
tBack = ILP("Bilder/tobias_back.jpeg")
audiTim = ILP("Bilder/audi_tim.jpeg")
vw_tim = ILP("Bilder/vw_tim.jpeg")
janIstSoToll = ILP("Bilder/jansAchSoTollesBild.JPEG")
marokko = ILP("Bilder/marokkoTaxi.jpg")
vwAuschnitt = ILP("Bilder/ausschnitt207.jpg")


#print(tFront.get_text())
#print(janIstSoToll.path + janIstSoToll.get_text())
#print(vwAuschnitt.path + vwAuschnitt.get_text())



cv2.waitKey(0)
cv2.destroyAllWindows()