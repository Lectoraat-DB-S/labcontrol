import time
import socket
from collections import defaultdict
from scapy.all import rdpcap, TCP, IP, Raw

PCAP_FILE ="sds1202_turnon_connect.pcapng"

#PCAP_FILE = "sds1202xe_mathon.pcapng"
streams = defaultdict(list)
# TCP streams opslaan
def sendPCAPfile():
    

    print("PCAP laden...")
    packets = rdpcap(PCAP_FILE)

    print("Streams analyseren...")

    for p in packets:
        if IP in p and TCP in p and Raw in p:

            src = p[IP].src
            dst = p[IP].dst
            sport = p[TCP].sport +5
            dport = int(p[TCP].dport)
            dport = dport + 11


            key = (src, sport, dst, dport)

            timestamp = float(p.time)
            payload = bytes(p[Raw])

            streams[key].append((timestamp, payload))

    print(f"Aantal TCP streams gevonden: {len(streams)}")

# ---------------------------------------------------------
# replay functie
# ---------------------------------------------------------

def replay_stream(stream_key, packets, realtime=True):

    src, sport, dst, dport = stream_key

    print(f"\nReplay stream {src}:{sport} -> {dst}:{dport}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
    #sock.connect((dst, dport))
    sock.bind((src, sport))
    sock.connect((dst, dport))
    sock.connect((dst, 911))
    start_capture_time = packets[0][0]
    start_replay_time = time.time()

    for ts, payload in packets:

        if realtime:
            delay = (ts - start_capture_time) - (time.time() - start_replay_time)
            if delay > 0:
                time.sleep(delay)

        sock.sendall(payload)

    sock.close()

# ---------------------------------------------------------
# streams afspelen
# ---------------------------------------------------------

def playStreams():
    for stream_key, pktlist in streams.items():

        # sorteer op timestamp
        pktlist.sort(key=lambda x: x[0])

        try:
            replay_stream(stream_key, pktlist)

        except Exception as e:
            print("Replay error:", e)