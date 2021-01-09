# rpi-pcf85063
Python functions for PCF85063

activate the rtc on CM4 IO-board with adding the line
dtparam=i2c_vc=on

in /boot/config.txt. After that check with i2cdetect -y 10 if the port is 0x51 active.

.

.

50: -- 51 -- -- -- -- -- -- -- -- -- -- -- -- -- --

.

.


The following functions are implemented:
reset

setTime

setDate

readTime

enableAlarm

setAlarm

readAlarm

timerSet
