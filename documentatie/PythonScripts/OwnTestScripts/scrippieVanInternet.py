# Keygen program for Siglent oscilloscopes
 
import hashlib
 
# You get this by running "SCOPEID?" at the SCIP prompt and removing the dashes
SCOPEID = '0000000000000000'
# Replace this with your SN
SN = 'SDS00000000000'
# This is one of the four options below
Model = 'SDS1000X-E'
# 'SDS1000X-E', 'SDS2000X-E', 'SDS2000X+', 'SDS5000X', 'ZODIAC-'
 
bwopt = ('25M', '40M', '50M', '60M', '70M', '100M', '150M', '200M',
         '250M', '300M', '350M', '500M', '750M', '1000M', 'MAX')
otheropt = ('AWG', 'WIFI', 'MSO', 'FLX',
            'CFD', 'I2S', '1553', 'FG', '16LA')
 
hashkey = '5zao9lyua01pp7hjzm3orcq90mds63z6zi5kv7vmv3ih981vlwn06txnjdtas3u2wa8msx61i12ueh14t7kqwsfskg032nhyuy1d9vv2wm925rd18kih9xhkyilobbgy'
 
def gen(x):
    h = hashlib.md5((
        hashkey +
        (Model+'\n').ljust(32, '\x00') +
        opt.ljust(5, '\x00') +
        2*(((SCOPEID if opt in bwopt else SN) + '\n').ljust(32, '\x00')) +
        '\x00'*16).encode('ascii')
    ).digest()
    key = ''
    for b in h:
        if (b <= 0x2F or b > 0x39) and (b <= 0x60 or b > 0x7A):
            m = b % 0x24
            b = m + (0x57 if m > 9 else 0x30)
        if b == 0x30:
            b = 0x32
        if b == 0x31:
            b = 0x33
        if b == 0x6c:
            b = 0x6d
        if b == 0x6f:
            b = 0x70
        key += chr(b)
    return key.upper()
 
for opt in bwopt:
    print('{:5} {}'.format(opt, gen(SCOPEID)))
for opt in otheropt:
    print('{:5} {}'.format(opt, gen(SN)))