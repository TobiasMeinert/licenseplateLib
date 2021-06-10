from licenseplatelib import IdentifyLicensePlate as ILP
import cv2
import glob

cars = []
badCars = []

for path in glob.glob("Bilder/*.*"):
    cars.append(ILP(path))

for car in cars:
    print("Das Kennzeichen von " + car.name + " ist: " + car.get_text())
    if car.get_text() == 'Nothing Found!':
        badCars.append(car)

sBadCar = "Bad Cars are: "
for car in badCars:
    sBadCar = sBadCar + " " + car.name

print(sBadCar)
for car in badCars:
    if len(car.imageList) > 0:
        i = 0
        for img in car.imageList:
            cv2.imshow(car.name + str(i), img)
    else:
        print(car.name + ": Kein Bild Zugeschnitten")


print(str(len(badCars)/len(cars)*100) +"% ist die Fehlerquote ")

cv2.waitKey(0)
cv2.destroyAllWindows()