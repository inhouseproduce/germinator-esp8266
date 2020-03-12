import uuid
import ntptime
import machine
import sht31

#AWS MQTT client cert example for esp8266 or esp32 running MicroPython 1.9 
from umqtt.robust import MQTTClient
import time

# SHT31 Pin Init
i = machine.I2C(sda=machine.Pin(5), scl=machine.Pin(4)) # Found tutorials saying to flip these, but worked before...
s = sht31.SHT31(i)

# 2 Relay Module Pin Init
heaterPin = machine.Pin(0, machine.Pin.OUT)
humidiPin = machine.Pin(2, machine.Pin.OUT)

######################################################
#              VALUES TO EDIT: BEGIN                 #
######################################################

# Temperature Vals (TRUE)
tempLimit = 23.0
tMax = 24.0

# Humidity Vals (TRUE)
humidLimit = 90.0
hMax = 97.0

#This works for either ESP8266 ESP32 if you rename certs before moving into board
CERT_FILE = "CERTNAME.cert.der"
KEY_FILE = "CERTNAME.key.der"

#if you change the ClientId make sure update AWS policy
MQTT_CLIENT_ID = "basicPubSub"
MQTT_PORT = 8883

#topic AWS policy
MQTT_TOPIC = "MQTT_TOPIC"

#Change the following settings to match your environment
MQTT_HOST = "AWS_ENDPOINT_ADDRESS-ats.iot.us-west-1.amazonaws.com"
WIFI_SSID = "inHouse_24GHz"
WIFI_PW = "P@$$word"
port = 8081
endpoint = 'ENDPOINT'

######################################################
#               VALUES TO EDIT: END                  #
######################################################

mqtt_client = None

def pub_msg(msg):
    global mqtt_client
    try:    
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise

def connect_mqtt():    
    global mqtt_client

    try:
        with open(KEY_FILE, "r") as f: 
            key = f.read()

        print("Got Key")
            
        with open(CERT_FILE, "r") as f: 
            cert = f.read()

        print("Got Cert")	

        mqtt_client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
        mqtt_client.connect()
        print('MQTT Connected')
    except Exception as e:
        print('Cannot connect MQTT: ' + str(e))
        raise

def connect_wifi(ssid, pw):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PW)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

        
def connect_wifi_sdk(ssid, pw):
    from network import WLAN
    from network import STA_IF
    import machine

    wlan = WLAN(STA_IF)
    nets = wlan.scan()
    if(wlan.isconnected()):
        wlan.disconnect()            
    wlan.connect(ssid, pw)         
    while not wlan.isconnected():             
        machine.idle() # save power while waiting
        print('WLAN connection succeeded!')         
        break 
    print("connected:", wlan.ifconfig())

f = open('log.txt', 'w')

#start execution
try:
    print("Connecting WIFI")
    connect_wifi(WIFI_SSID, WIFI_PW)
    print("Connecting MQTT")
    connect_mqtt()
    rtc = machine.RTC()
    # synchronize with ntp
    # need to be connected to wifi
    utc = -8
    ntptime.settime() # set the rtc datetime from the remote server
    dateTime = rtc.datetime()
    year = str(dateTime[0])
    month = str(dateTime[1])
    if len(month) == 1:
        month = '0' + month
    date = str(dateTime[2])
    if len(date) == 1:
        date = '0' + date
    weekDay = 'M'
    if dateTime[3] == 0:
        weekDay = 'M'
    elif dateTime[3] == 1:
        weekDay = 'T'
    elif dateTime[3] == 2:
        weekDay = 'W'
    elif dateTime[3] == 3:
        weekDay = 'R'
    elif dateTime[3] == 4:
        weekDay = 'F'
    elif dateTime[3] == 5:
        weekDay = 'S'
    elif dateTime[3] == 6:
        weekDay = 'U'
    hour = str(dateTime[4]+utc)
    if len(hour) == 1:
        hour = '0' + hour
    minute = str(dateTime[5])
    if len(minute) == 1:
        minute = '0' + minute
    sec = str(dateTime[6])
    if len(sec) == 1:
        sec = '0' + sec
    usec = str(dateTime[7])
    if len(usec) == 2:
        usec = '0' + usec
    elif len(usec) == 1:
        usec = "00" + usec
    postId = uuid.uuid4()
    dt = year + '-' + month + '-' + date + weekDay + hour + ':' + minute + ':' + sec + '.' + usec + 'Z'   # print vals
    f.write("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"" + str(dt) + "\", \"temp_c\" : 0.0, \"temp_f\" : 32.0, \"humidity\" : 0.0}")
    print("Publishing")
    pub_msg("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"" + str(dt) + "\", \"temp_c\" : 0.0, \"temp_f\" : 32.0, \"humidity\" : 0.0}")
    print("Initializer Complete")
except Exception as e:
    print(str(e))
    pass