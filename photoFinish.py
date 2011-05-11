from subprocess import call
from os.path import exists, expanduser
from os import mkdir, remove
from PIL import Image
import glob
import logging
import sys


def main(imageDir, movieFile):
    panoName = "pano.jpg"
    imageDir = expanduser(imageDir) # expand ~username
    movieFile = expanduser(movieFile)
    frameBreaker(movieFile, imageDir)
    combineImages(imageDir, panoName)

def frameBreaker(movieFileName, imageDir):
    """Break down movie into images
    
    args:
        movieFileName: path to the movie
        imageDir: directory which will hold the frames extracted from the 
            movie
    """
    # SHOULD THIS BE DONE IN A SHELL SCRIPT?
    createImages = False

    # if the dir exists, ask if we should just use the existing images
    if exists(imageDir):
        yn = raw_input("Would you prefer to keep and use existing images? (Y/N)\n-->")
        if yn == "N":
            logger.info("blowing away images")
            for image in glob.iglob(imageDir + "*.jpg"):
                remove(image)
            createImages = True
    else:
        logger.info("creating " + imageDir)
        mkdir(imageDir)
        createImages = True

    if createImages:
        logger.info("creating images from movie!")
        call(["ffmpeg", "-i", movieFileName, "-r", "1", "-f", "image2", imageDir + "foo-%03d.jpg", "-vframes", "10"])


def combineImages(imageDir, panoName):
    """Combines multiple images into one.

    Take vertical box of pixels from each frame, and place them sequentially
    moving to the right in the photofinish image.

    Args: 
        imageDir: path to the directory which is storing images
        panoName: filename (including extension) of the output image
    """

    # need to figure out number of images, so we can create the pano image
    # to the right size
    imagePaths = glob.glob(imageDir + "*.jpg")
    numImages = len(imagePaths)

    if numImages == 0:
        print "No images in", imageDir
        return

    # create pano image
    im = Image.open(imagePaths[0])
    x_size, y_size = im.size
    panoImg = Image.new(im.mode, (numImages, y_size))

    x_offset = 0
    box = (0, 0, 1, y_size)
    for imagePath in imagePaths:
        # grab vertical set of pixels
        im = Image.open(imagePath)
        slit = im.crop(box)

        # paste in pano image, incrementing the x_offset as we go
        panoImg.paste(slit, (x_offset, 0, x_offset + 1, y_size))
        x_offset += 1
    panoImg.save(panoName, "JPEG")

if __name__ == "__main__":
    # set logger
    logger = logging.getLogger("VideoGraph")
    logging.basicConfig(level = logging.INFO)

    # check if the right number of variables are passed in
    if 3 != len(sys.argv):
        print "photofinish should be called in the following way:"
        print "photofinish.py [videoName] [outputDir]"
        sys.exit(2)

    main(sys.argv[2], sys.argv[1])
