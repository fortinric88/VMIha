# VMI Ventilairsec custom integration

This folder contains a Home Assistant custom integration skeleton derived from the Jeedom backup content:
- Proprietary D1079 payload parsing based on the XML definitions from the backup
- Basic entity setup for sensors, select and number
- Config flow using the EnOcean serial port /dev/ttyS2 by default

To make this fully operational on a real Home Assistant installation, the serial transport layer must be completed so that incoming EnOcean telegrams are received and outgoing commands can be sent.
