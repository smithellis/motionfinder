# import the necessary packages
from imutils.video import FileVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os

framenum = 0
sdThresh = 20
font = cv2.FONT_HERSHEY_SIMPLEX
withmotion = []
moves = False
ftypes = ('.m1v', '.mpeg', '.mov', '.qt', '.mpa', '.mpg', '.mpe', '.avi', '.movie', '.mp4')

def distMap(frame1, frame2):
    """outputs pythagorean distance between two frames"""
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:,:,0]**2 + diff32[:,:,1]**2 + diff32[:,:,2]**2)/np.sqrt(255**2 + 255**2 + 255**2)
    dist = np.uint8(norm32*255)
    return dist

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True,
	help="Directory of your video files")
ap.add_argument("-t", "--threshold", required=False,
	help="Movement threshold")
ap.add_argument("-q", "--qsize", required=True,
	help="Queue size")
ap.add_argument("-v", "--verbose", required=False,
	help="Verbosity")
args = vars(ap.parse_args())

path = args['directory']
queue = int(args['qsize'])
thresh = args['threshold']

movies = [f for f in os.listdir(path)
	if os.path.isfile(os.path.join(path, f))
	and f.lower().endswith(ftypes)]

for item in movies:
	print("[INFO] starting video file thread for {}".format(item))
	fvs = FileVideoStream(path+item,queue_size=queue).start()
	time.sleep(1.0)
	fps = FPS().start()
	frame1 = fvs.read()
	frame1 = imutils.resize(frame1, width=450)
	frame2 = fvs.read()
	frame2 = imutils.resize(frame2, width=450)

	while fvs.more():
		frame3 = fvs.read()
		if frame3 is None:
			break

		frame3 = imutils.resize(frame3, width=450)
		rows, cols, _ = np.shape(frame3)
		dist = distMap(frame1, frame3)
		frame1 = frame2
		frame2 = frame3
		mod = cv2.GaussianBlur(dist, (9,9), 0)
		_, thresh = cv2.threshold(mod, 100, 255, 0)
		_, stDev = cv2.meanStdDev(mod)
		tstamp = "comingsoon"
		if args['verbose']:
			print("stdev: {} and sdthresh: {} AT {}".format(stDev,sdThresh,tstamp))

		if stDev > sdThresh:
			if args['verbose']:
				print("Motion detected.. Do something!!!");
			moves = True

		if cv2.waitKey(1) & 0xFF == 27:
			break
		fps.update()

	if moves == True:
		withmotion.append(item)
		moves = False

	fps.stop()
	print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
	cv2.destroyAllWindows()
	fvs.stop()


print("Scanned these files:")
for item in movies:
	print(item)
print("\nThese items had motion:")
for item in withmotion:
	print(item)
