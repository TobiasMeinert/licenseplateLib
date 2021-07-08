import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob

cars = []
badCars = []
exampleCar = ILP("pictures/examplecar.jpg", showImages=True, showDebug=True)
print("The Feature from: " + exampleCar.name + ' is ' + exampleCar.getLicenseplateString())
if len(exampleCar.district) > 0:
    print("The Car comes from: " + exampleCar.district)


cars = []
for path in glob.glob("pictures/*.*"):
    cars.append(ILP(path, showDebug=True))

for car in cars:
    print("The Feature from: " + car.name + ' is ' + car.getLicenseplateString())
    if len(car.district) > 0:
        print("The Car comes from: " + car.district)
    if car.feature == 'Nothing Found!':
        badCars.append(car)






cv2.waitKey(0)
cv2.destroyAllWindows()