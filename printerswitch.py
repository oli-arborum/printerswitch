#!/usr/bin/env python3

'''
MIT License

Copyright (c) 2021 Oliver Baum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
'''

##############################################################################
# configuration is done here

# name of printer queue
PRINTER_NAME = "HP-Color-LaserJet-CP1215"
# IP address of TP-Link WiFi socket
SOCKET_IP_ADDR = "192.168.1.220"
# delay for switching printer off after queue is empty (in seconds)
DELAY_PRINTER_OFF_S = 600 # 10 min
# use journal for logging
USE_JOURNAL = True

# end of configuration
##############################################################################

socket_switch_exec = "tplink_smartplug.py"

import subprocess
import logging
import time
if USE_JOURNAL:
    from systemd import journal

log = logging.getLogger("printerswitch")

def lenPrinterQueue():
    '''return length of printer queue for PRINTER_NAME or None if error'''
    p = subprocess.run(["lpstat", "-o", PRINTER_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        log.error(f"'lpstat' call returned with {p.returncode}; stderr: '{p.stderr.decode().strip()}'")
        return None
    queue_string = p.stdout.decode().strip()
    if len(queue_string) == 0:
        return 0
    queue_list = queue_string.split("\n")
    return len(queue_list)

def printerOn():
    '''switch printer socket on, return False on error'''
    p = subprocess.run([socket_switch_exec, "-t", SOCKET_IP_ADDR, "-c", "on"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        log.error(f"printerOn: '{socket_switch_exec}' call returned with {p.returncode}; stderr: '{p.stderr.decode().strip()}'")
        return False
    return True

def printerOff():
    '''switch printer socket off, return False on error'''
    p = subprocess.run([socket_switch_exec, "-t", SOCKET_IP_ADDR, "-c", "off"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        log.error(f"printerOff: '{socket_switch_exec}' call returned with {p.returncode}; stderr: '{p.stderr.decode().strip()}'")
        return False
    return True


### main ###
# configure logger
if USE_JOURNAL:
    log.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER="printerswitch"))
    log.setLevel(logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO)

log.info("printerswitch started")

lastTimeQueueNotEmpty = 0
printerPower = False # start with printer switched off
queueEmpty = True # state machine for log outputs

try:
    while True:
        lpq = lenPrinterQueue()
        if lpq is not None:
            # only change state if querying printer queue did not fail
            if lpq > 0:
                if queueEmpty:
                    log.info(f"non-empty queue detected: {lpq} jobs")
                    queueEmpty = False
                # queue not empty: reset timer and switch printer on, if switched off
                lastTimeQueueNotEmpty = time.time()
                if not printerPower:
                    log.info("switching printer power on")
                    if printerOn():
                        printerPower = True
            else:
                if not queueEmpty:
                    log.info("empty queue detected")
                    queueEmpty = True
                # queue empty: check if delay passed and switch printer off, if switched on
                if printerPower and time.time() - lastTimeQueueNotEmpty > DELAY_PRINTER_OFF_S:
                    if printerOff():
                        log.info("switching printer power off")
                        printerPower = False
        time.sleep(30)
except Exception as e:
    log.error(f"caught exception: {e!r}")
except KeyboardInterrupt:
    log.error(f"caught KeyboardInterrupt!")
log.info("exiting")

