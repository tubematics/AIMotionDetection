#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## USAGE
# download RPi Cam Control v6.6.11 on your raspberry pi
# open Browser with "IPAdressPi"/html
# run ai motion detection
#
# example modified from https://www.pyimagesearch.com/2020/02/10/opencv-dnn-with-nvidia-gpus-1549-faster-yolo-ssd-and-mask-r-cnn/
# import the necessary packages
import numpy as np
import imutils
import cv2
import time
import subprocess
import requests

from PIL import Image
from io import BytesIO

class AIMotionDetection():
  def __init__(self):
    self.ipRPi      = "0.0.0.0"
    self.frameCounter = 0
    self.url        = "http://" + self.ipRPi + "/html/cam_pic.php?time=%d&pDelay=40000" %self.frameCounter # change to RPi IP adress
    self.password   = "securepassword"    # change to password of RPi
    self.prototxt   = "MobileNetSSD_deploy.prototxt"
    self.model      = "MobileNetSSD_deploy.caffemodel"
    self.input      = "../example_videos/HausRotSchwanz.mp4"
    self.output     = "../output_videos/HRS2.avi"
    self.display    = 0         # 1 if output frame should be displayed
    self.confidence = 0.2       # minimum probability to filter weak detections
    self.gpuUse     = False     # boolean indicating if CUDA GPU should be used
    
    self.CLASSES    = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
    
    self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
    

  def inference(self, detections, frame):
    idx = -1
    objectList = []
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
      # extract the confidence (i.e., probability) associated with
      # the prediction
      confidence = detections[0, 0, i, 2]

      # filter out weak detections by ensuring the `confidence` is
      # greater than the minimum confidence
      if confidence > self.confidence:
        # extract the index of the class label from the
        # `detections`, then compute the (x, y)-coordinates of
        # the bounding box for the object
        idx = int(detections[0, 0, i, 1])
        if self.CLASSES[idx] == self.output:
          box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
          (startX, startY, endX, endY) = box.astype("int")

          # draw the prediction on the frame
          label = "{}: {:.2f}%".format(self.CLASSES[idx],
            confidence * 100)
          cv2.rectangle(frame, (startX, startY), (endX, endY),
            self.COLORS[idx], 2)
          y = startY - 15 if startY - 15 > 15 else startY + 15
          cv2.putText(frame, label, (startX, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)

          objectList.append(str(CLASSES[idx]))

    return objectList, idx

  def detect(self):
    self.frameCounter = 0
    timer = 0
    videoOn = False
    counter = 0

    # load serialized model from disk
    net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)

    # check if we are going to use GPU
    if self.gpuUse:
      # set CUDA as the preferable backend and target
      print("[INFO] setting preferable backend and target to CUDA...")
      net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
      net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    # initialize the video stream and pointer to output video file, then
    # start the FPS timer
    print("[INFO] accessing video stream...")

    # loop over the frames from the video stream
    while True:
      counter += 1
      self.frameCounter += 1
      writer = None

      r = requests.get(url = self.url) 

      if r.status_code == 200:
        img = Image.open(BytesIO(r.content))
        b, g, r = img.split()
        img = Image.merge("RGB", (r, g, b))
        frame = np.asarray(img)

      else:
        print("connection failed")

      # resize the frame, grab the frame dimensions, and convert it to
      # a blob
      frame = imutils.resize(frame, width=700)
      (h, w) = frame.shape[:2]
      blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

      # pass the blob through the network and obtain the detections and
      # predictions
      net.setInput(blob)
      detections = net.forward()

      objectList, idx= self.inference(detections, frame)
      print(str(objectList))

      if idx == -1:
        objectname = ""
      else:
        objectname = str(self.CLASSES[idx])  

      # update the screen every 5 cycles 
      if counter % 5 == 0:
        cmdline = ["sshpass", "-p", self.password, "ssh", "pi@" + self.ipRPi, "echo 'an " + objectname + "' >/var/www/html/FIFO11"]
        cmdOne = True
        sub = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
        print("[INFO] Text Objectname set...")

      # choose detected object from this list (self.CLASSES)
      if 'bird' in objectList:      
        timer = 0

        if videoOn == False:
          cmdline = ["sshpass", "-p", self.password, "ssh", "pi@" + self.ipRPi, "echo 'ca 1\r\nab 1' >/var/www/html/FIFO1"]
          sub2 = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
          print('[INFO] Video started...')
          videoOn = True

      if not objectList:     #if list is empty
        if timer == 0:
          timer = time.time()

        # switch off the video 5 s after object no longer detected
        if (time.time()-timer) > 5:
          if videoOn == True:
            cmdline = ["sshpass", "-p", self.password, "ssh", "pi@" + self.ipRPi, "echo 'ca 0\r\nab 0' >/var/www/html/FIFO1"]
            sub4 = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
            print("[INFO] Video stopped")
            timer = 0
            videoOn = False
          else:
            pass

      # dont over do it - we are communicating with a pi
      time.sleep(0.25)

      # check to see if the output frame should be displayed to our
      # screen
      if self.display > 0:
        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
          break

      # if an output video file path has been supplied and the video
      # writer has not been initialized, do so now
      if self.output != "" and writer is None:
        # initialize our video writer
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(self.output, fourcc, 30,
          (frame.shape[1], frame.shape[0]), True)

      # if the video writer is not None, write the frame to the output
      # video file
      if writer is not None:
        writer.write(frame)


if __name__ == "__main__":
  detection =  AIMotionDetection()
  detection.detect()
