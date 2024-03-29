#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in9_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import asyncio
from pynput import keyboard

logging.basicConfig(level=logging.DEBUG)
epd = epd2in9_V2.EPD()

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)

text_image = Image.new('1', (epd.height, epd.width), 255)
text_draw = ImageDraw.Draw(time_image)

def initAndClear():
    epd.init()
    epd.Clear(0xFF)

def splashScreen():
    splashImg = Image.open(os.path.join(picdir, 'koala.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)


async def keypress_listener():
    text = ""
    
    def on_press(key):
        nonlocal text
        try:
            if key == keyboard.Key.enter:
                print("Entered text:", text)
                text = ""
            elif key == keyboard.Key.space:
                text += " "
            
            else:
                text += key.char
                #print(text)

        except AttributeError:
            pass

        finally:
            time_draw.rectangle((10, 10, 120, 50), fill = 255)
            time_draw.text((10, 10), time.strftime('%H:%M:%S'), font = font24, fill = 0)
            newimage = time_image.crop([10, 10, 120, 50])
            time_image.paste(newimage, (10,10))  
            epd.display_Partial(epd.getbuffer(time_image))
    
    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        await asyncio.Future()

async def main():

    initAndClear()
    splashScreen()

    epd.display_Base(epd.getbuffer(time_image))


    await asyncio.gather(
        keypress_listener(),
    )

if __name__ == "__main__":
    asyncio.run(main())
     


