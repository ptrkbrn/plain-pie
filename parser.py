import sys
import os
import cv2
from pysubparser import parser
from pysubparser.cleaners import brackets

try:
    path = sys.argv[1]
    # parse through each file in specfied directory
    for file in os.listdir(path):
        ext = os.path.splitext(file)[1]
        filepath = os.path.join(path, file)
        # if subtitle file
        if ext == '.srt':
            subtitles = brackets.clean(
                parser.parse(filepath)
            )
            for subtitle in subtitles:
                print(subtitle.start)
                print(subtitle.end)
                print(subtitle.text)
        # if video file
        elif ext == '.mp4':
            # reads video file
            cam = cv2.VideoCapture(filepath)
            # creates array of timestamps
            timestamps = [cam.get(cv2.CAP_PROP_POS_MSEC)]
            try:
                # creates directory for video frames
                if not os.path.exists(os.path.join(path, 'data')):
                    os.makedirs('data')
            # if directory is not created, throw error
            except OSError:
                print("Error: Could not create directory")

            # frame
            currentframe = 0

            while(True):
                # read data from frame
                ret, frame = cam.read()

                if ret:
                    # if video runtime still left, continue creating frames
                    name = './data/frame' + str(currentframe) + '.jpg'
                    print('Creating... ' + name)
                    # adds current timestamp to array
                    timestamps.append(cam.get(cv2.CAP_PROP_POS_MSEC))
                    print(timestamps[currentframe] / 1000)
                    #write extracted frames
                    cv2.imwrite(name, frame)

                    # increment counter to update frame count
                    currentframe += 1
                else:
                    break
            
            # Release space and windows once done
            cam.release()
            cv2.destroyAllWindows()

        # if not supported file type
        else:
            print('Not a valid file type')
except:
    print('Not a valid directory')


