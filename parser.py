import sys
import os
import cv2
import base64
from datetime import datetime
from pysubparser import parser
from pysubparser.cleaners import brackets
from helpers import to_msec, upload_to_aws

import psycopg2
from config import config

def connect():
    # Connect to db server
    conn = None
    try:
        # read connection params
        params = config()

        # connect to Postgres server
        print('Connecting to PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL db server version
        db_version = cur.fetchone()
        print(db_version)

        try:
            path = sys.argv[1]
            # parse through each file in specfied directory
            for file in os.listdir(path):
                ext = os.path.splitext(file)[1]
                filepath = os.path.join(path, file)
                basename = os.path.basename(filepath)
                filename = os.path.splitext(basename)[0].upper()
                # if subtitle file
                if ext == '.srt':
                    subtitles = parser.parse(filepath)
                    for subtitle in subtitles:
                        sql = """INSERT INTO subtitles(text, episode, time_start, time_end)
                    VALUES(%s, %s, %s, %s);"""
                        print(to_msec(subtitle.start))
                        print(to_msec(subtitle.end))
                        print(subtitle.text)
                        print(sql, (subtitle.text, to_msec(subtitle.start), to_msec(subtitle.end),))
                        print(cur.execute(sql, (subtitle.text, filename, to_msec(subtitle.start), to_msec(subtitle.end),)))
                        conn.commit()
                # if video file
                elif ext == '.mkv':
                    # reads video file
                    cam = cv2.VideoCapture(filepath)
                    # creates array of timestamps
                    timestamps = [cam.get(cv2.CAP_PROP_POS_MSEC)]
                    # frame
                    currentframe = 0
                    lastgreymean = 0
                    # try:
                    #     # creates directory for video frames
                    #     if not os.path.exists(os.path.join(path, 'data')):
                    #         os.makedirs('data')
                    # # if directory is not created, throw error
                    # except OSError:
                    #     print("Error: Could not create directory")

                    while(True):
                        # read data from frame
                        ret, frame = cam.read()
                        if ret:
                            # if video runtime still left, continue creating frames
                            sql = """INSERT INTO screenshots(timestamp, episode, filename, url)
                            VALUES(%s, %s, %s, %s);"""
                            name = filename + '-' + str(currentframe) + '.jpg'
                            # adds current timestamp to array
                            timestamps.append(cam.get(cv2.CAP_PROP_POS_MSEC))
                            # print(timestamps[currentframe] / 1000)
                            #write extracted frames
                            # print(cv2.subtract(lastframe, frame))
                            # converts frame to greyscale
                            grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # reads mean value of greyscale image
                            grey_mean = cv2.mean(grey_frame)
                            # evaluates motion blur in each frame
                            if cv2.Laplacian(frame, cv2.CV_64F).var() > 60:
                                # if mean different enough, i.e. frame is unique enough, continue
                                difference = cv2.subtract(grey_mean, lastgreymean)
                                if difference[0][0] > .8 or difference[0][0] < -.8:
                                    print('Creating... ' + name)
                                    # increment last meme with current frame
                                    lastgreymean = cv2.mean(grey_frame)
                                    # encode image as string and add to db
                                    image_string = cv2.imencode('.jpg', frame)[1].tobytes()
                                    upload_to_aws(image_string, 'fully-loaded-nachos', name)
                                    # print(image_string)
                                    url = 'https://fully-loaded-nachos.s3.amazonaws.com/' + name
                                    cur.execute(sql, (timestamps[currentframe], filename, name, url))
                                    conn.commit()

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

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()
