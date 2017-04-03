from PIL import Image
import pytesseract
import os


#import images from folder trees, the image and their answers will be stored in memory.
#this should speed up the tesseract process quite a bit until nb of images becomes too big
#try to dump all image in the same dir (./ocrSpeed/) with the following format
# tess-area-nextAvailableFileName.png
# separate dict with areas, ex: dic['stack1'] will return a dict { tess : list(img) }


class ocrSpeed:

    #use this img class to give pertinent info about said img

    class Img:

        im = ''
        size = [0,0]
        pix = ''
        tess = ''
        area = ''
        path = ''

        def __init__(self,im = '',size = [0,0], pix = '', tess = '', area='', path = ''):
            self.im = im
            self.size = size
            self.pix = pix
            self.tess = tess
            self.area = area
            self.path = path

    count= 0
    loadedOCR = {}
    path = ''


    def __init__(self,path, fullCheck = False):
        #load every file from the path and enter them in a dictionnary {img:tess}
        self.path = path
        self.loadImgs()


    #tess an image and save it to the path folder, can use an area if we need
    def makeImgTess(self, im, area=None,config = None, datatype=None):
        tess = self.getTess(im, config, datatype)
        filename = self.findNextAvailableFilename(self.path, tess+'-'+area)
        im.save(self.path+filename)

        if area not in self.loadedOCR.keys():
            self.loadedOCR[area] = []

        imClass = self.Img(pix=im.load(), area = area, tess=tess, size=im.size)
        self.loadedOCR[area].append(imClass)

    def addToloadedOCR(self, im, tess, area):
        if area not in self.loadedOCR.keys():
            self.loadedOCR[area] = []

        imClass = self.Img(pix=im.load(), size=im.size, tess = tess, area = area)
        self.loadedOCR[area].append(imClass)

    #add an image with tess - area - num .png and add it to loadedOCR
    def addToDir(self,im,tess, area):
        #filename = self.findNextAvailableFilename(self.path, tess + '-' + area)
        #im.save(self.path + filename)
        #self.addToloadedOCR(im, tess, area)

        try:
            filename = self.findNextAvailableFilename(self.path, str(tess) + '-' + area)
            im.save(self.path + filename)
            self.addToloadedOCR(im,tess,area)
        except:
            filename = self.findNextAvailableFilename(self.path,  'ERROR'+ '-' + area)
            im.save(self.path + filename)
            print 'ERROR', tess, type(tess), area, self.path + filename

    # check can be full or fast, var is for fast and default is 5
    #if save==True, it will try to do a Tess with no config
    #if save==False it will not get a default tess or add to the loadedOCR, this can be used if we know
    #special config are to be used to get a valid OCR answer
    def checkIfTessExist(self,im, check, var=4, area='', save=True):
        if check == 'fast':
            loadedTess = self.fastCheck(im,area,var)
        else:
            loadedTess = self.fullCheck(im,area)

        #print 'loadedtess', loadedTess
        if loadedTess == None:
            #print 'not found in loadedOCR'
            if save==False:
                return None
            tess = self.getTess(im) #a changer pour fnc ou je peux faire un dic avec area et config
            self.addToDir(im,tess,area)
            return tess
        else:
            pass
            #print 'found in loadedOCR'

        return loadedTess

    #compare only a nb of line to speed up the process, all line are
    def fastCheck(self,im,area, nbline = 4):
        pass

    #does a full check line by line to make sure we have the same img
    def fullCheck(self,im, area):

        width, height = im.size
        if width == 0 or height == 0:
            #print 'full check image res = 0'
            return None

        if area not in self.loadedOCR.keys():
            self.loadedOCR[area] = []
        for imgClass in self.loadedOCR[area]:

            if (width, height) != imgClass.size:
                continue

            if self.isSameImg(im.load(),im.size,imgClass.pix,imgClass.size) == True:
                #print 'found img', area, imgClass.tess
                return imgClass.tess

        return None

    def createDir(self,directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


    #find next available name for png file
    def findNextAvailableFilename(self,path,name=''):
        cur = self.getAllFromDir(path)

        for x in range(0,100000):
            filename = name+'-'+str(x)+'.png'
            if filename not in cur:
                return filename
        return None


    def getAllFromDir(self,path):
        return os.listdir(path)

    #load up all images from path dir into the main dic
    def loadImgs(self):
        imgs = self.getAllFromDir(self.path)
        count = 0
        for img1 in imgs:

            info = img1.split('-')

            if info[0] == '':
                print img1, 'has no tess data, please fix this'
            if info[1] not in self.loadedOCR.keys():
                self.loadedOCR[info[1]] = []

            im = Image.open(self.path+img1)

            imClass = self.Img(tess=info[0], area=info[1], pix=im.load(), size=im.size)

            test = False
            #print len(self.loadedOCR[info[1]][info[0]])
            for img2 in self.loadedOCR[info[1]]:

                if self.isSameImg(img2.pix, img2.size, imClass.pix, imClass.size) == True:

                    test = True

            if test == False:

                self.count = self.count + 1
                self.loadedOCR[info[1]].append(imClass)
        #print self.loadedOCR
        print self.count , 'images pre loaded'


    def isSameColor(self,pix1, pix2, var=15):

        if not(pix1[0] + var > pix2[0] and pix1[0] - var < pix2[0]):
            return False
        if not(pix1[1] + var > pix2[1] and pix1[1] - var < pix2[1]):
            return False
        if not(pix1[2] + var > pix2[2] and pix1[2] - var < pix2[2]):
            return False

        return True

    def isSameImg(self,pix1,pix1size, pix2, pix2size, var=0):

        if pix1size != pix2size:
            return False

        if pix1size[0] == 0:
            print 'isSameAction len areas == 0'
            return False
        if pix1size[1] == 0:
            print 'isSameAction len areas == 0'
            return False

        x,y = pix1size

        for i in range(0, x):
            for n in range(0, y):

                if self.isSameColor(pix1[i,n], pix2[i,n]) == False:
                    return False
        return True


    def getTess(self,img, config=None, datatype=None):
        if datatype == 'card1':
            return pytesseract.image_to_string(img, config='-c tessedit_char_whitelist=mOA2345678LO9JQK -psm 6')


        if datatype == 'num':
            tess = pytesseract.image_to_string(img, config='-c tessedit_char_whitelist=0123456789., -psm 6')
            return tess.replace(',','').replace('.','')
            #return pytesseract.image_to_string(img, config='-psm 6')
        if config:

            return pytesseract.image_to_string(img, config=config)
        return pytesseract.image_to_string(img)


