import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob

cars = []

for path in glob.glob("Bilder/*.*"):
    cars.append(ILP(path))

for car in cars:
    #print(car.name)
    print(car.get_text())
#print(janIstSoToll.path + janIstSoToll.get_text())
#print(vwAuschnitt.path + vwAuschnitt.get_text())



cv2.waitKey(0)
cv2.destroyAllWindows()