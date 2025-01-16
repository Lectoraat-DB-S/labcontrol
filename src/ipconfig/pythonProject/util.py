import subprocess

def set_ip(interface_name, ip_address, subnet_mask, gateway):
    try:
        # Stel het IP-adres in
        subprocess.run(
            f'netsh interface ipv4 set address name="{interface_name}" static {ip_address} {subnet_mask} {gateway}',
            check=True, shell=True)
        print(f"IP-adres, subnetmasker en gateway voor {interface_name} zijn succesvol ingesteld.")
    except subprocess.CalledProcessError as e:
        print(f"Er is een fout opgetreden: {e}")

# Parameters instellen
interface_name = "Ethernet"  # Vervang dit door de naam van jouw interface
ip_address = "192.168.1.123"  # Vervang dit door het gewenste IP-adres
subnet_mask = "255.255.255.0"  # Vervang dit door het gewenste subnetmasker
gateway = "192.168.2.2"  # Vervang dit door het gewenste gateway-adres

# Roep de functie aan
set_ip(interface_name, ip_address, subnet_mask, gateway)