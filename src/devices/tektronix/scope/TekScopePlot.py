#set matplotlib as such it will reflect a Tektronix scope screen.
#orignal code made by Niels Boer
import matplotlib.pyplot as plt
from devices.tektronix.scope.Acquisitions import TekTrace
from devices.tektronix.scope.TekScopes import TekScope
from enum import Enum
import numpy as np

def setTekPlot(scope: TekScope):

    fig,ax = plt.subplots() #Scope view initialization 
    
    
    #first check if there are two traces to plot.
    if scope.CH1.isVisible and scope.CH2.isVisible:
        #create a plot with two traces 
        V_DIV_CH1 = scope.CH1.getLastTrace().V_DIV
        V_DIV_CH2 = scope.CH2.getLastTrace().V_DIV    
        timeData = scope.CH1.getLastTrace().scaledXData
        voltageDataCH1 = scope.CH1.getLastTrace().scaledYdata
        voltageDataCH2 = scope.CH2.getLastTrace().scaledYdata
        SEC_DIV = scope.CH1.getLastTrace().secDiv
        
        if V_DIV_CH1 > V_DIV_CH2: #Scaling CH2 with proper factor when vertical scale of CH1 is bigger
        
            fig.plot(timeData, voltageDataCH1, color='yellow')

            #for i in range(len(splitDataCH2)):
            #    graphVoltageCH2.append(voltageDataCH2[i]*(V_DIV_CH1/V_DIV_CH2))
            #Assume hold is true
            fig.plot(timeData, voltageDataCH2, color='cyan')
            ax.set_ylim(-4*V_DIV_CH1, 4*V_DIV_CH1) #Setting limit in vertical direction equal to 8 divisions of biggest vertical scale

            #Setting ticks in vertical direction 
            major_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1) #Making list for major ticks at each division 
            minor_yticks = np.arange(-4*V_DIV_CH1, 4*V_DIV_CH1, V_DIV_CH1/5) #Making list for minor ticks at each 1/5th of divsion 

            #Displaying ticks in vertical direction 
            ax.set_yticks(major_yticks)
            ax.set_yticks(minor_yticks, minor = True)
        elif V_DIV_CH2 > V_DIV_CH1: #Scaling CH1 with proper factor when vertical scale of CH2 is bigger
            fig.plot(timeData, voltageDataCH2, color='cyan')

            #for i in range(len(splitDataCH1)):
            #    graphVoltageCH1.append(voltageDataCH1[i]*(V_DIV_CH2/V_DIV_CH1)) 
            
            fig.plot(timeData, voltageDataCH1, color='yellow')
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
