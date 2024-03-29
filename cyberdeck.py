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
import keyboard

logging.basicConfig(level=logging.DEBUG)
epd = epd2in9_V2.EPD()

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)

text_image = Image.new('1', (epd.height, epd.width), 255)
text_draw = ImageDraw.Draw(text_image)

def initAndClear():
    epd.init()
    epd.Clear(0xFF)

def splashScreen():
    splashImg = Image.open(os.path.join(picdir, 'koala.bmp'))
    epd.display(epd.getbuffer(splashImg))
    time.sleep(2)
import asyncio
import keyboard

async def keypress_listener(text_changed_event):
    text = ""
    caps_lock_active = False
    shift_pressed = False

    while True:
        key_event = await asyncio.to_thread(keyboard.read_event)
        if key_event.event_type == keyboard.KEY_DOWN:
            if key_event.name == "enter":
                print("Entered text:", text)
                text = ""
            elif key_event.name == "space":
                text += " "
            elif key_event.name == "caps lock":
                caps_lock_active = not caps_lock_active
            elif key_event.name == "backspace":
                text = text[:-1]  # Delete the most recent character
            elif key_event.name == "shift":
                shift_pressed = True
            else:
                if shift_pressed or (caps_lock_active and key_event.name.isalpha()):
                    text += key_event.name.upper()
                else:
                    text += key_event.name
            text_changed_event.set()

        elif key_event.event_type == keyboard.KEY_UP:
            if key_event.name == "shift":
                shift_pressed = False

async def text_changed_checker(text_changed_event):
    while True:
        await text_changed_event.wait()
        text_draw.rectangle((10, 10, 120, 50), fill = 255)
        text_draw.text((10, 10), time.strftime('%H:%M:%S'), font = font24, fill = 0)
        newimage = text_image.crop([10, 10, 120, 50])
        text_image.paste(newimage, (10,10))  
        epd.display_Partial(epd.getbuffer(text_image))
        text_changed_event.clear()


async def main():

    initAndClear()
    splashScreen()

    epd.display_Base(epd.getbuffer(text_image))

    text_changed_event = asyncio.Event()
    await asyncio.gather(
        keypress_listener(text_changed_event),
        text_changed_checker(text_changed_event),
    )

if __name__ == "__main__":
    asyncio.run(main())
     



