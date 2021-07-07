# Introduction
This university project is an introduction to working with python and image editing. Especially working with libraries, classes and openCV. 
The documentation should be really beginner-friendly and will also contain workflows, and a guide how to set up the project.

The licenseplatelib.py contains the class IdentifyLicensePlate which takes a path to an image. If it detects a licenseplate, and the text is matching the (at the moment) german format. The getLicenseplatestring method will return the licenseplate as String.

# Dependencies
Before working with this code you need to install some libraries. You can either use feature from your IDE (if you use one) else here is a [how to install python libaries].

## Following libraries are needed:
| libary            | documentation  |
|------------       |----------------|
| cv2               | [cv2 documentation](https://docs.opencv.org/4.5.2/d6/d00/tutorial_py_root.html)  |
| Pillow            | [Pillow documentation](https://pillow.readthedocs.io/en/stable/)  | 
| Tesseract-OCR     | [Tesseract documentation](https://pypi.org/project/pytesseract/) |
| NumPy             |[Numpy documentation](https://numpy.org/doc/stable/)
| Imutils           |[Imutils documentation](https://pypi.org/project/imutils/)

# Flowcharts
The main method from the IdentifyLicensePlate is getLicenseplateString. This method starts the image processing as well as the text detection. The logic of the function is presented in following graphic.
    ![Flowcharts getlicenseplateString](/documentation/getLicenseplateString.png)
