import time, board, digitalio, busio
from PIL import Image, ImageDraw, ImageFont
from math import cos, sin, pi, floor
from adafruit_rplidar import RPLidar
import adafruit_rgb_display.st7735 as st7735  

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Setup SPI bus using hardware SPI:
spi = board.SPI()

disp = st7735.ST7735R(spi, rotation=90, x_offset=2, y_offset=2, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=24000000)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width   # we swap height/width to rotate it to landscape!sudo apt-get install libfreetype6-dev
    width = disp.height
else:
    width = disp.width   # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = -2
x = 0

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)

def process_data(data):
    global max_distance
    lcd.fill((0,0,0))
    for angle in range(360):
        distance = data[angle]
        if distance > 0:                  # ignore initially ungathered data points
            max_distance = max([min([5000, distance]), max_distance])
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point = (160 + int(x / max_distance * 119), 120 + int(y / max_distance * 119))
            draw.point(point, None)
        disp.image(image)
        time.sleep(.1)
    
# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

scan_data = [0]*360

try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = distance
            process_data(distance)

except KeyboardInterrupt:
    print('Stoping.')
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()

except Exception as error:
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()
    print('Error: ' + repr(error))