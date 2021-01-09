#!/usr/bin/python3
# Copyright 2021 Markus Barth  <barthm1@gmail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



import smbus
import time
import datetime

# I2C-Adresse des PCF80063A
address = 0x51

# registar overview - crtl & status reg
RTC_CTRL_1 = 0x00
RTC_CTRL_2 = 0x01
RTC_OFFSET = 0x02
RTC_RAM_by = 0x03

# registar overview - time & data reg
RTC_SECOND_ADDR = 0x04
RTC_MINUTE_ADDR = 0x05
RTC_HOUR_ADDR   = 0x06
RTC_DAY_ADDR    = 0x07
RTC_WDAY_ADDR   = 0x08
RTC_MONTH_ADDR  = 0x09
RTC_YEAR_ADDR	= 0x0a # years 0-99; calculate real year = 1970 + RCC reg year

# registar overview - alarm reg
RTC_SECOND_ALARM = 0x0b
RTC_MINUTE_ALARM = 0x0c
RTC_HOUR_ALARM   = 0x0d
RTC_DAY_ALARM    = 0x0e
RTC_WDAY_ALARM   = 0x0f

# registar overview - timer reg
RTC_TIMER_VAL   = 0x10
RTC_TIMER_MODE  = 0x11
RTC_TIMER_TCF   = 0x08
RTC_TIMER_TE    = 0x04
RTC_TIMER_TIE   = 0x02
RTC_TIMER_TI_TP = 0x01

# format
RTC_ALARM          = 0x80	# set AEN_x registers
RTC_ALARM_AIE      = 0x80	# set AIE ; enable/disable interrupt output pin
RTC_ALARM_AF       = 0x40	# set AF register ; alarm flag needs to be cleared for alarm
RTC_CTRL_2_DEFAULT = 0x00
RTC_TIMER_FLAG     = 0x08

TIMER_CLOCK_4096HZ   = 0
TIMER_CLOCK_64HZ     = 1
TIMER_CLOCK_1HZ      = 2
TIMER_CLOCK_1PER60HZ = 3


# Erzeugen einer I2C-Instanz und Öffnen des Busses
pcf85063 = smbus.SMBus(10)

def decToBcd(val):
     return ((val // 10 * 16) + (val % 10))

def bcdToDec(val):
     return ((val // 16 * 10) + (val % 16))

def constrain (val, min_val, max_val):
    return min (max_val, max(min_val, val))

def reset():	# datasheet 8.2.1.3.
     pcf85063.write_byte_data (address, RTC_CTRL_1, 0x58)

def setTime (hour, minute, second):
     pcf85063.write_byte_data (address, RTC_SECOND_ADDR, decToBcd(second))
     pcf85063.write_byte_data (address, RTC_MINUTE_ADDR, decToBcd(minute))
     pcf85063.write_byte_data (address, RTC_HOUR_ADDR, decToBcd(hour))


def setDate (weekday, day, month, yr):

     year = yr - 1970; 	# convert to RTC year format 0-99

     pcf85063.write_byte_data (address, RTC_DAY_ADDR,   decToBcd(day))
     pcf85063.write_byte_data (address, RTC_WDAY_ADDR,  decToBcd(weekday))   # 0 for Sunday
     pcf85063.write_byte_data (address, RTC_MONTH_ADDR, decToBcd(month))
     pcf85063.write_byte_data (address, RTC_YEAR_ADDR,  decToBcd(year))

def readTime():
     rdata = pcf85063.read_i2c_block_data (address, RTC_SECOND_ADDR, 7)
     print (rdata)

     print (bcdToDec (rdata[0] & 0x7f)) # second
     print (bcdToDec (rdata[1])& 0x7f)  # minute
     print (bcdToDec (rdata[2] & 0x3f)) # hour

     print (bcdToDec (rdata[3] & 0x3f)) # day
     print (bcdToDec (rdata[4] & 0x07)) # wday
     print (bcdToDec (rdata[5] & 0x1f)) # month
     print (bcdToDec (rdata[6]) + 1970) # year


def enableAlarm(): # datasheet 8.5.6.
     # check Table 2. Control_2
     control_2 = RTC_CTRL_2_DEFAULT | RTC_ALARM_AIE #enable interrupt
     control_2 &= ~RTC_ALARM_AF                     # clear alarm flag

     pcf85063.write_byte_data (address, RTC_CTRL_2, control_2)

def setAlarm (alarm_second, alarm_minute, alarm_hour, alarm_day, alarm_weekday):

     if (alarm_second < 99): # second
        alarm_second = constrain (alarm_second, 0, 59)
        alarm_second = decToBcd (alarm_second)
        alarm_second &= ~RTC_ALARM;
     else:
        alarm_second = 0x0
        alarm_second |= RTC_ALARM

     if (alarm_minute < 99): # minute
        alarm_minute = constrain (alarm_minute, 0, 59)
        alarm_minute = decToBcd (alarm_minute)
        alarm_minute &= ~RTC_ALARM
     else:
        alarm_minute = 0x0;
        alarm_minute |= RTC_ALARM

     if (alarm_hour < 99): #  hour
        alarm_hour = constrain(alarm_hour, 0, 23)
        alarm_hour = decToBcd(alarm_hour)
        alarm_hour &= ~RTC_ALARM
     else:
        alarm_hour = 0x0
        alarm_hour |= RTC_ALARM

     if (alarm_day < 99): # day
        alarm_day = constrain(alarm_day, 1, 31)
        alarm_day = decToBcd(alarm_day)
        alarm_day &= ~RTC_ALARM
     else:
        alarm_day = 0x0
        alarm_day |= RTC_ALARM

     if (alarm_weekday < 99): # weekday
        alarm_weekday = constrain(alarm_weekday, 0, 6)
        alarm_weekday = decToBcd(alarm_weekday)
        alarm_weekday &= ~RTC_ALARM
     else:
        alarm_weekday = 0x0
        alarm_weekday |= RTC_ALARM

     enableAlarm();

     pcf85063.write_byte_data (address, RTC_SECOND_ALARM, alarm_second)
     pcf85063.write_byte_data (address, RTC_MINUTE_ALARM, alarm_minute)
     pcf85063.write_byte_data (address, RTC_HOUR_ALARM,   alarm_hour)
     pcf85063.write_byte_data (address, RTC_DAY_ALARM,    alarm_day)
     pcf85063.write_byte_data (address, RTC_WDAY_ALARM,   alarm_weekday)   # 0 for Sunday

def readAlarm():
     rdata = pcf85063.read_i2c_block_data (address, RTC_SECOND_ALARM, 5)    # datasheet 8.4.
     print (rdata)

     alarm_second = rdata[0]        # read RTC_SECOND_ALARM register

     if (RTC_ALARM & alarm_second): # check is AEN = 1 (second alarm disabled)
        alarm_second = 99           # using 99 as code for no alarm
     else:                          # else if AEN = 0 (second alarm enabled)
        alarm_second = bcdToDec (alarm_second & ~RTC_ALARM) # remove AEN flag and convert to dec number

     alarm_minute = rdata[1] # minute
     if (RTC_ALARM & alarm_minute):
        alarm_minute = 99
     else:
        alarm_minute = bcdToDec (alarm_minute & ~RTC_ALARM)

     alarm_hour = rdata[2] # hour
     if (RTC_ALARM & alarm_hour):
        alarm_hour = 99
     else:
        alarm_hour = bcdToDec (alarm_hour & 0x3F) # remove bits 7 & 6

     alarm_day = rdata[3] # day
     if (RTC_ALARM & alarm_day):
        alarm_day = 99
     else:
        alarm_day = bcdToDec (alarm_day & 0x3F) # remove bits 7 & 6

     alarm_weekday = rdata[4]  # weekday
     if (RTC_ALARM & alarm_weekday):
        alarm_weekday = 99
     else:
        alarm_weekday = bcdToDec (alarm_weekday & 0x07) # remove bits 7,6,5,4 & 3

     print (alarm_second, alarm_minute, alarm_hour, alarm_day, alarm_weekday)

def timerSet (source_clock, val, int_enable, int_pulse):

     timer_reg = [0,0]

     # disable the countdown timer
     pcf85063.write_byte_data (address, RTC_TIMER_MODE, 0x18)

     # clear Control_2
     pcf85063.write_byte_data (address, RTC_CTRL_2, 0x00)

     # reconfigure timer
     timer_reg[1] |= RTC_TIMER_TE # enable timer

     if (int_enable):
        timer_reg[1] |= RTC_TIMER_TIE # enable interrupr

     if (int_pulse):
        timer_reg[1] |= RTC_TIMER_TI_TP # interrupt mode

     timer_reg[1] |= source_clock << 3   # clock source
     # timer_reg[1] = 0b00011111;

     timer_reg[0] = val

     # write timer value
     pcf85063.write_byte_data (address, RTC_TIMER_VAL, timer_reg[0])
     pcf85063.write_byte_data (address, RTC_TIMER_MODE, timer_reg[1])



now = datetime.datetime.now()
print ("Current date and time : ")
print (now.strftime("%Y-%m-%d %H:%M:%S"))

reset()
setTime (now.hour, now.minute, now.second)
print (" Wochentag :" , int(datetime.datetime.today().strftime('%w')))
setDate (int(datetime.datetime.today().strftime('%w')), now.day, now.month, now.year)

readTime ()

setAlarm (21, 55, 14, 9, 6)
readAlarm()
