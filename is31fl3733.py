from __future__ import print_function

from .constants import *
from smbus2 import SMBus, i2c_msg
import time

class IS31FL3733DeviceNotFound(IOError):
    pass

class IS31FL3733(object):

    address = 0x50  
    busnum = 1
    syncmode = REGISTER_FUNCTION_CONFIGURATION_SYNC_CLOCK_SINGLE
    breathing = 0
    softwareshutdown = 0
    currentPage = PAGE_LEDONOFF
    pixels = [[0] * 16 for i in range(12)]
    triggerOpenShortDetection = 1
    DEBUG = False
    lastDebug = ""
    name = "IS31FL3733"

    def debug(self, *args):
        if self.DEBUG:
            if not hasattr(self, "lastDebug"):
                self.lastDebug = ""
            if self.lastDebug != args:
                print(self.name + ":", *args)
            self.lastDebug = args

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
          for key, value in kwargs.items():
              if type(value) is dict:
                  if getattr(self,key):
                        tempdict = getattr(self,key).copy()
                        tempdict.update(value)
                        value = tempdict
              setattr(self,key,value)

        self.smbus = SMBus(self.busnum)

        try:
            self.attemptDetection()
        except IOError:
            raise IS31FL3733DeviceNotFound('Could not communicate with device.')
        except TypeError:
            raise IS31FL3733DeviceNotFound('Device detection failed.')

        self.reset()
        self.setContrast(255)
        self.triggerOpenShortDetection = True
        self.setConfiguration()
        self.debug("Initialized.")

    def attemptDetection(self):

        # REGISTER_INTERRUPT_STATUS defaults to 0, can only be 0-3
        if self.read(REGISTER_INTERRUPT_STATUS) > 3:
            raise TypeError('REGISTER_INTERRUPT_STATUS is an invalid value--is this IS31FL3733?')

        # 0xC0 is not a readable address in any of the registers
        # It doesn't return a read error, but does always return 0
        if self.read(0xC0) != 0:
            raise TypeError('Was able to read an address that should not be readable (0xC0)--is this IS31FL3733?')

        # later IS31FL37xx devices support this...

        try:
            idregister=self.read(REGISTER_ID)
            if idregister != REGISTER_ID_VALUE_IS31FL3733:
                raise TypeError('ID register value',idregister,'does not match IS31FL3733 value:',REGISTER_ID_VALUE_IS31FL3733)
        except IOError:
            # all's well.
            pass


        self.debug("IS31FL3733 device detected.")
        return True

    def selectPage(self,value):
        if self.currentPage is not value:
            self.debug("changing page to",value,"from",self.currentPage)
            self.write(REGISTER_COMMAND_WRITE_LOCK,COMMAND_WRITE_LOCK_DISABLE_ONCE)
            self.write(REGISTER_COMMAND,value)
            self.currentPage = value

    def setContrast(self,value):
        self.selectPage(PAGE_FUNCTION)
        self.write(REGISTER_FUNCTION_CURRENT_CONTROL,value)

    def reset(self):
        self.selectPage(PAGE_FUNCTION)
        self.currentPage = PAGE_LEDONOFF
        self.debug("reset got",self.read(REGISTER_FUNCTION_RESET))

    def enableAllPixels(self):
        self.selectPage(PAGE_LEDONOFF)
        self.writeBlock(0, [ 255 ] * 0x18 )
        self.selectPage(PAGE_LEDPWM)
        for i in range(0,12):
            self.writeBlock(i*16,[ 255 ] * (16))

    def setPixelPower(self,row,col,val):
        address = row*2 + (col > 7)
# This needs work


    def setPixelPWM(self,row,col,val,immediate=True):
        pixel = row*16 + col
        self.pixels[row][col] = val
        # self.debug(row*16,col,"=",row*16 + col)
        if immediate:
            self.selectPage(PAGE_LEDPWM)
            self.write(pixel,val)

    def setAllPixelsPWM(self,values):
        # self.debug("length is",len(values))
        self.selectPage(PAGE_LEDPWM)

        # messageAddress = i2c_msg.write(self.address, [0])
        # messageToSend = i2c_msg.write(self.address, values)
        # self.smbus.i2c_rdwr(messageAddress,messageToSend)

        # TODO set the values in the array

        iterator = 0
        messages = []

        for chunk in self.chunks(values,32):
            messages.append(i2c_msg.write(self.address, iterator * 32 + chunk))
            iterator += 1

        self.smbus.i2c_rdwr(*messages)

    def setAllPixels(self,values):
        self.debug("length is",len(values))
        self.selectPage(PAGE_LEDONOFF)
        self.writeBlock(0,values)

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
        self.triggerOpenShortDetection = 1
        self.setConfiguration()
        time.sleep(0.01)
        self.selectPage(PAGE_LEDONOFF)
        returners = []
        for i in range(REGISTER_LEDONOFF_OPEN_START, REGISTER_LEDONOFF_OPEN_STOP + 1): # python range not inclusive
            returners.append(self.read(i))
        return returners

    def getShortPixels(self):
        self.triggerOpenShortDetection = 1
        self.setConfiguration()
        time.sleep(0.01)
        self.selectPage(PAGE_LEDONOFF)
        returners = []
        for i in range(REGISTER_LEDONOFF_SHORT_START, REGISTER_LEDONOFF_SHORT_STOP + 1): # python range not inclusive
            returners.append(self.read(i))
        return returners

    def chunks(self, values, length):
        for i in range(0, len(values), length):
            yield values[i:i + length]

    def writeBuffer(self):
        flat_list = [item for sublist in self.pixels for item in sublist]
        self.setAllPixelsPWM(0,flat_list)

    def sevenSegment(self, row, col, value, brightness=0):
        if brightness:
            self.selectPage(PAGE_LEDPWM)
            self.writeBlock(0,[brightness]*8)
        self.selectPage(PAGE_LEDONOFF)
        bits = 0B00000000
        if value == 0:
            bits = 0B00111111
        elif value == 1:
            bits = 0B00000110
        elif value == 2:
            bits = 0B01011011
        elif value == 3:
            bits = 0B01001111
        elif value == 4:
            bits = 0B01100110
        elif value == 5:
            bits = 0B01101101
        elif value == 6:
            bits = 0B01111101
        elif value == 7:
            bits = 0B00000111
        elif value == 8:
            bits = 0B01111111
        elif value == 9:
            bits = 0B01101111
        # self.debug(value)
        # self.debug(str(bits))
        # bits = 0b11111111 - bits
        self.write(row*2 + col + REGISTER_LEDONOFF_ONOFF_START,bits)


if __name__ == '__main__':

    for address in range(0x50,0x60):
        print("trying",address)
        try:
            matrix = IS31FL3733(address=address, busnum=8, DEBUG=True)
            matrix.setContrast(255)
            print("powering on all pixels")
            matrix.enableAllPixels()
            time.sleep(2)
            print("powering off all pixels via PWM register")
            matrix.setAllPixelsPWM([0]*192)

            print("let's try some 7-segment values (looks scrambled on most devices)")
            for value in range(10):
                print(value)
                matrix.sevenSegment(0,0,value)
                time.sleep(0.5)

            time.sleep(2)

            print("let's fade up from 0 to 10 on all pixels")
            for value in range(10):
                matrix.setAllPixelsPWM([value]*192)

            print ("let's draw some rows and cols")
            for row in range(12):
                for col in range(16):
                    matrix.setPixelPWM(row,col, 2)

            print("let's set some arbitrary pixels (check for adjacent shorts)")
            for i in range(11):
                matrix.setPixelPWM(i,i,40)
            for i in range(11):
                matrix.setPixelPWM(11-i,i,20)
            matrix.setPixelPWM(0,0,100)
            matrix.setPixelPWM(0,5,100)
            matrix.setPixelPWM(1,6,100)
            matrix.setPixelPWM(0,10,100)
            matrix.setPixelPWM(11,11,100)
            matrix.setPixelPWM(11,11,100)
            matrix.setPixelPWM(6,11,100)
            # matrix.setPixelPWM(3,12,3)
            time.sleep(1);
            print("all that done, now let's check for missing/short pixels.")
            print("missing pixels")
            print(matrix.getOpenPixels())
            print("short pixels")
            print(matrix.getShortPixels())
        except Exception as e:
            print("Address",address,"error:",e)
            time.sleep(0.1)
