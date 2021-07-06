import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob

cars = []
badCars = []
for path in glob.glob("pictures/*.*"):
    cars.append(ILP(path, showDebug=True))

for car in cars:
    print("--------------------------------------Bearbeite jetzt: " + car.name + "\n")
    print("Das Kennzeichen ist: " + car.name + ' ' + car.getLicenseplateString())
    if len(car.district) > 0:
        print("Das Auto kommt aus: " + car.district)
    if car.feature == 'Nothing Found!':
        badCars.append(car)


print(str(len(badCars)/len(cars)*100) +"% ist die Fehlerquote ")




cv2.waitKey(0)
cv2.destroyAllWindows()