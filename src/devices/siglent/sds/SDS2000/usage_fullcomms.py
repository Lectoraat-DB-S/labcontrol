from siglent_sds_scpi_full import SCPI, ch

# Stel socket-verbinding op (poort 5025 volgens manual). :contentReference[oaicite:9]{index=9}
scope_sock.write(SCPI["ROOT"]["*idn?"]())
resp = scope_sock.query(SCPI["WAVEFORM"]["preamble?"]())
# set CH1 scale
scope_sock.write(SCPI["CHANNEL"]["scale"](1, "5.00E-02"))
# read waveform from C2
scope_sock.write(SCPI)
data = scope_sock.query(SCPI["WAVEFORM"]["data?"]())
