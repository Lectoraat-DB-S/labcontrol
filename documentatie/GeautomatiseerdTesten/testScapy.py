
from scapy.all import *
from scapy.utils import rdpcap
from scapy.all import IP, ICMP, sr1


global src_ip, dst_ip
src_ip = "192.168.1.226"
dst_ip = "192.168.1.240"

infile = "sds1202xe_mathon.pcapng"

def my_send(rd, count=100):
    pkt_cnt = 0
    p_out = []

    for p in rd:
        pkt_cnt += 1
        np = p.payload
       # np[IP].dst = dst_ip
       # np[IP].src = src_ip
        del np[IP].chksum
        p_out.append(np)
        if pkt_cnt % count == 0:
            send(PacketList(p_out))
            p_out = []

def sendMyPCAP():
    try:
        my_reader = PcapReader(infile)
        #del my_reader[IP].chksum
        my_send(my_reader)
    except IOError:
        print ("Failed reading file %s contents" % infile)
        sys.exit(1)


