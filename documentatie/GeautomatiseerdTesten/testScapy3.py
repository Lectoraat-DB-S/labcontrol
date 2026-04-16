from scapy.all import *
from scapy.all import IP, ICMP, TCP, sr1

dst = "192.168.1.240"
dport = 911
sport = 965


def drukDePCAPFileOverInternet():
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

    pcap_file = "sds1202xe_mathon.pcapng"

    # Lees alle pakketten uit het pcap bestand
    packets = rdpcap(pcap_file)

    sendp(packets, iface="Ethernet")

    # data sturen
    """
    payload = b"example"
    pkt = IP(dst=dst)/TCP(
        sport=sport,
        dport=dport,
        flags="PA",
        seq=synack.ack,
        ack=synack.seq + 1
    )/payload

    send(pkt)"""