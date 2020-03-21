# Python-IS31FL3733
A matrix-centric Python driver for the IS31FL3733 16x12 I2C scanning matrix driver.

[Datasheet](http://www.issi.com/WW/pdf/IS31FL3733.pdf)

Usage

```

matrix = IS31FL3733(address=0x5F, busnum=10, DEBUG=False)
print("powering on all pixels")
matrix.enableAllPixels()

print("powering off all pixels via PWM register")
matrix.setAllPixelsPWM([0]*192)

print("let's fade up from 0 to 10 on all pixels")
for value in range(10):
	matrix.setAllPixelsPWM([value]*192)

```

Example projects

![Road Ahead project preview](http://chriscombs.net/assets/resized/1200/road-ahead-20191229-IMG_2380.jpg)
[14 panels of IS31FL3733 powering 336 segmented displays](https://hackaday.io/project/169244-336-digit-7-segment-display-with-per-segment-pwm)
