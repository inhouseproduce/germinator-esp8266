import time
import uuid
import os
import urequests
import ujson

# Failover Limit (TRUE)
terrMin = 10.0
terrMax = 27.0
herrMin = 0.0
herrMax = 100.0

# # Failover Limit (FALSE)
# terrMin = 0.0
# terrMax = 40.0
# herrMin = 0.0
# herrMax = 100.0

# Helper Variables
prevTemp = 0.0
prevHumi = 0.0
firstRun = True
hon = False
ton = False
err = False
tDiff = 0
hDiff = 0

# Iterators
iter = 1
MAXWRITE = 1000000
min_heat_off = 0
min_humi_off = 0

utc = -8

while True: 
    response = urequests.get(addr + ':' + str(port) + '/' + endpoint) # Change Values in Boot
    data = response.text
    jsonParse = ujson.loads(data)
    ssid_new = jsonParse["uuid"]
    pw_new = jsonParse["password"]
    minTemp_new = jsonParse["minTemp"]
    maxTemp_new = jsonParse["maxTemp"]
    minHumid_new = jsonParse["minHumid"]
    maxHumid_new = jsonParse["maxHumid"]
    if WIFI_SSID != ssid_new or WIFI_PW != pw_new:
        try:
            connect_wifi(ssid_new, pw_new)
            WIFI_SSID = ssid_new
            WIFI_PW = pw_new
        except:
            pass
    if tempLimit != minTemp_new or tMax != maxTemp_new:
        if minTemp_new < maxTemp_new: # Replace errvals
            if minTemp_new > terrMin:
                tempLimit = minTemp_new
            if maxTemp_new < terrMax:
                tMax = maxTemp_new
    if humidLimit != minHumid_new or hMax != maxHumid_new:
        if minHumid_new < maxHumid_new: # Replace errvals
            if minHumid_new >= herrMin:
                humidLimit = minHumid_new
            if maxHumid_new <= herrMax:
                hMax = maxHumid_new
    # UUID and TimeDate
    postId = str(uuid.uuid4())
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

    dt = year + '-' + month + '-' + date + weekDay + hour + ':' + minute + ':' + sec + '.' + usec + 'Z'   # print vals

    try: # Check for sensor Error
        err = False
        temp = s.get_temp_humi()[0]
        humid = s.get_temp_humi()[1]
    except:
        err = True
        temp = "Error"
        humid = "Error"
        if not ton and (min_heat_off == 0 or min_heat_off == 1): # Revert immediately to switch timer
            ton = True
            heaterPin.off()
            min_heat_off = -1
        else:
            ton = False
            heaterPin.on()
        if not hon and (min_humi_off == 0 or min_humi_off == 5): # Revert immediately to switch timer
            hon = True
            humidiPin.off()
            min_humi_off = -1
        else:
            hon = False
            humidiPin.on()
        iter += 1
        if iter == MAXWRITE + 1:
            iter = 1
        try:
            # WRITE SHT DATA HERE
            pub_msg("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"" + str(dt) + "\", \"temp_c\" : 0.0, \"temp_f\" : 32.0, \"humidity\" : 0.0}")
        except:
            f.write("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"2000-00-00M00:00.000Z\", \"temp_c\" : 0.0, \"temp_f\" : 32.0, \"humidity\" : 0.0}\n")
            iter += 1
            min_heat_off += 1
            min_humi_off += 1
            time.sleep(60)
            pass
        min_heat_off += 1
        min_humi_off += 1
        time.sleep(60)
        pass
    temp_f = (temp * 9.0 / 5.0) + 32.0
    tDiff = temp - prevTemp
    hDiff = humid - prevHumi

    # Don't remove, code seems to not work if you remove for some reason. Beats me... ¯\_(ツ)_/¯
    print("Breakpoint\n")

    # Let a run clear before we start writing -> Buffer write protocol
    if not firstRun:
        if temp > terrMax or temp < terrMin or tDiff > 5.0 or tDiff < -5.0 or err: # Check logic
            err = True
            if temp > terrMax or tDiff > 5.0: # Off first, interval will spike rates
                ton = False
                heaterPin.on()
            else:
                if not ton and (min_heat_off == 0 or min_heat_off == 1):
                    ton = True
                    heaterPin.off()
                    min_heat_off = -1
                else:
                    ton = False
                    heaterPin.on()
        else: # Normal processing
            if temp < tempLimit and prevTemp < tempLimit: # Turn on
                heaterPin.off()
                ton = True
            elif ton and temp < tMax and prevTemp < tMax: # On, but not at threshhold
                heaterPin.off()
                ton = True
            else: # Turn/keep off
                heaterPin.on()
                ton = False
        if humid > herrMax or humid < herrMin or hDiff > 5.0 or hDiff < -5.0 or err: # Check logic
            err = True
            if humid > herrMax or hDiff > 5.0: # Off first, interval will spike rates
                hon = False
                humidiPin.on()
            else:
                if not hon and (min_humi_off == 0 or min_humi_off == 5):
                    hon = True
                    humidiPin.off()
                    min_humi_off = -1
                else:
                    hon = False
                    humidiPin.on()
        else: # Normal processing
            if humid < humidLimit and prevHumi < humidLimit: # Turn on
                humidiPin.off()
                hon = True
            elif hon and humid < hMax and prevHumi < hMax: # On, but not at threshhold
                humidiPin.off()
                hon = True
            else: # Turn/keep off
                humidiPin.on()
                hon = False

    # Write back debouncer
    prevTemp = temp
    prevHumi = humid
    firstRun = False

    # Iterate
    if iter == MAXWRITE + 1:
        iter = 1
        f.close()
        os.remove('log.txt')
        f = open('log.txt', 'w')
        f.write("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"" + str(dt) + "\", \"temp_c\" : 0.0, \"temp_f\" : 32.0, \"humidity\" : 0.0}")

    try:
        # WRITE SHT DATA HERE
        pub_msg("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"" + str(dt) + "\", \"temp_c\" : " + str(temp) + ", \"temp_f\" : " + str(temp_f) + ", \"humidity\" : " + str(humid) + "}")
    except:
        # Write to log, we can't connect
        f.write("{\"postId\" : \"" + str(postId) + "\", \"postDate\" : \"2000-00-00M00:00.000Z\", \"temp_c\" : " + str(temp) + ", \"temp_f\" : " + str(temp_f) + ", \"humidity\" : " + str(humid) + "}\n")
        iter += 1
        pass

    # Error Sleep Delay
    if not err:
        time.sleep(1)
    else:
        min_heat_off += 1
        min_humi_off += 1
        time.sleep(60)
f.close()
