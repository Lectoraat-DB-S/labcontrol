from scapy.all import rdpcap, sendp
from scapy.all import get_if_list
from scapy.all import show_interfaces
from scapy.all import *
from scapy.all import IP, ICMP, TCP, sr1

print(get_if_list())
show_interfaces()
dst = "192.168.1.240"
dport = 911
sport = 965

pcap_file = "sds1202xe_mathon.pcapng"

def verstuurPCAPbestand():
    # Lees alle pakketten uit het pcap bestand
    packets = rdpcap(pcap_file)

    # Verstuur ze opnieuw op layer 2
    #sendp(packets, iface="eth0", inter=0)
    # Verstuur ze opnieuw op layer 2
    # SYN
    syn = IP(dst=dst)/TCP(sport=sport, dport=dport, flags="S", seq=1000)
    synack = sr1(syn)

    # ACK
    ack = IP(dst=dst)/TCP(
        sport=sport,
        dport=dport,
        flags="A",
        seq=synack.ack,
        ack=synack.seq + 1
    )

    send(ack)

    sendp(packets, iface="Ethernet")