PORT=/dev/tty.SLAB_USBtoUART
BINFILE=esp8266-20191220-v1.12.bin
MAIN=main.py
LOGFILE=log.txt
DESKTOP_LOG=log_SHT31.txt
BOOT=boot.py
SHT31_DEP=sht31.py
BR=115200
TOOL=esptool.py
PY=ampy
INS=run.sh

default: put run

put:
	${PY} --port ${PORT} put ${MAIN}
	${PY} --port ${PORT} put ${BOOT}
	${PY} --port ${PORT} put ${SHT31_DEP}

run:
	${PY} --port ${PORT} run ${MAIN}

clean:
	${PY} --port ${PORT} rm ${MAIN}
	${PY} --port ${PORT} rm ${BOOT}
	${PY} --port ${PORT} rm ${SHT31_DEP}
	${PY} --port ${PORT} rm ${LOGFILE}
	rm ${DESKTOP_LOG}
	make test_clean

get:
	${PY} --port ${PORT} get ${LOGFILE} ${DESKTOP_LOG}
	cat ${DESKTOP_LOG}

install:
	chmod +x ${INS}
	./${INS}

flash: erase_fl write_fl

erase_fl:
	esptool.py --port ${PORT} erase_flash

write_fl:
	esptool.py --port ${PORT} --baud ${BR} write_flash --flash_size=detect 0 ${BINFILE}
