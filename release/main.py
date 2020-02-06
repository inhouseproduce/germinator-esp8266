import time
import os

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
statHeat = "Off"
statHum = "Off"

# Iterators
iter = 1
MAXWRITE = 1000000

while True:
    try: # Check for sensor Error
        err = False
        temp = s.get_temp_humi()[0]
        humid = s.get_temp_humi()[1]
    except:
        err = True
        statHeat = "Error"
        statHum = "Error"
        temp = "Error"
        humid = "Error"
        if not ton: # Revert immediately to switch timer
            ton = True
            heaterPin.off()
        else:
            ton = False
            heaterPin.on()
        if not hon: # Revert immediately to switch timer
            hon = True
            humidiPin.off()
        else:
            hon = False
            humidiPin.on()
        iter += 1
        if iter == MAXWRITE + 1:
            iter = 1
        try:
            # WRITE SHT DATA HERE
            pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"0\", \"TempVal\" : \"" + str(temp) + "\"}")
            pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"1\", \"HeatStat\" : \"" + statHeat + "\"}")
            pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"2\", \"HumiVal\" : \"" + str(humid) + "\"}")
            pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"3\", \"HumiStat\" : \"" + statHum + "\"}")
        except:
            f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"0\", \"TempVal\" : \"" + str(temp) + "\"}\n")
            f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"1\", \"HeatStat\" : \"" + statHeat + "\"}\n")
            f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"2\", \"HumiVal\" : \"" + str(humid) + "\"}\n")
            f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"3\", \"HumiStat\" : \"" + statHum + "\"}\n")
            time.sleep(3600)
            pass
        time.sleep(3600)
        pass
    mem = gc.mem_free()
    tDiff = temp - prevTemp
    hDiff = humid - prevHumi

    # Let a run clear before we start writing -> Buffer write protocol
    if not firstRun:
        if temp > terrMax or temp < terrMin or tDiff > 5.0 or tDiff < -5.0 or err: # Check logic
            err = True
            if temp > terrMax or tDiff > 5.0: # Off first, interval will spike rates
                ton = False
                heaterPin.on()
            else:
                if not ton:
                    ton = True
                    heaterPin.off()
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
                if not hon:
                    hon = True
                    humidiPin.off()
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

    # Status Set
    if err: # Error still because checker
        statHeat = "Error"
        statHum = "Error"
    else: 
        if ton:
            statHeat = "On"
        else:
            statHeat = "Off"
        if hon:
            statHum = "On"
        else:
            statHum = "Off"

    # Write back debouncer
    prevTemp = temp
    prevHumi = humid
    firstRun = False

    # Iterate
    iter += 1
    if iter == MAXWRITE + 1:
        iter = 1

    try:
        # WRITE SHT DATA HERE
        pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"0\", \"TempVal\" : \"" + str(temp) + "\"}")
        pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"1\", \"HeatStat\" : \"" + statHeat + "\"}")
        pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"2\", \"HumiVal\" : \"" + str(humid) + "\"}")
        pub_msg("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"3\", \"HumiStat\" : \"" + statHum + "\"}")
    except:
        # Write to log, we can't connect
        f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"0\", \"TempVal\" : \"" + str(temp) + "\"}\n")
        f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"1\", \"HeatStat\" : \"" + statHeat + "\"}\n")
        f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"2\", \"HumiVal\" : \"" + str(humid) + "\"}\n")
        f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"3\", \"HumiStat\" : \"" + statHum + "\"}\n")
        pass

    # Error Sleep Delay
    if not err:
        time.sleep(1)
    else:
        time.sleep(3600)
f.close()
