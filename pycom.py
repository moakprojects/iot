import socket
import pycom
import time
from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
from SI7006A20 import SI7006A20
import json
import struct
from machine import Pin
from machine import ADC

pycom.heartbeat(False)

#Credential information of the connected router
wifi_ssid = '####'
wifi_pass = '####'

#This makes the connection
if machine.reset_cause() != machine.SOFT_RESET:

    wlan = WLAN(mode=WLAN.STA)

    wlan.connect(wifi_ssid, auth=(WLAN.WPA2, wifi_pass), timeout=5000)

    while not wlan.isconnected():
        machine.idle()

print('Connected to Wifi\n')
print(wlan.ifconfig())

#This is need for the current time, Pycom don't have module to give the actual time, it can just give the seconds from the power on, so after the pycom device connect to the router we have to synchronize its RTC module, the RTC gets the current datetime from pool.ntp.org site and after it time.localtime() can provide the actual time
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
time.timezone(7200)

#Here we initialize the two class which needs for the light and humidity sense, both needs the pysense class
py = Pysense()
lt = LTR329ALS01(py)
hu = SI7006A20(py)

#This is for the extension temperature sensor, we have to put the Pin19 to output to get values from the sensor
p_out = Pin('P19', mode=Pin.OUT)
p_out.value(1)
p_out.value(0)
p_out.toggle()
p_out(True)

#We will get the sensed extenson temperature values (basically voltage values) through the Pin16
adc = ADC(id=0)
apin = adc.channel(pin='P16')

#We initialize a socket which will transfer these data to the webserver
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def data_sense():
    #connect to the webserver on the port 1236
    s.connect(('18.196.31.205', 1236))
    #get the sensed values
    light = lt.light()
    hum = hu.humidity()
    volt = apin.voltage()
    current_t = time.localtime()

    #make a dictionary from the values, to use as less bit as possible, the keys are just one letter, these are:
    # t: time
    # b: blue channel of light
    # r: red channel of light
    # h: humidity
    # v: voltage for the temperature
    data = {'t':current_t,'b':light[0],'r':light[1],'h':hum,'v':volt}
    # we make a json from the dict 
    data_send = json.dumps(data)
    #we send it to the webserver and then close the connection (I'm not sure yet, is it neccessary or not)
    s.send(data_send)
    s.disconnect()
    #after a while we measure again by call the function
    time.sleep(300)
    data_sense()

data_sense()
