# 🕵️‍♂️ D31B1 - ARP Poison Tool (MitM)

**Herramienta de intercepción de tráfico y envenenamiento ARP (ARP Spoofing) desarrollada en Python.**

Este script permite realizar ataques de *Man-in-the-Middle* (MitM) interceptando la comunicación entre una víctima y la puerta de enlace (Gateway/Router) mediante la manipulación de las tablas ARP.

> **⚠️ Disclaimer:** Herramienta creada con fines estrictamente educativos para la asignatura de Seguridad Informática. El autor no se hace responsable del mal uso.

## 📋 Características
* **IP Forwarding Automático:** Habilita el reenvío de paquetes en el sistema atacante (Linux) para mantener la conexión a internet de la víctima.
* **Auto-Restauración:** Al finalizar el ataque (CTRL+C), la herramienta restaura automáticamente las tablas ARP originales de la víctima y el router para evitar cortes en la red.
* **Modo Silencioso:** Utiliza la librería `Scapy` para enviar paquetes ARP falsos de forma continua.

## ⚙️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/deiviRd18/D31B1-ARP-Poison.git](https://github.com/deiviRd18/D31B1-ARP-Poison.git)
   cd D31B1-ARP-Poison# D31B1-ARP-Poison
