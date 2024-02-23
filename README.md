# satel2mqtt-py
Python version of utility, that allows Satel CA-10 (and probably other older models) alarm system input events to publish to MQTT topic.
Rewritten to be used in Home Assistant. 

  
Required configuration on Satel CA10 -
Connected RS-232 port, enabled printing event log in central configuration.
Some of sensors should be changed to state SILENT only to report issues on the printer.
