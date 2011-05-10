from subprocess import call
from os.path import exists, expanduser
from os import mkdir, remove
from PIL import Image
import glob, logging


def main(imageDir, movieFile):
    imageDir = expanduser(imageDir) # expand ~username
    movieFile = expanduser(movieFile)
    frameBreaker(movieFile, imageDir)
    combineImages(imageDir)

def frameBreaker(movieFileName, imageDir):
    """Break down movie into images"""
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
        # create images
        logger.info("creating images from movie!")
        call(["ffmpeg", "-i", movieFileName, "-r", "1", "-f", "image2", imageDir + "foo-%03d.jpg", "-vframes", "10"])


def combineImages(imageDir):
    # need to figure out number of images, so we can create the pano image
    # to the right size
    numImages = len(glob.glob(imageDir + "*.jpg"))

    # create pano image
    # this is stupid -> should just grab an image instead of creating iterator
    for imagePath in glob.iglob(imageDir + "*.jpg"):
        im = Image.open(imagePath)
        x_size, y_size = im.size
        break # all images should be the same size

    panoImg = Image.new(im.mode, (numImages, y_size))

    x_offset = 0
    box = (0, 0, 1, y_size)
    for imagePath in glob.iglob(imageDir + "*.jpg"):
        # grab vertical set of pixels
        im = Image.open(imagePath)
        slit = im.crop(box)

        # paste in pano image, incrementing the x_offset as we go
        panoImg.paste(slit, (x_offset, 0, x_offset + 1, y_size))
        x_offset += 1

    panoImg.save("test.jpg", "JPEG")

# input: movieFileName fileName
if __name__ == "__main__":
    # set logger
    logger = logging.getLogger("VideoGraph")
    logging.basicConfig(level = logging.INFO)

    main("~/Projects/videoGraph/temp/", "~/Movies/5129975364.mov")
