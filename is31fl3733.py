from __future__ import print_function

from constants import *
from smbus2 import SMBus
import time


class IS31FL3733(object):

    address = 0x50
    busnum = 0
    syncmode = REGISTER_FUNCTION_CONFIGURATION_SYNC_CLOCK_SINGLE
    breathing = 0
    softwareshutdown = 0
    currentPage = PAGE_LED_ON_OFF
    pixels = [[0] * 12 for i in range(16)]
    triggerOpenShortDetection = 1

    def __del__(self):
        # self.smbus.close()
        pass

    def __init__(self, *args, **kwargs):

        # Flags

        if type (args) is not None:
          for arg in args:
              setattr(self,arg,True)

        # key=value parameters

        if type (kwargs) is not None:
          for key, value in kwargs.iteritems():
              if type(value) is dict:
                  if getattr(self,key):
                        tempdict = getattr(self,key).copy()
                        tempdict.update(value)
                        value = tempdict
              setattr(self,key,value)

        self.smbus = SMBus(self.busnum)
        self.reset()
        self.setContrast(255)
        self.triggerOpenShortDetection = 1
        self.setConfiguration()

    def selectPage(self,value):
        if self.currentPage is not value:
            print("changing page to",value,"from",self.currentPage)
            self.write(REGISTER_COMMAND_WRITE_LOCK,COMMAND_WRITE_LOCK_DISABLE_ONCE)
            self.write(REGISTER_COMMAND,value)
            self.currentPage = value

    def setContrast(self,value):
        self.selectPage(PAGE_FUNCTION)
        self.write(REGISTER_FUNCTION_CURRENT_CONTROL,value)

    def reset(self):
        self.selectPage(PAGE_FUNCTION)
        self.currentPage = PAGE_LED_ON_OFF
        print("reset got",self.read(REGISTER_FUNCTION_RESET))

    def enableAllPixels(self):
        self.selectPage(PAGE_LED_ON_OFF)
        self.writeBlock(0, [ 255 ] * 0x17 )
        self.selectPage(PAGE_LED_PWM)
        for i in range(0,12):
            self.writeBlock(i*16,[ 255 ] * (16))

    def setPixelPower(self,row,col,val):
        address = row*2 + (col > 7)
# This needs work


    def setPixelPWM(self,row,col,val):
        pixel = row*16 + col
        self.pixels[row][col] = val
        self.selectPage(PAGE_LED_PWM)
        self.write(pixel,val)

    def setConfiguration(self):
        self.selectPage(PAGE_FUNCTION)
        regvalue = ( self.breathing * REGISTER_FUNCTION_CONFIGURATION_BREATHING_ENABLE ) | ( self.syncmode ) | ( ( not self.softwareshutdown ) * REGISTER_FUNCTION_CONFIGURATION_SOFTWARE_SHUTDOWN ) | ( self.triggerOpenShortDetection * REGISTER_FUNCTION_CONFIGURATION_TRIGGER_OPEN_SHORT_DETECTION )
        self.triggerOpenShortDetection = False
        self.write(REGISTER_FUNCTION_CONFIGURATION, regvalue)

    def write(self,register,value):
        self.smbus.write_byte_data(self.address,register,value)

    def writeBlock(self,register,value):
        self.smbus.write_i2c_block_data(self.address,register,value) 

    def read(self,register):
        return self.smbus.read_byte_data(self.address,register)

    def getOpenPixels(self):
        self.selectPage(PAGE_LED_ON_OFF)
        for i in range(0x18,0x2e):
            print(self.read(i))

    def getShortPixels(self):
        self.selectPage(PAGE_LED_ON_OFF)
        for i in range(0x30,0x47):
            print(self.read(i))




if __name__ == '__main__':
    matrix = IS31FL3733(address=0x5F)
    matrix.enableAllPixels()
    matrix.getOpenPixels()
    matrix.getShortPixels()
