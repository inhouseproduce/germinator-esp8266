# ESP8266

### Connection Instructions
  Connect GPIO Pin 4 to scl
  Connect GPIO Pin 5 to sda

### Flash Board
    esptool.py --port /dev/ttyUSB0 erase_flash
    esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 esp8266-lastUpdateLabel.bin

### Push file to esp
    ampy --port /dev/ttyUSB0 put boot.py
    ampy --port /dev/ttyUSB0 put main.py
    ampy --port /dev/ttyUSB0 put sht31.py

### Run the file (Local)
    ampy --port /dev/ttyUSB0 run main.py

### Direct shell
    miniterm.py /dev/ttyUSB0 115200 --dtr 0
    -- Press restart to boot

### From Scratch
### Tools
    pip install pyserial
    pip install pyparsing
    pip install esptool
    pip install virtualenv
    pip install adafruit-ampy
    brew install cmake ninja
    brew install ccache
    sudo pip3 install adafruit-circuitpython-sht31d

### Files
    README.md: Informational document containing all updates
    boot.py: Src code initializing pins and libraries to be run in main.py
    main.py: Src code for getting and sending data received from running  commands from sht31.py
    sht31.py: Python library code running and automating all data gathering in SHT31
    run.sh: pip install all necessary tools for the code and debugging
    Makefile: Simple makefile to run commands of above files and make everything easier

### Makefile Commands
    make: Runs put and then run on given PORT
    make run: Runs main.py on given PORT
    make put: Copies boot.py, main.py, and sht31.py to the ESP8266
    make get: gets the log of all outputs from temperature/humidity data and prints to your console for verification
    make clean: Removes all files from ESP8266
    make install: Runs run.sh
    make flash: Runs erase_fl, then write_fl
    make erase_fl: Erases and clears flash at PORT so it can be written again
    make write_fl: Writes flash to PORT with given BINFILE
    make reset: flashes, puts and screens the ESP8266

### AWS IoT MQTT Connection
    Code Based off of https://gist.github.com/StanS-AWS/a243ffac4fd19a3a8ab243633aa322db
    Start by going to Amazon MQTT and choosing IoT -> Onboard
    Select your OS and Python connection kit to speed-up the cloud thing registration
    Download connection kit, and run the connection test as prompted
    Run these four commands in your terminal:
        git clone https://github.com/aws/aws-iot-device-sdk-python.git
        python setup.py install
        curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
        python aws-iot-device-sdk-python/samples/basicPubSub/basicPubSub.py -e xxxxxxxxxxxxxx-ats.iot.xx-xxxx-x.amazonaws.com -r root-CA.crt -c xxxxxxxx.cert.pem -k xxxxxxxx.private.key
    Replace x as necessary
    In your IoT device's Manage->Devices->DevName, you can find all your needed files
    Subscribe to MQTT topic in 'Test': sdk/test/Python
    On ESP32, thus far is fine and no further steps are necessary; simply run the following:
        ampy -p /dev/ttyUSB0 put main.py
        ampy -p /dev/ttyUSB0 put xxxxxxxx.cert.pem
        ampy -p /dev/ttyUSB0 put xxxxxxxx.private.key 
    On ESP8266, the following extra commands are needed:
        openssl x509 -in Vita.cert.pem -out Vita.cert.der -outform DER
        openssl rsa -in Vita.private.key -out Vita.key.der -outform DER
        ampy -p /dev/ttyUSB0 put main.py
        ampy -p /dev/ttyUSB0 put xxxxxxxx.cert.der
        ampy -p /dev/ttyUSB0 put xxxxxxxx.key.der 
    Finally, simply restart the board
        screen /dev/ttyUSB0 115200 --dtr 0 
        import machine
        machine.reset()

### AWS MQTT to DynamoDB Connection
    In the AWS IoT console, in the navigation pane, choose Act.
    On the Rules page, choose Create.
    On the Create a rule page, enter a name and description for your rule.
    Under Rule query statement, choose the latest version from the Using SQL version list. For Rule query statement, enter:
        sdk/test/Python
    On Select an action, choose Insert a message into a DynamoDB table, and then choose Configure action.
    On Configure action, choose Create a new resource.
    On the Amazon DynamoDB page, choose Create table.
    On Create DynamoDB table, enter a name. 
        In Partition key, enter Row. 
        Select Add sort key, and then enter PositionInRow in the Sort key field. 
        Row represents a row in Excel. 
        PositionInRow represents the position of a cell in the row. 
        Choose String for both the partition and sort keys, and then choose Create. 
        It takes a few seconds to create your DynamoDB table. 
        Close the browser tab where the Amazon DynamoDB console is open. 
        If you don't close the tab, your DynamoDB table is not displayed in the Table name list on the Configure action page of the AWS IoT console.
    On Configure action, choose your new table from the Table name list. 
        In Partition key value, enter ${row}. 
        This instructs the rule to take the value of the row attribute from the MQTT message and write it into the Row column in the DynamoDB table. In Sort key value, enter ${pos}. 
        This writes the value of the pos attribute into the PositionInRow column. 
        In Write message data to this column, enter Payload. 
        This inserts the message payload into the Payload column. 
        Leave Operation blank. 
        This field allows you to specify which operation (INSERT, UPDATE, or DELETE) you want to perform when the action is triggered. 
        Choose Create a new role.
    In Create a new role, enter a unique name, and then choose Create role.
    Choose Add action.
    Choose Create rule.
    To test, simply attempt to send messages from the console
        Open the AWS IoT console and from the navigation pane, choose Test.
        Choose Publish to a topic. In the Publish section, enter sdk/test/Python. In the message area, enter the following JSON:
            { "row" : "0", "pos" : "0", "moisture" : "75" }
        This in our ESP8266 is formatted as:
            pub_msg("{\"row\" : \"0\", \"pos\" : \"1\", \"temp\" : \"23\"}")
            row 0 -> Limitation data
            pos 0 -> Temperature data
            pos 1 -> Humidity data
    Return to the DynamoDB console and choose Tables.
    Select your table, and then choose Items. Your data is displayed on the Items tab.

### DB IoT Integration
    Data will be set in a circular write-back loop taking in x values at most
    row 0 -> Limitation data
        pos 0 -> Temperature min limit
        pos 1 -> Temperature max limit
        pos 2 -> Humidity min limit
        pos 3 -> Humidity max limit
    row > 0 -> Sensor data
        pos 0 -> Temperature data
        pos 1 -> Heater Status
        pos 2 -> Humidity data
        pos 3 -> Humidifier Status
    These values will be read at a rate of one second per data read and the first sent value will take us some time
    main.py has been modified in order to accomodate for writing said temp data into the database
    Formatting is JSON
    Log file will no longer be a part of this project
    Initializer list must be reallocated to the boot.py file
    All loop sequences are in main.py

### AWS Limitation Notes
    Testing was done on mobile hotspot
    Double check all constraints
    Edit only constraint values, wifi connection, and MQTT topic

### AWS RDS Connection
    This connection was simply made by porting MQTT to S3
    Updates made logged in changelog.txt
    
### Remote Control
    Has been integrated under futureRelease folder with final delay times.
    Need to run NodeJS server with dedicated IP port connection and open socket. 
    Please edit variables only in boot.py
    Uses ujson and urequest which is a sublibrary of CPython's json and request library
    Please review
    Limitations is that ESP8266's Python code has volatile memory, so we will need to still adjust code based on wifi router
    We will need internet connection for this to work

### Instructions
    Go to the specific folder you are searching for and run the flash commands above
      Make sure to have your bin file for the specific flash in that folder
    Go to the folder you are searching for
      Refer to the notes for any prerequisites you may need to do before building the data
    Put all your build files into the ESP8266 using the put commands
    boot.py will run first, then main.py
    Use the screen command to monitor any progress happening with delays
    Note some of these will have latent start times

### Final notes
    See changelog for backlog history
    Most of this is simply pipelining data via RDS, the code should work in general, but heavily dependent
    Private key and certificates must be generated prior to uploading code and must be on the machine
    For further security, try to find a way to keep private key and certificate to be off the machine
    For general purposes, boot.py will handle any and all 

See release for latest files
See futureRelease for files with remote control enabled
