from machine import Pin, I2C
from framebuf import FrameBuffer, MONO_HLSB
import ssd1306

# using default address 0x3C
oledWidth = 128
oledHeight = 32
i2c = I2C(1, sda=Pin(26), scl=Pin(27))
display = ssd1306.SSD1306_I2C(oledWidth, oledHeight, i2c)


# Takes current time and uses convertToString and numbersToBitmap to display correct font with displayFont
def showTime(countDown):
    timeString = convertToString(countDown)
    bitMap = numbersToBitmap(timeString)
    displayFont(bitMap)


# Used to clear the display
def fillDisplay(value):
    display.fill(value)
    display.show()


def invertDisplay(value):
    display.invert(value)
    display.show()


def powerDisplay(value):
    if value:
        display.poweron()
    elif not value:
        display.poweroff()


# Takes in bitmap of a converted string and shows it on the display
def displayFont(bitmapArray):
    startX = -16 + int((oledWidth - 16 * len(bitmapArray)) / 2)
    startY = int((oledHeight - 16) / 2)
    display.fill(0)
    for i in bitmapArray:
        bitmap = bytearray(i)
        fb = FrameBuffer(bitmap, 16, 24, MONO_HLSB)
        startX += 16
        display.blit(fb, startX, startY)
    display.show()


# Takes in number and shows it as minutes/seconds 95 -> 01:35. Bitmap fonts from https://github.com/DavesCodeMusings/oled-bitmapper
def convertToString(t: int):
    mins, secs = divmod(t, 60)
    timeStr = "{:02d}:{:02d}".format(mins, secs)
    return timeStr


# fmt: off
# Converts a string of numbers to a bitmap with the correct font
def numbersToBitmap(numberString):
    bitmapArrays = []
    for num in numberString:
        if num == "0":
            bitmapArrays.append(
                [255,232,127,216,191,184,192,56,224,56,224,56,224,56,224,56,224,56,192,24,128,8,0,0,128,8,192,24,224,56,224,56,224,56,224,56,224,56,192,56,191,184,127,216,255,232,0,0]
            )
        elif num == "1":
            bitmapArrays.append(
                [0,8,0,24,0,56,0,56,0,56,0,56,0,56,0,56,0,56,0,24,0,8,0,0,0,8,0,24,0,56,0,56,0,56,0,56,0,56,0,56,0,56,0,24,0,8,0,0]
            )
        elif num == "2":
            bitmapArrays.append(
                [255,232,127,216,63,184,0,56,0,56,0,56,0,56,0,56,0,56,0,24,63,232,127,240,191,224,192,0,224,0,224,0,224,0,224,0,224,0,192,0,191,128,127,192,255,224,0,0]
            )
        elif num == "3":
            bitmapArrays.append(
                [255,232,127,216,63,184,0,56,0,56,0,56,0,56,0,56,0,56,0,24,63,232,127,240,63,232,0,24,0,56,0,56,0,56,0,56,0,56,0,56,63,184,127,216,255,232,0,0]
            )
        elif num == "4":
            bitmapArrays.append(
                [0,8,0,24,128,56,192,56,224,56,224,56,224,56,224,56,224,56,192,24,191,232,127,240,63,232,0,24,0,56,0,56,0,56,0,56,0,56,0,56,0,56,0,24,0,8,0,0]
            )
        elif num == "5":
            bitmapArrays.append(
                [255,224,127,192,191,128,192,0,224,0,224,0,224,0,224,0,224,0,192,0,191,224,127,240,63,232,0,24,0,56,0,56,0,56,0,56,0,56,0,56,63,184,127,216,255,232,0,0]
            )
        elif num == "6":
            bitmapArrays.append(
                [255,224,127,192,191,128,192,0,224,0,224,0,224,0,224,0,224,0,192,0,191,224,127,240,191,232,192,24,224,56,224,56,224,56,224,56,224,56,192,56,191,184,127,216,255,232,0,0]
            )
        elif num == "7":
            bitmapArrays.append(
                [255,232,127,216,63,184,0,56,0,56,0,56,0,56,0,56,0,56,0,24,0,8,0,0,0,8,0,24,0,56,0,56,0,56,0,56,0,56,0,56,0,56,0,24,0,8,0,0]
            )
        elif num == "8":
            bitmapArrays.append(
                [255,232,127,216,191,184,192,56,224,56,224,56,224,56,224,56,224,56,192,24,191,232,127,240,191,232,192,24,224,56,224,56,224,56,224,56,224,56,192,56,191,184,127,216,255,232,0,0]
            )
        elif num == "9":
            bitmapArrays.append(
                [255,232,127,216,191,184,192,56,224,56,224,56,224,56,224,56,224,56,192,24,191,232,127,240,63,232,0,24,0,56,0,56,0,56,0,56,0,56,0,56,63,184,127,216,255,232,0,0]
            )
        elif num == ":":
            bitmapArrays.append(
                [0,0,0,0,0,0,0,0,0,0,0,0,1,128,3,192,3,192,1,128,0,0,0,0,0,0,0,0,1,128,3,192,3,192,1,128,0,0,0,0,0,0,0,0,0,0,0,0]
            )
        else:
            print("Invalid input: {}".format(num))
    return bitmapArrays
# fmt: on
