from IPython import get_ipython
get_ipython().magic('reset -sf')

import pyvisa as visa
import time as t

import datetime
import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import serial
import struct
arduino = serial.Serial(port='COM6',baudrate=9600, timeout=.1)
import subprocess as sp 

#from sr865aConstants import *

timeConstants = np.array([1e-6,
                          3e-6,
                          10e-6,
                          30e-6,
                          100e-6,
                          300e-6,
                          1e-3,
                          3e-3,
                          10e-3,
                          30e-3,
                          100e-3,
                          300e-3,
                          1,
                          3,
                          10,
                          30,
                          100,
                          1e3,
                          3e3,
                          10e3,
                          30e3])

sensitivites = np.array([1,
                         500e-3,
                         200e-3,
                         100-3,
                         50e-3,
                         20e-3,
                         10e-3,
                         5e-3,
                         2e-3,
                         1e-3,
                         500e-6,
                         200e-6,
                         100e-6,
                         50e-6,
                         20e-6,
                         10e-6,
                         5e-6,
                         2e-6,
                         1e-6,
                         500e-9,
                         200e-9,
                         100e-9,
                         50e-9,
                         20e-9,
                         10e-9,
                         5e-9,
                         2e-9,
                         1e-9])
plt.close("all")

################################
# Funcitons used below

def threeTCdelay (frequency, lockin) :
  T = 1/frequency
  TC = np.where(timeConstants>(20*T))[0][0]  #3 was 5 
  if TC<9:
    TC = 9    
  lockin.write("OFLT %i" %TC)
      
  delay = timeConstants[TC]*10
  
  t.sleep(delay)

  
def updatePlot(realVStore, imagVStore,frequencies,jj):
  plt.clf()
  complexV = realVStore+(realVStore*1j)
  
  #plt.scatter3D((realVStore[1:jj])*1E6,(imagVStore[1:jj])*1E6,frequencies,cmap=plt.cm.Spectral)
  

  ax = plt.axes(projection='3d')
  if jj == 0:
    ax.plot3D((realVStore[0])*1E6, (imagVStore[0])*1E6, np.log10(frequencies[0]), 'gray')
    ax.scatter3D((realVStore[0])*1E6, (imagVStore[0])*1E6, np.log10(frequencies[0]))
    rlim = max((abs((realVStore[0])*1E6)),(abs((imagVStore[0])*1E6)))
  else:
    ax.plot3D((realVStore[0:jj])*1E6, (imagVStore[0:jj])*1E6, np.log10(frequencies[0:jj]), 'gray')
    ax.scatter3D((realVStore[0:jj])*1E6, (imagVStore[0:jj])*1E6, np.log10(frequencies[0:jj]))
    rlim = max(max(abs((realVStore[0:jj])*1E6)),max(abs((imagVStore[0:jj])*1E6)))

  
  ax.set_xlim(-rlim, rlim) 
  ax.set_ylim(-rlim, rlim)
  ax.set_zlim(min(np.log10(frequencies)), max(np.log10(frequencies)))
  ax.set_xlabel('Real V (microV)')
  ax.set_ylabel('Imag V (microV)')
  ax.set_zlabel('log(Frequency (Hz))')
  #ax.set_zscale('log')
  

  
  #plt.xlabel('Real V (microV)')
  #plt.ylabel('Imag V (microV)')
  #plt.zlabel('Frequency (Hz)')

  plt.pause(0.001)
  return complexV

def moveMono (wavelength, delay, park):
  proc = sp.Popen([moveWavelengthExe, str(wavelength), str(delay), str(park)], shell=True)
  proc.wait()
  
def flipMirror (position):
  # 0 for straight through, 1 for side exit
  sp.Popen([flipMirrorExe, str(position)], shell=True)
  
def filterSelect (position):
  # 0 for straight through, 1 for side exit
  sp.Popen([filterExe, str(position)], shell=True)  
  
def ardfilter(wheelnum,filternum):
  arduino.write(struct.pack('>BB',wheelnum,filternum))
  t.sleep(1)
  data = arduino.readline()
  return data  
def updatePlot (plt, wavelengths, readings):
  plt.scatter(wavelengths, readings)
  plt.ylim(np.min(readings), np.max(readings)*1.1)
  plt.pause(0.1)
  plt.clf()
  
################################
# Begin script

rm = visa.ResourceManager()
lockin = rm.open_resource('USB0::0xB506::0x2000::002881::INSTR')
                           #USB0::0xB506::0x2000::002881::INSTR
freqGen = rm.open_resource('USB0::0x2A8D::0x8D01::CN61230079::INSTR')
 

moveWavelengthExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setWLbentham.exe"
flipMirrorExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\flipMirrorBentham.exe"
filterExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setFilterBentham.exe"

################################

outputPath = "C:\\Users\\e47018kr\\Documents\\Python Scripts"


wavelengths = [-1]#, 0, 550]#, 0, 450, 550, 650, 750];#np.arange(250, 750.1, 25)
mirrormode = 1
grating = 1
#nAve = 3
delayTime = 2.5 # seconds
wfilter = 0
NDfilter = 0.0

if mirrormode == 1:
    source = "IL6_"
else:
    source = "IL1_"

filters = ''    
if wfilter != 0:
    filters = filters + "LP" +str(wfilter)

filters = filters + "OD_ND" +str(NDfilter)   
filterSelect(1)
specs = source+str(min(wavelengths))+"_"+str(max(wavelengths))+"_"+filters
################################

now = datetime.datetime.now()
folderName = now.strftime("%Y-%m-%d-%H.%M")
outputFolder = "".join([outputPath, folderName, "MAPIB2S3",specs])
Nave = 5

if (os.path.exists(outputFolder) == False):
  os.makedirs(outputFolder)
else:
  print("Clearing directories")
  shutil.rmtree(outputFolder)
  os.makedirs(outputFolder)

###############################################################################
## Set sweep parameters

# Probe properties
shape = 'SIN'
amplitude = 0.02  #minimum 0.02  = peak to peak

voltage = 0# array of voltages, 0.36]#np.linspace(-1,1,7)
#voltages = [0, 0.2, 0.4, 0.6, 0.8, 1.07,0, -0.2]   

# log10 scale
startFrequency = np.log10(1*10**-1) #-0.3 #-0.3 # in Hz
stopFrequency = np.log10(1*10**6)
nFrequencySteps = 7*8+1
frequencies1 = np.logspace(startFrequency, stopFrequency, nFrequencySteps)

frequencies2 = np.logspace(stopFrequency, startFrequency, nFrequencySteps)
frequencies = np.append(frequencies1,frequencies2)
Nscale = 3
powersf = np.log10(frequencies)*Nscale
Navef = Nave*np.ones(len(frequencies))#np.fix(powersf-np.min(powersf)+1)
##############################################################################
## Perform sweep
Xave = np.zeros(int(np.max(Navef)))
Yave = np.zeros(int(np.max(Navef)))
realVStore = np.zeros((len(frequencies),len(wavelengths)))*np.nan
realVerrStore = np.zeros((len(frequencies),len(wavelengths)))*np.nan  
imagVStore =np.zeros((len(frequencies),len(wavelengths)))*np.nan 
imagVerrStore = np.zeros((len(frequencies),len(wavelengths)))*np.nan 
thetaStore = np.zeros((len(frequencies),len(wavelengths)))*np.nan 


now2 = datetime.datetime.now()
fileName2 = now2.strftime("-%H.%M")
outputFilename = "".join([outputFolder, "\\output_t",fileName2, "_", str(voltage),"V","_XYlockin.xlsx"])
# set FG parameters

freqGen.write("SOUR1:FREQ %.6f" %startFrequency)
freqGen.write("SOUR1:VOLT:OFFS 0.0")
freqGen.write('OUTP1:STAT 1')
freqGen.write("SOUR1:FUNC:SHAP %s" %shape)
freqGen.write("SOUR1:VOLT:UNIT VPP")
freqGen.write("SOUR1:VOLT %f" %amplitude)
freqGen.write("OUTP:SYNC 1" )
freqGen.write("OUTP1:LOAD INF")
freqGen.write("SOUR1:VOLT:OFFS %.2f" %voltage)
# step V
filterSelect(6)
ardfilter(1,0)
ardfilter(2,0)
#step frequency
iFreq = 0
for frequency in frequencies: 
    # Set lockin to appropriate input coupling
    if (frequency < 0.16) :
      lockin.write('ICPL DC')
    else :
      lockin.write('ICPL AC')  
    lockin.write('ICPL AC')  
       ########################
 # Are all lockin settings appropriate?
  
    if (frequency < 1000) :
      lockin.write('SYNC ON')
    else :
      lockin.write('SYNC OFF')
  
    # source the frequency
    freqGen.write("SOUR1:FREQ %.6f" %frequency)
    
    # hold while the lockin is unlocked, then wait 2 seconds
    t.sleep(2)
    unlocked = bool(int(str(lockin.query('LIAS? 3')).replace('\n','')))
    while unlocked:
      t.sleep(2)  
      unlocked = bool(int(str(lockin.query('LIAS? 3')).replace('\n','')))
      
    iWave = 0
    for wavelength in wavelengths:
        if wavelength == -1:
           filterSelect(6) 
        else:
           filterSelect(1)
           if wavelength == 0:
               ardfilter(1,2)#OD 1.0
           moveMono (wavelength, 0, 1)
        ii=0
        
    
          ########################
          # insert TC appropriate delay
        
        threeTCdelay(frequency, lockin)
          
        # input voltage range check
        vLevel = int(lockin.query('ILVL?'))
        vRange = int(lockin.query('IRNG?'))
        if (vLevel == 0) :
          lockin.write('IRNG %i' %(vRange+1))
        elif (vLevel == 4) :   
          lockin.write('IRNG %i' %(vRange-1))
         
        # sensitivity check
        sens = int(lockin.query('SCAL?'))
        underflow = float(lockin.query('OUTP? 2'))<(0.01*sensitivites[sens])
        overloaded = bool(int(str(lockin.query('LIAS? 0')).replace('\n',''))) or bool(int(str(lockin.query('LIAS? 1')).replace('\n','')))
        while (overloaded) :
          lockin.write('SCAL %i' %(sens-1))
          t.sleep(1)       
          sens = int(lockin.query('SCAL?'))
          overloaded = bool(int(str(lockin.query('LIAS? 0')).replace('\n',''))) or bool(int(str(lockin.query('LIAS? 1')).replace('\n','')))
        while (underflow) :
          lockin.write('SCAL %i' %(sens+1))
          t.sleep(1) 
          sens = int(lockin.query('SCAL?'))
          underflow = float(lockin.query('OUTP? 2'))<(0.01*sensitivites[sens])        
        
        ########################
        # Take readings
        Xave = np.zeros(Nave)
        Yave = np.zeros(Nave)
        for ir in range(0,Nave):
            t.sleep(2+1/frequency)
            Xave[ir],Yave[ir] = str(lockin.query("SNAP? 0,1")).replace('\n','').split(',')
        X = np.average(Xave)
        Xerr = np.std(Xave)
        Y = np.average(Yave)
        Yerr = np.std(Yave)
        R = 27 #ohms
        
        realV = float(X)
        imagV = float(Y)
        realVerr = float(Xerr)
        imagVerr = float(Yerr)
        
        realI = realV/R
        imagI = imagV/R
        realIerr = realVerr/R
        imagIerr = imagVerr/R
        print("Voltage: " + str(realV) + " " + str(imagV))
        theta = -np.arctan(imagV/realV) 
        
        realVStore[iFreq,iWave] = realV
        imagVStore[iFreq,iWave] = imagV
        realVerrStore[iFreq,iWave] = realVerr
        imagVerrStore[iFreq,iWave] = imagVerr
        thetaStore[iFreq,iWave] = theta
       
        #complexV = updatePlot(realVStore, imagVStore,frequencies,jj)
      
        print("v: %.2f" %(voltage))
        print("λ: " + str(wavelength))
        print("f: " + str(frequency))
        print("") 
        iWave = iWave + 1  
          

        ii=ii+1
    iFreq = iFreq + 1   
headers = []
headers.append('Frequency (Hz)')    
for wavelength in wavelengths:
    if wavelength == -1:
        headers.append('Dark')
    elif wavelength == 0:
        headers.append('Broad')
    else:
        headers.append( str(wavelength)+'nm')
        
freq = np.resize(frequencies,[len(frequencies),1])

outReal1 = np.append(freq,realVStore,axis = 1)
realVdf = pd.DataFrame(outReal1,columns=headers)

outImag1 = np.append(freq,imagVStore,axis = 1)
imagVdf = pd.DataFrame(outImag1,columns=headers)


with pd.ExcelWriter( outputFilename) as writer:
    realVdf.to_excel(writer, sheet_name="Real V", index=False)
    imagVdf.to_excel(writer, sheet_name="Imaginary V", index=False)
   
ardfilter(1,0)
ardfilter(2,0)

filterSelect(6)
freqGen.write('OUTP1:STAT 0')
print("Sweep finished")
