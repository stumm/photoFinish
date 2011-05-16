from subprocess import call
from os.path import exists, expanduser
from os import mkdir, remove
from PIL import Image
import glob
import logging
import sys


def main(imageDir, movieFile=None):
    panoName = "pano.jpg"
    imageDir = expanduser(imageDir) # expand ~username

    # movieFile is optional, so you can use any images you'd like
    if movieFile is not None:
        movieFile = expanduser(movieFile)
        frameBreaker(movieFile, imageDir)

    combineImages(imageDir, panoName, True)

def frameBreaker(movieFileName, imageDir):
    """Break down movie into images
    
    args:
        movieFileName: path to the movie
        imageDir: directory which will hold the frames extracted from the 
            movie
    """
    createImages = True

    # if the dir exists, ask if we should just use the existing images
    if exists(imageDir):
        yn = raw_input("Would you prefer to keep and use existing images? (Y/N)\n-->")
        if yn == "N":
            logger.info("blowing away images")
            for image in glob.iglob(imageDir + "*.jpg"):
                remove(image)
        else:
            createImages = False
    else:
        logger.info("creating " + imageDir)
        mkdir(imageDir)

    if createImages:
        logger.info("creating images from movie!")
        call(["ffmpeg", "-i", movieFileName, "-re", "-f", "image2", imageDir + "foo-%04d.jpg"]) 


def combineImages(imageDir, panoName, rotate=False):
    """Combines multiple images into one.

    Take vertical box of pixels from each frame, and place them sequentially
    moving to the right in the photofinish image.

    Args: 
        imageDir: path to the directory which is storing images
        panoName: filename (including extension) of the output image
    """

    # number of images will be used to set the size of the image
    imagePaths = glob.glob(imageDir + "*.jpg")
    numImages = len(imagePaths)

    if numImages == 0:
        print "No images in", imageDir
        return

    # create pano image
    im = Image.open(imagePaths[0])
    x_size, y_size = im.size
    if rotate:
        panoImg = Image.new(im.mode, (x_size, numImages))
        box = (0, 0, x_size, 1)
    else:
        panoImg = Image.new(im.mode, (numImages, y_size))
        box = (0, 0, 1, y_size)

    offset = 0
    for imagePath in imagePaths:
        # grab sliver of pixels
        im = Image.open(imagePath)
        slit = im.crop(box)

        # paste in pano image, incrementing the offset as we go
        if rotate:
            panoImg.paste(slit, (0, offset, x_size, offset + 1))
        else:
            panoImg.paste(slit, (offset, 0, offset + 1, y_size))
        offset += 1

    if rotate:
        panoImg = panoImg.rotate(270)

    panoImg.save(panoName, "JPEG")

if __name__ == "__main__":
    # set logger
    logger = logging.getLogger("VideoGraph")
    logging.basicConfig(level = logging.INFO)

    # check if the right number of variables are passed in
    if 3 != len(sys.argv):
        print "photofinish should be called in the following way:"
        print "photofinish.py [outputDir] [videoName]"
        sys.exit(2)

    main(sys.argv[1], sys.argv[2])
