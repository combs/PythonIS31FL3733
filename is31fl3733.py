
from constants import *
from smbus2 import SMBus
import time


class IS31FL3733(object):

    address = 0x50
    busnum = 0
    syncmode = REGISTER_FUNCTION_CONFIGURATION_SYNC_CLOCK_SINGLE
    breathing = False
    softwareshutdown = False
    currentPage = PAGE_LED_ON_OFF
    pixels = [[0] * 12 for i in range(16)]

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

    def selectPage(self,value):
        if self.currentPage != value:
            self.write(REGISTER_COMMAND_WRITE_LOCK,COMMAND_WRITE_LOCK_DISABLE_ONCE)
            self.write(REGISTER_COMMAND,value)
            self.currentPage = value

    def reset(self):
        self.write(REGISTER_COMMAND_WRITE_LOCK,COMMAND_WRITE_LOCK_DISABLE_ONCE)
        self.write(REGISTER_COMMAND,PAGE_FUNCTION)
        self.read(REGISTER_FUNCTION_RESET)

    def setPixelPWM(self,row,col,val):
        pixel = row*16 + col
        self.pixels[row][col] = val
        self.selectPage(PAGE_LED_PWM)
        self.write(pixel,val)

    def setConfiguration(self):
        self.selectPage(PAGE_FUNCTION)
        regvalue = ( self.breathing * REGISTER_FUNCTION_CONFIGURATION_BREATHING_ENABLE ) & ( self.syncmode ) & ( self.softwareshutdown * REGISTER_FUNCTION_CONFIGURATION_SOFTWARE_SHUTDOWN ) & ( self.triggerOpenShortDetection * REGISTER_FUNCTION_CONFIGURATION_TRIGGER_OPEN_SHORT_DETECTION )
        self.triggerOpenShortDetection = False
        self.write(REGISTER_FUNCTION_CONFIGURATION, regvalue)

    def write(self,register,value):
        self.smbus.write_byte_data(self.address,register,value)

    def read(self,register):
        return self.smbus.read_byte_data(self.address,register)



if __name__ == '__main__':
    matrix = IS31FL3733()
    matrix.setPixelPWM(4,1,128)
