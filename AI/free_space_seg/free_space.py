import sys
import argparse

import cv2
import jetson.inference
from jetson_inference import segNet
import jetson.utils
import numpy as np

# parse the command line
parser = argparse.ArgumentParser(description="Segment a live camera stream using an semantic segmentation DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=segNet.Usage())

parser.add_argument("--network", type=str, default="fcn-resnet18-sun-512x400", help="pre-trained model to load, see below for options")
parser.add_argument("--classid", type=str, default=2, help="filter for classid")

try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

flip = 2
dispW = 512
dispH = 400

cuda_frame = None
class_mask = None
camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

# load the segmentation network
network =args.network
net = segNet(network, sys.argv)

cap = cv2.VideoCapture(camSet)
ret, frame = cap.read()

# Allocate buffer for cuda_frame
if cuda_frame is None:
  cuda_frame = jetson.utils.cudaAllocMapped(width=dispW, height=dispH, format="rgba8")
  img = jetson.utils.cudaToNumpy(cuda_frame, dispW, dispH, 4)
frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
cuda_frame = jetson.utils.cudaFromNumpy(frame_rgba)

# process the segmentation network
net.Process(cuda_frame)
num_classes = net.GetNumClasses()
jetson.utils.cudaDeviceSynchronize()
img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB).astype(np.uint8)
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Allocate buffer for mask
if class_mask is None:
  class_mask = jetson.utils.cudaAllocMapped(width=dispW, height=dispH, format="rgb8")
  class_mask_np = jetson.utils.cudaToNumpy(class_mask)

# get the class mask (each pixel contains the classID for itself)
net.Mask(class_mask, dispW, dispH, format="rgb8")
class_mask_np = jetson.utils.cudaToNumpy(class_mask)

# compute the number of times each class occurs in the mask
arr = np.array(class_mask_np)            	
img = cv2.resize(img, (dispW, dispH), interpolation = cv2.INTER_LINEAR) 
output = img.copy()

# Color the pixel with green for those representing a class_id 
if args.classid == 99:
  for n in range(num_classes):
    valid = np.all(arr == n, axis = -1)
    rs, cs = valid.nonzero()
    colorCode = net.GetClassColor(n)
    output[rs, cs, :] = [colorCode[0],colorCode[1],colorCode[2]]
else:
  valid = np.all(arr == args.classid, axis = -1)
  rs, cs = valid.nonzero()
  colorCode = net.GetClassColor(args.classid)
  output[rs, cs, :] = [colorCode[0],colorCode[1],colorCode[2]]
overlayed_image = cv2.addWeighted(img,0.5,output,0.5,0)
cv2.imshow("overlayed_image", overlayed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()