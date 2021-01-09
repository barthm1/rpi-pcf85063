# rpi-pcf85063
Python functions for PCF85063

activate the rtc on CM4 IO-board with adding the line
dtparam=i2c_vc=on

in /boot/config.txt. After that check with i2cdetect -y 10 if the port is 0x51 active.

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- 0c -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 2f
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- 51 -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --

The following functions are implemented:
reset
setTime
setDate
readTime
enableAlarm
setAlarm
readAlarm
timerSet
