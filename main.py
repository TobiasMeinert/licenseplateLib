import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob

cars = []

for path in glob.glob("Bilder/*.*"):
    cars.append(ILP(path))

for car in cars:
    print("Das Kennzeichen ist: " + car.name + ' ' + car.get_text())
    if len(car.district) > 0:
        print("Das Auto kommt aus: " + car.district)





cv2.waitKey(0)
cv2.destroyAllWindows()