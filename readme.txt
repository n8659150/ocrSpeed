

Speed up OCR process if there are similar images that comes back often, it make a directory of images with the detected name ( tess ) + a classification name if we have more than one kind of area to scan from ( area ) + nb item with the same tess+area

ex: 

we have an image with the number 380 in an area we call bottomleft

an image will be saved as 380-bottomleft-0.png


As we load up the class in import with:

import ocrSpeed

ocr = ocrSpeed(path-of-imgs-dir)

it will auto load up in memory the image we already have a tess scan on, if it detect the same image, instead of using the python tesseract ( which can be somewhat slow) it will load up the tesseract name directly from memory.