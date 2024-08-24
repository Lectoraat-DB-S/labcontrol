#source by Niels Boer.
#merge request failed therefore copy/paste into main this way.

import pyvisa 
import matplotlib.pyplot as plt
import numpy as np

#Data declarations 
scopeDataCH1=[]
voltageDataCH1=[]
scopeDataCH2=[]
voltageDataCH2=[]
timeData=[]
graphVoltageCH1 = []
graphVoltageCH2 = []

#Using pyvisa resource manager
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Generator Initialization 
gen= rm.open_resource('USB0::0xF4ED::0xEE3A::SDG00002140678::INSTR')

#Generator assignment and Waveform Settings CH1
gen.write('C1:BSWV WVTP,SQUARE,FRQ,1e3HZ,AMP,1000e-3V,OFST,0V,DUTY,50')
gen.write('C1:OUTP ON')

#Generator assignment and Waveform Settings CH2
gen.write('C2:BSWV WVTP,RAMP,FRQ,1e3HZ,AMP,100e-3V,OFST,0V,DUTY,50')
gen.write('C2:OUTP ON')

#Osciloscope Initialization
scope = rm.open_resource('USB0::0x0699::0x0364::C054565::INSTR') #Copy and paste Oscilloscope ID here from 'NI-VISA Interactive Control' 

#Oscilloscope V/DIV and SEC/DIV Settings
scope.write ('HORIZONTAL:MAIN:SECDIV 2.5e-3') #Sets SEC/DIV #Already in Tekscope.
scope.write('CH1:SCALE 200e-3') #Sets V/DIV CH1 #added to TekChannel
scope.write('CH2:SCALE 20e-3') #Sets V/DIV CH2 #idem
scope.write('TRIGGER:MAIN:LEVEL 0') #Sets Trigger Level in V #integrated into Tekscope
scope.write('HORizontal:POSITION 0') #Sets Horizontal Position in s #moved2Tekscope

#Transfering scope data from CH1 to computer
scope.write("DATA:SOURCE CH1") #Sets CH1 as data source #integrated into Tekscope.
scope.write("DATA:ENCDG ASCII") #Sets the type of encoding for the data #Integrated into Tekscope
scope.write("DATA:WIDTH 1") #Sets data to use 1 byte for storing oscilloscope value  #moved2TekScope
scope.write("DATA:START 1") #Sets start of sample data 
scope.write("DATA:STOP 2500") #Sets end of sample data #both moved2Tekscope
print(scope.query('DATa?')) #Requesting settings for data transfer 
print(scope.query('WFMPRE?')) #Same as above, but with more information 

XZERO_CH1 = float(scope.query('WFMPRE:XZERO?')) #Requesting Horizontal Position value in s
XINCR_CH1 = float(scope.query('WFMPRE:XINCR?')) #Requesting multiplier for scaling time data
PT_OFF_CH1 = float(scope.query('WFMPRE:PT_OFF?')) #Requesting Trigger Offset in sample values

YZERO_CH1 = float(scope.query('WFMPRE:YZERO?')) #Requesting waveform conversion factor (Not sure what this is)
YMULT_CH1 = float(scope.query('WFMPRE:YMULT?')) #Requesting multiplier for scaling voltage data
YOFF_CH1 = float(scope.query('WFMPRE:YOFF?')) #Requesting vertical offset in V for calculating voltage

NR_PT =  int(scope.query('WFMPRE:NR_PT?')) #Requesting the number of samples 
SEC_DIV = float(scope.query('HORIZONTAL:MAIN:SECDIV?')) #Requesting the horizontal scale in SEC/DIV
V_DIV_CH1 = float(scope.query('CH1:SCALE?')) #Requesting the vertical scale of CH1 in V/DIV => 2TekScope


rawDataCH1 = scope.query('CURVE?') #Requesting the CSV data from CH1
splitDataCH1= rawDataCH1.split(',') #Turning the CSV data of CH1 into a list without comma seperated values

#Transfering scope from CH2 data to computer
scope.write("DATA:SOURCE CH2") #Sets CH2 as data source 
scope.write("DATA:ENCDG ASCII") #Sets the type of encoding for the data => 2TekScope
scope.write("DATA:WIDTH 1") #Sets data to use 1 byte for storing oscilloscope value 
scope.write("DATA:START 1") #Sets start of sample data 
scope.write("DATA:STOP 2500") #Sets end of sample data
print(scope.query('DATa?')) #Requesting settings for data transfer 
print(scope.query('WFMPRE?')) #Same as above, but with more information

#Not needed probably
#XZERO_CH2 = float(scope.query('WFMPRE:XZERO?'))
#XINCR_CH2 = float(scope.query('WFMPRE:XINCR?'))
#PT_OFF_CH2 = float(scope.query('WFMPRE:PT_OFF?'))

YZERO_CH2 = float(scope.query('WFMPRE:YZERO?')) #Requesting waveform conversion factor (Not sure what this is)
YMULT_CH2 = float(scope.query('WFMPRE:YMULT?')) #Requesting multiplier for scaling voltage data CH2
YOFF_CH2 = float(scope.query('WFMPRE:YOFF?')) #Requesting vertical offset in V for calculating voltage

V_DIV_CH2 = float(scope.query('CH2:SCALE?')) #Requesting the vertical scale of CH1 in V/DIV

rawDataCH2 = scope.query('CURVE?') #Requesting the CSV data from CH2
splitDataCH2 = rawDataCH2.split(',') #Turning the CSV data of CH2 into a list without comma seperated values

#Converting the raw voltage data acquired from CH1 to the correct voltage values for each sample 
for i in range(len(splitDataCH1)):
    scopeDataCH1.append(int(splitDataCH1[i]))
    voltageSampleCH1 = ((float(scopeDataCH1[i])-YOFF_CH1)*YMULT_CH1)+YZERO_CH1
    voltageDataCH1.append(voltageSampleCH1)

#Converting the raw voltage data acquired from CH2 to the correct voltage values for each sample
for i in range(len(splitDataCH2)):
    scopeDataCH2.append(int(splitDataCH2[i]))
    voltageSampleCH2 = ((float(scopeDataCH2[i])-YOFF_CH2)*YMULT_CH2)+YZERO_CH2
    voltageDataCH2.append(voltageSampleCH2)

#Converting the raw time data of each sample to the correct time values for each sample
for i in range(int(NR_PT)):
    timeSample = ((i-PT_OFF_CH1)*XINCR_CH1)+XZERO_CH1
    timeData.append(timeSample)

#Settings for displaying scope view
fig,ax = plt.subplots() #Scope view initialization 

if V_DIV_CH1 > V_DIV_CH2: #Scaling CH2 with proper factor when vertical scale of CH1 is bigger
    ax.plot(timeData, voltageDataCH1, color='yellow')

    for i in range(len(splitDataCH2)):
        graphVoltageCH2.append(voltageDataCH2[i]*(V_DIV_CH1/V_DIV_CH2))

    ax.plot(timeData, graphVoltageCH2, color='cyan')
    ax.set_ylim(-4*V_DIV_CH1, 4*V_DIV_CH1) #Setting limit in vertical direction equal to 8 divisions of biggest vertical scale

    #Setting ticks in vertical direction 
    major_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1) #Making list for major ticks at each division 
    minor_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1/5) #Making list for minor ticks at each 1/5th of divsion 

    #Displaying ticks in vertical direction 
    ax.set_yticks(major_yticks)
    ax.set_yticks(minor_yticks, minor = True)
elif V_DIV_CH2 > V_DIV_CH1: #Scaling CH1 with proper factor when vertical scale of CH2 is bigger
    ax.plot(timeData, voltageDataCH2, color='cyan')

    for i in range(len(splitDataCH1)):
        graphVoltageCH1.append(voltageDataCH1[i]*(V_DIV_CH2/V_DIV_CH1)) 

    ax.plot(timeData, graphVoltageCH1, color='yellow')
    ax.set_ylim(-4*V_DIV_CH2, 4*V_DIV_CH2)

    major_yticks = np.arange(-4*V_DIV_CH2, 4*V_DIV_CH2, V_DIV_CH2)
    minor_yticks = np.arange(-4*V_DIV_CH2, 4*V_DIV_CH2, V_DIV_CH2/5)

    ax.set_yticks(major_yticks)
    ax.set_yticks(minor_yticks, minor = True)

else: #No scaling correction needed as both vertical scales are the same
    ax.plot(timeData, voltageDataCH1, color='yellow')
    ax.plot(timeData, voltageDataCH2, color='cyan')
    ax.set_ylim(-4*V_DIV_CH1, 4*V_DIV_CH1)

    major_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1)
    minor_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1/5)

    ax.set_yticks(major_yticks)
    ax.set_yticks(minor_yticks, minor = True)

ax.set_xlim(timeData[0], timeData[len(timeData)-1]) #Limiting scope view to start time and stop time of the samples

#Making lists for displaying ticks in the horizontal direction 
major_xticks = np.arange(timeData[0], timeData[len(timeData)-1], abs(timeData[len(timeData)-1]-timeData[0])/10)
minor_xticks = np.arange(timeData[0], timeData[len(timeData)-1], abs(timeData[len(timeData)-1]-timeData[0])/50)

#Displaying ticks in horizontal direction 
ax.set_xticks(major_xticks)
ax.set_xticks(minor_xticks, minor = True)

#Changing major and minor tick settings to make an oscilloscope view
ax.tick_params(axis = 'both', which = 'major', labelsize = 0, color='gray', direction='inout', length=4)
ax.tick_params(axis = 'both', which = 'minor', labelsize = 0, color='gray', direction='inout', length=4)

#Changing the positions of the axes to make a cross for the oscilloscope view
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('center')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_color('none')

ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')

ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

#Setting border around oscilloscope view
ax.patch.set_edgecolor('gray')  
ax.patch.set_linewidth(1) 

#Displaying grid in oscilloscope view
ax.grid(which = 'major', alpha=0.3)

#Converting the requested V/DIV of CH1 to SI values and displaying it in scope view 
if V_DIV_CH1 >= 1:
    V_DIV_CH1_SCOPE = '{:4.2f}'.format(V_DIV_CH1)
    fig.text(0.20,0.075, 'CH1 ' + str(V_DIV_CH1_SCOPE) + 'V', ha='center', va='center',size='medium',color='yellow')
else:
    V_DIV_CH1_SCOPE = V_DIV_CH1*1e3
    V_DIV_CH1_SCOPE = '{:4.1f}'.format(V_DIV_CH1_SCOPE)
    fig.text(0.20,0.075, 'CH1 ' + str(V_DIV_CH1_SCOPE) + 'mV', ha='center', va='center',size='medium',color='yellow')

#Converting the requested V/DIV of CH2 to SI values and displaying it in scope view 
if V_DIV_CH2 >= 1:
    V_DIV_CH2_SCOPE = '{:4.2f}'.format(V_DIV_CH2)
    fig.text(0.375,0.075, 'CH2 ' + str(V_DIV_CH2_SCOPE) + 'V', ha='center', va='center',size='medium',color='cyan')
else: 
    V_DIV_CH2_SCOPE = V_DIV_CH2*1e3
    V_DIV_CH2_SCOPE = '{:4.1f}'.format(V_DIV_CH2_SCOPE)
    fig.text(0.375,0.075, 'CH2 ' + str(V_DIV_CH2_SCOPE) + 'mV', ha='center', va='center',size='medium',color='cyan')

#Converting the requested SEC/DIV to SI values and displaying it in scope view 
if SEC_DIV >= 1:
    SEC_DIV_SCOPE = '{:7.2f}'.format(SEC_DIV)
    fig.text(0.56,0.075, 'M' + str(SEC_DIV_SCOPE) + 's', ha='center', va='center',size='medium',color='white')

if SEC_DIV < 1 and SEC_DIV >= 1e-3:
    SEC_DIV_SCOPE = SEC_DIV*1e3
    SEC_DIV_SCOPE = '{:7.2f}'.format(SEC_DIV_SCOPE)
    fig.text(0.56,0.075, 'M' + str(SEC_DIV_SCOPE) + 'ms', ha='center', va='center',size='medium',color='white')

if SEC_DIV < 1e-3 and SEC_DIV >= 1e-6:
    SEC_DIV_SCOPE = SEC_DIV*1e6
    SEC_DIV_SCOPE = '{:7.2f}'.format(SEC_DIV_SCOPE)
    fig.text(0.56,0.075, 'M' + str(SEC_DIV_SCOPE) + u'\u03bc'+ 's', ha='center', va='center',size='medium',color='white')

if SEC_DIV < 1e-6 and SEC_DIV >= 5e-9:
    SEC_DIV_SCOPE = SEC_DIV*1e9
    SEC_DIV_SCOPE = '{:7.2f}'.format(SEC_DIV_SCOPE)
    fig.text(0.56,0.075, 'M' + str(SEC_DIV_SCOPE) + 'ns', ha='center', va='center',size='medium',color='white')

#Adding colours to scope view
ax.set_facecolor('black') #Setting background colour of scope view to be black
fig.patch.set_facecolor('#2337ba') #Setting colour of interface
