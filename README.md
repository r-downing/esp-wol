# esp-wol

micropython code for a device to automatically send wake-on-lan packets. Used for restarting a server after a power outage.

GPIO16 must be connected to RST for the periodic deepsleep wake to work.