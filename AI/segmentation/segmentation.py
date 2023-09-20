#!/usr/bin/env python3
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import sys
import argparse
import time

from jetson_inference import segNet
from jetson_utils import videoSource, videoOutput, cudaOverlay, cudaDeviceSynchronize, Log

from segnet_utils import *

import Jetson.GPIO as GPIO

GPIO.setwarnings(False)
motor_right_a = 11
motor_right_b = 12
motor_left_a = 15
motor_left_b = 16
motor_right_en = 32
motor_left_en = 33

speed = 30

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_right_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_en, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(motor_left_en, GPIO.OUT, initial=GPIO.HIGH)
p = GPIO.PWM(motor_right_en, speed)
w = GPIO.PWM(motor_left_en, speed)

timer = 0

# parse the command line
parser = argparse.ArgumentParser(description="Segment a live camera stream using an semantic segmentation DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=segNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="fcn-resnet18-sun-512x400", help="pre-trained model to load, see below for options")
parser.add_argument("--filter-mode", type=str, default="linear", choices=["point", "linear"], help="filtering mode used during visualization, options are:\n  'point' or 'linear' (default: 'linear')")
parser.add_argument("--visualize", type=str, default="overlay,mask", help="Visualization options (can be 'overlay' 'mask' 'overlay,mask'")
parser.add_argument("--ignore-class", type=str, default="void", help="optional name of class to ignore in the visualization results (default: 'void')")
parser.add_argument("--alpha", type=float, default=150.0, help="alpha blending value to use during overlay, between 0.0 and 255.0 (default: 150.0)")
parser.add_argument("--stats", action="store_true", help="compute statistics about segmentation mask class output")

try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# load the segmentation network
net = segNet(args.network, sys.argv)

# note: to hard-code the paths to load a model, the following API can be used:
#
# net = segNet(model="model/fcn_resnet18.onnx", labels="model/labels.txt", colors="model/colors.txt",
#              input_blob="input_0", output_blob="output_0")

# set the alpha blending value
net.SetOverlayAlpha(args.alpha)

# create video output
output = videoOutput(args.output, argv=sys.argv)

# create buffer manager
buffers = segmentationBuffers(net, args)

# create video source
input = videoSource(args.input, argv=sys.argv)

# process frames until EOS or the user exits
while True:
    # capture the next image
    img_input = input.Capture()

    if img_input is None: # timeout
        continue
        
    # allocate buffers for this size image
    buffers.Alloc(img_input.shape, img_input.format)

    # process the segmentation network
    net.Process(img_input, ignore_class=args.ignore_class)

    # generate the overlay
    if buffers.overlay:
        net.Overlay(buffers.overlay, filter_mode=args.filter_mode)

    # generate the mask
    if buffers.mask:
        net.Mask(buffers.mask, filter_mode=args.filter_mode)

    # composite the images
    if buffers.composite:
        cudaOverlay(buffers.overlay, buffers.composite, 0, 0)
        cudaOverlay(buffers.mask, buffers.composite, buffers.overlay.width, 0)

    # render the output image
    output.Render(buffers.output)

    # draw pathfinding frame
    grid_width, grid_height = net.GetGridSize()
    class_mask = cudaAllocMapped(width=grid_width, height=grid_height, format="gray8")
    class_mask_np = cudaToNumpy(class_mask)
    net.Mask(class_mask, grid_width, grid_height)

    # Use output for navigation 

    if timer == 3:
        if class_mask_np[9,4] <= 1 & class_mask_np[9,5] <= 1 & class_mask_np[9,6] <= 1 & class_mask_np[9,7] <= 1 & class_mask_np[9,8] <= 1:
            #if class_mask_np[1,4] >= 1 & class_mask_np[1,5] >= 1 & class_mask_np[1,6] >= 1 & class_mask_np[1,7] >= 1 & class_mask_np[1,8] >= 1:
                #if class_mask_np[7,4] >= 1 & class_mask_np[7,5] >= 1 & class_mask_np[7,6] >= 1 & class_mask_np[7,7] >= 1 & class_mask_np[7,8] >= 1:
                #    if class_mask_np[6,4] >= 1 & class_mask_np[6,5] >= 1 & class_mask_np[6,6] >= 1 & class_mask_np[6,7] >= 1 & class_mask_np[6,8] >= 1:
                print("I see floor")
                p.start(speed)
                w.start(speed)
                GPIO.output(motor_right_a, GPIO.HIGH)
                GPIO.output(motor_right_b, GPIO.LOW)
                GPIO.output(motor_left_a, GPIO.LOW)
                GPIO.output(motor_left_b, GPIO.HIGH)
                time.sleep(.3)
                p.stop()
                w.stop()
                GPIO.output(motor_right_a, GPIO.LOW)
                GPIO.output(motor_left_b, GPIO.LOW)
                GPIO.output(motor_right_b, GPIO.LOW)
                GPIO.output(motor_left_a, GPIO.LOW)
                timer = 0
        else:
            print ("No floor")
            p.start(speed+20)
            w.start(speed+20)
            GPIO.output(motor_right_a, GPIO.LOW)
            GPIO.output(motor_right_b, GPIO.HIGH)
            GPIO.output(motor_left_a, GPIO.LOW)
            GPIO.output(motor_left_b, GPIO.HIGH)
            time.sleep(.3)
            p.stop()
            w.stop()
            GPIO.output(motor_right_b, GPIO.LOW)
            GPIO.output(motor_left_b, GPIO.LOW)
            GPIO.output(motor_right_a, GPIO.LOW)
            GPIO.output(motor_left_a, GPIO.LOW)
                #else: 
                    #print ("No floor")
           # else:
         #       print ("No floor")
       # else:
        #    print ("No floor")
    else:
        timer = timer +1                
    
    # update the title bar
    output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

    # print out performance info
    cudaDeviceSynchronize()
    #net.PrintProfilerTimes()

    # compute segmentation class stats
    if args.stats:
        buffers.ComputeStats()

    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
        p.stop()
        w.stop()
        GPIO.output(motor_right_a, GPIO.LOW)
        GPIO.output(motor_left_b, GPIO.LOW)
        GPIO.output(motor_right_b, GPIO.LOW)
        GPIO.output(motor_left_a, GPIO.LOW)
        break
