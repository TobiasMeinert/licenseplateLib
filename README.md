# Introduction
This university project is an introduction to working with python and image editing. Especially working with libraries, classes and openCV. 
The documentation should be really beginner-friendly and will also contain workflows, and a guide how to set up the project.

The licenseplatelib.py contains the class IdentifyLicensePlate which takes a path to an image. If it detects a licenseplate, and the text is matching the (at the moment) german format. The getLicenseplatestring method will return the licenseplate as String.

# Dependencies
Before working with this code you need to install some libraries. You can either use feature from your IDE (if you use one) else here is a [how to install python libaries].

## Following libraries are needed:
| libary            | documentation  |
|------------       |----------------|
| cv2               | [cv2 documentation](https://pypi.org/project/opencv-python/)  |
| Pillow            | [Pillow documentation](https://pillow.readthedocs.io/en/stable/)  | 
| Tesseract-OCR     | [Tesseract documentation](https://pypi.org/project/pytesseract/) |
| NumPy             | [Numpy documentation](https://numpy.org/doc/stable/)
| Imutils           | [Imutils documentation](https://pypi.org/project/imutils/)

# Attributes and methods of the class

The IdentifyLicensePlate has following attributes and methods:
    ![Flowchart IdentifyLicensePlate](/documentation/identifyLicenseplate.png)

rawImage and name are set after initiating an Object. The rawImage holds the image from the path loaded with cv2.imread. The name is generated from the path but the /pictures/ and the suffix are cut.
The Attributes feature and district are being set after getLicenseplate has successfully run.

getlicenseplateString() is the method which is getting for starting the identifying process. All other methods are only used internally. For further explanation look at the Flowcharts below.

# Flowcharts
Following the process of getting the licenseplate as string from the original image is explained with flowcharts. For best understanding of the code, try to follow the flowchart inside the code.

The main method from the IdentifyLicensePlate is [getLicenseplateString](https://github.com/meiTob/Kennzeichenerkennung/blob/b9627e55419c2de57726a856b065093ed5adde60/licenseplatelib.py#L40). The method is called in the main script to get the feature. It starts the image processing as well as the text recognition.
    ![Flowchart getlicenseplateString](/documentation/getLicenseplateString.png)

To understand the image processing more in depth we are looking at the [findAndCropLicensePlate](https://github.com/meiTob/Kennzeichenerkennung/blob/b9627e55419c2de57726a856b065093ed5adde60/licenseplatelib.py#L73). This method searches in the original image for a licenseplate and cuts the suspected part of the image out. It returns a list with all cutted images. Note: The method will cut wrong images also. The text detection will filter them out. As long as the licenseplate is in the imagelist it is working.
    ![Flowchart findAndCropLicensePlate_1](/documentation/findAndCropLicensePlate_1.png)
    ![Flowchart findAndCropLicensePlate_2](/documentation/findAndCropLicensePlate_2.png)

The returned imagelist is thrown into the text detection (explained later). If the text detection is not able to identify a licenseplate the [originalImgEdgeDetection](https://github.com/meiTob/Kennzeichenerkennung/blob/b9627e55419c2de57726a856b065093ed5adde60/licenseplatelib.py#L174) is used instead. This method takes the original image put some filter for edge detection on it. The image is then thrown into the text detection and we hope for the best.
    ![Flowchart originalImgEdgeDetection.ong](/documentation/originalImgEdgeDetection.png)

The [validateFormate](https://github.com/meiTob/Kennzeichenerkennung/blob/b9627e55419c2de57726a856b065093ed5adde60/licenseplatelib.py#L114)-method  works with the python inbuild [regrex libary](https://docs.python.org/3/library/re.html). It mainly filters non letters and numbers out of the string, and then compares the resulting string with a pattern for german licenseplates. The following flowchart doesn't use the real code lines. Instead, the comments are being used, as they are more understable.
    ![Flowchart validateFormat](/documentation/validateFormat.png)

# Using the class
In the main.py script is an example, how to use the class.

The class is imported as ILP. That means we can use ILP instead of licenseplatelib.IdentifyLicenseplate in the following code:
```
from licenseplatelib import IdentifyLicensePlate as ILP
``` 

We initiate an Object with:
The showDebug option is going to print information about the image editing process to understand it, or look why the class is not able to identify a licenseplate.
The showImages option will show multiple images of different steps from the image editing process.

```
exampleCar = ILP("examplePictures/examplecar.jpg", showImages=True, showDebug=True)
```

the method call ```.getLicenseplateString``` is going to start the identifying process. It returns the feature as string and will be printed into the terminal.

```
print("The Feature from: " + exampleCar.name + ' is ' + exampleCar.getLicenseplateString()) 
``` 
The if statement checks if the district is set, then the district is printed:
```
if len(exampleCar.district) > 0:
    print("The Car comes from: " + exampleCar.district)
```


glob.glob is creating a list with all images in the directory pictures. The for loop iterates through that list and initiates a object for every image and saves them into the cars list.
```
cars = []
for path in glob.glob("pictures/*.*"):
    cars.append(ILP(path, showDebug=True))
```

For being able to show the pictures the following two line of code are needed in every script using the IdentifyLicenseplate class with "showImages = True":
```
cv2.waitKey(0)
cv2.destroyAllWindows()
```