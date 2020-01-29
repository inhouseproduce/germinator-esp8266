import time
import os

# # Lims (REAL)
# tempLimit = 20.56
# tMax = 21.667
# humidLimit = 47.0
# hMax = 50.0
# terrMin = 10.0
# terrMax = 27.0
# herrMin = 40.0
# herrMax = 60.0

# Lims (False)
tempLimit = 30.0
tMax = 35.0
humidLimit = 95.0
hMax = 100.0
terrMin = 0.0
terrMax = 40.0
herrMin = 0.0
herrMax = 100.0

prevTemp = 0.0
prevHumi = 0.0
firstRun = True
hon = False
ton = False
err = False
tDiff = 0
hDiff = 0
# Log data
f = open('log.txt', 'w') 
f.write("Temp Max: " + str(tMax) + ", Temp Min: " + str(tempLimit) + "\n")
f.write("Humidity Max: " + str(hMax) + ", Humidity Min: " + str(humidLimit) + "\n---\n")

while True:
    temp = s.get_temp_humi()[0]
    humid = s.get_temp_humi()[1]
    mem = gc.mem_free()
    tDiff = temp - prevTemp
    hDiff = humid - prevHumi

    if not firstRun:
        if temp > terrMax or temp < terrMin or tDiff > 5.0 or tDiff < -5.0 or err:
            err = True
            f.write("Temperature (in Celsius): " + str(temp) + ", Previous Temp: " + str(prevTemp) + "\n")
            f.write("Error, temperature data error\n")
            if not ton:
                ton = True
                heaterPin.on()
            else:
                ton = False
                heaterPin.off()
        else: # Normal processing
            f.write("Temperature (in Celsius): " + str(temp) + ", Previous Temp: " + str(prevTemp) + "\n")
            if temp < tempLimit and prevTemp < tempLimit:
                heaterPin.on()
                ton = True
                f.write("Heater On\n-\n")
            elif ton and temp < tMax and prevTemp < tMax:
                f.write("Heater On\n-\n")
            else:
                heaterPin.off()
                ton = False
                f.write("Heater Off\n-\n")
        if humid > herrMax or humid < herrMin or hDiff > 5.0 or hDiff < -5.0 or err:
            err = True
            f.write("Humidity: " + str(humid) + ", Previous Humidity: " + str(prevHumi) + "\n")
            f.write("Error, humidity data error\n---\n")
            if not hon:
                hon = True
                humidiPin.on()
            else:
                hon = False
                humidiPin.off()
        else: # Normal processing
            f.write("Humidity: " + str(humid) + ", Previous Humidity: " + str(prevHumi) + "\n")
            if humid < humidLimit and prevHumi < humidLimit:
                humidiPin.on()
                hon = True
                f.write("Humidifier On\n---\n")
            elif hon and humid < hMax and prevHumi < hMax: 
                f.write("Humidifier On\n---\n")
            else:
                humidiPin.off()
                hon = False
                f.write("Humidifier Off\n---\n")
    prevTemp = temp
    prevHumi = humid
    firstRun = False

    if mem < 1000:
        f.close()
        os.remove('log.txt')
        f = open('log.txt', 'w')
        f.write("Temp Max: " + str(tMax) + ", Temp Min: " + str(tempLimit) + "\n")
        f.write("Humidity Max: " + str(hMax) + ", Humidity Min: " + str(humidLimit) + "\n---\n")

    if not err:
        time.sleep(1)
    else:
        time.sleep(3600)
f.close()