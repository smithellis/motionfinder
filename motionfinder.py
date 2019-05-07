# import the necessary packages
from imutils.video import FileVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os

# Set up our stuff

# Default motion threshold
sdThresh = 20

# A list of files that have motion
withmotion = []

# Flag for if a video has motion
moves = False

# Tuple of video extensions
ftypes = ('.m1v', '.mpeg', '.mov', '.qt', '.mpa', '.mpg', '.mpe', '.avi', '.movie', '.mp4')

# Calculates the pythagorean distance between two frames
def distMap(frame1, frame2):
    """outputs pythagorean distance between two frames"""
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:,:,0]**2 + diff32[:,:,1]**2 + diff32[:,:,2]**2)/np.sqrt(255**2 + 255**2 + 255**2)
    dist = np.uint8(norm32*255)
    return dist

# Capture our arguments
# Only "-d" and "-q" are required
ap = argparse.ArgumentParser()
# Directory to scan
ap.add_argument("-d", "--directory", required=True,
	help="Directory of your video files")
# Movement threshold
ap.add_argument("-t", "--threshold", required=False,
	help="Movement threshold")
# Queue size
ap.add_argument("-q", "--qsize", required=True,
	help="Queue size")
# Verbosity of the commandline output
ap.add_argument("-v", "--verbose", required=False,
	help="Verbosity")
args = vars(ap.parse_args())

# Simplify args into variables for no reason
path = args['directory']
queue = int(args['qsize'])
thresh = args['threshold']

# Scan the directory and get only files that end in a
# video extension
movies = [f for f in os.listdir(path)
	if os.path.isfile(os.path.join(path, f))
	and f.lower().endswith(ftypes)]

# Iterate over each movie we found and take action
for item in movies:
	print("[INFO] starting video file thread for {}".format(item))
    # Use the FileVideoStream object from imutils to open the file
    # This has a queue system set up, so it speeds the read up
	fvs = FileVideoStream(path+item,queue_size=queue).start()
	time.sleep(1.0)
    # Start a frame counter
	fps = FPS().start()

    # Grab two frames at the start of the video and resize them
	frame1 = fvs.read()
	frame1 = imutils.resize(frame1, width=450)
	frame2 = fvs.read()
	frame2 = imutils.resize(frame2, width=450)

    # Start moving through frames
	while fvs.more():
		frame3 = fvs.read()
        # If we are out of frames, fail violently
		if frame3 is None:
			break
        # Grab a third frame and resize it
		frame3 = imutils.resize(frame3, width=450)
        # Compare frames
		dist = distMap(frame1, frame3)
        # Shuffle frames down the stack like an intellectual baby
		frame1 = frame2
		frame2 = frame3
        #
		mod = cv2.GaussianBlur(dist, (9,9), 0)
		_, thresh = cv2.threshold(mod, 100, 255, 0)
		_, stDev = cv2.meanStdDev(mod)
        # I'd like to tell you *when* in the video we saw motion
        # But it ain't done yet
		tstamp = "comingsoon"
        # If you want frame data, here ya go
		if args['verbose']:
			print("stdev: {} and sdthresh: {} AT {}".format(stDev,sdThresh,tstamp))
        # If the standard deviation is greater than our defined threshold
        # let's say this video has motion.
        # Bonus: say it every frame that moves if you have decided to be verbose
		if stDev > sdThresh:
			if args['verbose']:
				print("Motion detected.. Do something!!!");
			moves = True
        # Wait a millisecond and see if there is a key press
		if cv2.waitKey(1) & 0xFF == 27:
			break
        # Update the frame count
		fps.update()
    # If there is motion int he file, add the file to our list
	if moves == True:
		withmotion.append(item)
		moves = False
    # Stop the frame counter
	fps.stop()
	print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    # If we'd had windows, we'd kill em.
    # Let's stop the read as well
	cv2.destroyAllWindows()
	fvs.stop()

# Output the glorious answer
print("\n**************\n")
print("Scanned these files:")
for item in movies:
	print(item)
print("\n**************\n")
print("These items had motion:")
for item in withmotion:
	print(item)
