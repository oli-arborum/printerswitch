# printerswitch
A small service to switch printer on and off via a TP-Link Smart WiFi Plug.

This is extremely useful if you have a printer that consumes (too) much power even in power-save or sleep mode (like my old HP Color LaserJet) and you want to have the printer available on the network (e.g. via AirPrint, see also my AirPrint tutorial under https://github.com/oli-arborum/tips-n-tricks/blob/master/airprint.md).

## Prerequisites
* `printerswitch` uses `lpstat` to query/poll the printer queue. Therefore, CUPS or any print spooler compatible with `lpstat` is required.
* `printerswitch` uses `tplink_smartplug.py` (see https://github.com/softScheck/tplink-smartplug) to switch the "TP-Link Smart WiFi Plug" which supplies power to the printer. `tplink_smartplug.py` needs to be in the search path.
* `printerswitch` optionally writes is status and error messages to the **systemd journal**. This of course works only on a system which uses systemd. Alternatively, `printerswitch` can be configured to write its messages to stdout/stderr.

## Configuration
### Get and test tplink-smartplug script
Firstly, get `tplink_smartplug.py` and make it executable for all users:
```
wget https://raw.githubusercontent.com/softScheck/tplink-smartplug/master/tplink_smartplug.py
chmod a+x tplink_smartplug.py
```
Now check if you can switch your TP-Link Smart WiFi Plug (replace "xxx.xxx.xxx.xxx" with the actual IPv4 address of your Smart Plug, use e.g. the DHCP lease table of you router to find it out):
```
./tplink_smartplug.py -t xxx.xxx.xxx.xxx -c on
./tplink_smartplug.py -t xxx.xxx.xxx.xxx -c off
```
### Adapt printerswitch configuration
Before installation you need to adapt `printerswitch.py` to your demands:
* Change the `PRINTER_NAME` to the name of the queue that is assigned to the printer that should be switched on and off.
* Change `SOCKET_IP_ADDR` to the IPv4 address of your TP-Link Smart WiFi Plug (see previous section).
* Optionally change `DELAY_PRINTER_OFF_S` to configure how long (in seconds) the printer shall be kept switched on after the print queue was detected as empty.
* Optionally set `USE_JOURNAL` to `False` to use stdout/stderr for status and error messages. (Useful for debugging and machines without systemd.)

## Installation
It is recommended to install `printerswitch` to `/usr/local/bin`.
```
sudo cp tplink_smartplug.py /usr/local/bin/
sudo cp printerswitch.py /usr/local/bin/
```
On machines with systemd you can use the provided unit file to run `printerswitch` as service:
```
sudo cp printerswitch.py /etc/systemd/system/
sudo systemctl start printerswitch.service
```
## Inspirations and acknowledgements
* first idea: https://www.raspberrypi.org/forums/viewtopic.php?t=45556
* switch TP-Link Smart WiFi plug from Python script: https://github.com/softScheck/tplink-smartplug
