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



for retry in range(3):
    print(f"Retry {retry + 1} / 3")
    with open("macs.txt", "rt") as fp:
        for line in fp:
            mac = line.strip()
            if mac:
                send_wol_packet(mac)
    print("sleeping for 30s...")
    sleep(30)

print("deep sleep for 3h")
machine.deepsleep(1000 * 60 * 60 * 3) 