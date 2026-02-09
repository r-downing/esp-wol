from machine import Pin
from utime import sleep
import network

import machine

import socket

wlan = network.WLAN(network.STA_IF)



def wol_packet(mac: str) -> bytes:
    return (b"\xff" * 6) + (bytes.fromhex(mac.replace(":", "")) * 16)



def get_broadcast_addr():
    if not wlan.isconnected():
        return ""
    
    ip_str, mask_str, _gw, _dns = wlan.ifconfig()
    
    ip = [int(i) for i in ip_str.split('.')]
    mp = [int(m) for m in mask_str.split('.')]
    

    return ".".join(str(ip[i] | (mp[i] ^ 255)) for i in range(4))

def send_wol_packet(mac):
    packet = wol_packet(mac)
    broadcast_addr = get_broadcast_addr()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        sock.sendto(packet, (broadcast_addr, 9))
        print(f"WoL Packet sent to {mac} via {broadcast_addr}")
    finally:
        sock.close()


import machine
import ujson

rtc = machine.RTC()

def save_to_rtc_8266(data):
    json_str = ujson.dumps(data)
    json_bytes = json_str.encode('utf-8')
    
    pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b' ' * pad
    
    rtc.memory(json_bytes)

def load_from_rtc_8266():
    data_bytes = rtc.memory()
    
    try:
        # Strip padding and decode
        return ujson.loads(data_bytes.decode('utf-8').strip())
    except Exception:
        return None


loaded = load_from_rtc_8266() or {}
if "deep_sleep" in loaded:
    sleep_time = min(loaded["deep_sleep"], 1000 * 60 * 30)
    loaded["deep_sleep"] -= sleep_time
    save_to_rtc_8266(loaded)

    machine.deepsleep(sleep_time)


for retry in range(3):
    print(f"Retry {retry + 1} / 3")
    with open("macs.txt", "rt") as fp:
        for line in fp:
            mac = line.strip()
            if mac:
                send_wol_packet(mac)
    print("sleeping for 30s...")
    sleep(30)

save_to_rtc_8266({"deep_sleep": 1000 * 60 * 60 * 3})
machine.reset()