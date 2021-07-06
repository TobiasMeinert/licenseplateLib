import licenseplatelib as lpl
from licenseplatelib import IdentifyLicensePlate as ILP
import cv2


tobiasBack = ILP("pictures/tobias_back_bearbeitet.jpeg", showImages= False, showDebug= False)               #Call the IdentifyLicensePlate class. As attributes it takes the path of the image and the debug enable for images and text
tobiasFront = ILP("pictures/tobias_front.jpeg", False, False)
print("==============Das Kennzeichen wurde Identifiziert als: " + tobiasBack.getLicenseplateString() + "=======================")
print("==============Das Kennzeichen wurde Identifiziert als: " + tobiasFront.getLicenseplateString()+ "=======================")
print("the car " + tobiasBack.name + "comes from: " + tobiasBack.district)
print("the car " + tobiasFront.name + "comes from: " + tobiasFront.district)

cv2.waitKey(0)                              #Just one image at a time
cv2.destroyAllWindows()                     #when terminated close all display windows



