#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join('/home/wade/RaspberryPi_JetsonNano/python/pic/')
libdir = os.path.join('/home/wade/RaspberryPi_JetsonNano/python/lib/')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in9_V2
import time
from PIL import Image,ImageDraw,ImageFont


logging.basicConfig(level=logging.DEBUG)
epd = epd2in9_V2.EPD()

mainscreen = Image.new('1', (epd.height, epd.width), 255)
mainscreen_draw = ImageDraw.Draw(mainscreen)

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)


def initAndClear():
    epd.init()
    epd.Clear(0xFF)

def splashScreen():
    splashImg = Image.open(os.path.join(picdir, 'koala.bmp'))
    epd.display(epd.getbuffer(splashImg))
    time.sleep(2)

def mainScreenLoop():
    epd.display_Base(epd.getbuffer(mainscreen))
    mail = Icon(os.path.join(picdir,'icons/mail.bmp'),os.path.join(picdir,'icons/mail selected.bmp'))
    notes = Icon(os.path.join(picdir,'icons/notes.bmp'),os.path.join(picdir,'icons/notes selected.bmp'))
    clock = Icon(os.path.join(picdir,'icons/clock.bmp'),os.path.join(picdir,'icons/clock selected.bmp'))
    settings = Icon(os.path.join(picdir,'icons/settings.bmp'),os.path.join(picdir,'icons/settings selected.bmp'))

    dock = Dock([mail,notes,clock,settings],60,24)
    time.sleep(1)
    dock.advance()
    time.sleep(1)
    dock.advance()
    time.sleep(.5)
    dock.retreat()
    time.sleep(.5)
    dock.retreat()
    time.sleep(.5)
    dock.retreat()
    time.sleep(.5)
    dock.retreat()
    time.sleep(.5)
    dock.retreat()
    time.sleep(.5)
    dock.retreat()

    
class Dock:
    def __init__(self,icons,y, icon_width):
        self.icons = icons
        self.y = y
        self.width = icon_width
        self.index = 0
        self.arrange()
    

    def arrange(self):
        x_start = epd.width/2 - len(self.icons)/2*self.width

        for i in self.icons:
            i.y = self.y
            i.x = x_start
            if self.icons.index(i) == 0:
                i.toggle()
            else:
                i.display(i.unselected_image_path)
    
    def advance(self):
        self.icons[self.index].toggle()
        self.index += 1
        if self.index >= len(self.icons):
            self.index = 0
        self.icons[self.index].toggle()
    
    def retreat(self):
        self.icons[self.index].toggle()
        self.index -= 1
        if self.index < 0:
            self.index = len(self.icons) - 1
        self.icons[self.index].toggle()






class Icon:
    def __init__(self, unselected_image_path, selected_image_path, x = 0, y = 0):
        self.x = x
        self.y = y
        self.unselected_image_path = unselected_image_path
        self.selected_image_path = selected_image_path
        self.selected = False
        #self.display(self.unselected_image_path)
            
    
        #epd.display_Base(epd.getbuffer(time_image))

    def toggle(self):
        self.selected = not self.selected
        if self.selected:
            self.display(self.selected_image_path)
        else:
            self.display(self.unselected_image_path)

    def display(self,img):

        bmp = Image.open(os.path.join(picdir, img))
        mainscreen.paste(bmp, (self.x,self.y))  
        epd.display_Partial(epd.getbuffer(mainscreen))


if __name__ == "__main__":
    initAndClear()
    splashScreen()


     



