################################
## This program performs a wavelength sweep on a bentham monocromator,measurening the power ouput with a powermeter

from IPython import get_ipython
get_ipython().magic('reset -sf')

import os
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time as t
import datetime
import shutil
import subprocess as sp 
import serial
import struct
plt.clf()
#arduino = serial.Serial(port='COM4',baudrate=9600, timeout=.1)
# Funcitons used below
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
  #arduino.write(struct.pack('>BB',wheelnum,filternum))
  t.sleep(1)
  #data = arduino.readline()
  #return data  
def updatePlot (plt, wavelengths, readings):
  plt.scatter(wavelengths, readings)
  plt.ylim(np.min(readings), np.max(readings)*1.1)
  plt.pause(0.1)
  plt.clf()
  
def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False
################################
# Sweep parameters


#C:\Users\e47018kr\Documents\BenthamMonoSweep\c_codes\System-35838
wavelengths = np.arange(300, 750.1, 5)
mirrormode = 0  #1:UV, 0:vis+nir
grating = 0 #0: 2400lines/cm 1:1200lines/cm 2:600lines/cm, 0:200-750 1:250-1100 2:300-2000
Gset = [2400, 1200, 600]
nAve = 100
delayTime = 1 # 2.5seconds
wfilter = 0 # stepper 2 0: 0nm 1:400nm 2:800nm 3:1400nm
WFset = [0, 400, 800, 1400]
NDfilter = 0 #stepper 1 0: 0OD 1:0.3 2:1.0OD 3:2.0OD 4:3.0OD 5:4.0OD
NDFset = [0.0 ,0.3, 1.0, 2.0, 3.0, 4.0]

if mirrormode == 0:
    source = "IL1_" #visible+NIR
else:
    source = "IL6_" #uv

filters = ''    
if wfilter != 0:
    filters = filters + "LP" +str(WFset[wfilter])

filters = filters + "OD_ND" +str(NDFset[NDfilter])  + "G" + str(Gset[grating]) 

specs = source+str(min(wavelengths))+"_"+str(max(wavelengths))+"_"+filters
################################



moveWavelengthExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setWLbentham.exe"
flipMirrorExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\flipMirrorBentham.exe"
filterExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setFilterBentham.exe"

outputPath = "C:\\Users\\e47018kr\\Documents\\MonoSweepOutput\\"

now = datetime.datetime.now()
folderName = now.strftime("%Y-%m-%d-%H.%M")
outputFolder = "".join([outputPath, folderName])

outputFilename = "".join([outputFolder, "\\thorlabsS120VC_back ill_ sub_",specs,".csv"])
figureFilename = "".join([outputFolder, "\\figure",specs,".png"])

################################
# Initialise NewPort 818UV
rm = pyvisa.ResourceManager()
thorlabs=rm.open_resource('USB0::0x1313::0x8078::P0000235::INSTR')
thorlabs.timeout = 25000
thorlabs.read_termination = '\n'

#address = "GPIB0::8"
#lockin = SRS830.getLockin(address)

################################
# House keeping

if (os.path.exists(outputFolder) == False):
  os.makedirs(outputFolder)
else:
  #clearDirs = "y";
  #clearDirs = input("Clear directories? [y]/n: ")
  #if (clearDirs == "y"):
  shutil.rmtree(outputFolder)
  os.makedirs(outputFolder)

################################
# Set up mono
# 1) Flip mirror away from PMT, 2) move to the first wavelength and park the mono
filterSelect(6)

moveMono (wavelengths[0], 0, 1)   


################################
# Perform sweep

readings = np.zeros(wavelengths.size)
readingserr = np.zeros(wavelengths.size)

plt.plot(wavelengths, readings)
plt.xlim(np.min(wavelengths), np.max(wavelengths))

ii = 0;

signalAve = np.zeros(nAve)
filterSelect(1)
ardfilter(1,NDfilter)
ardfilter(2,wfilter)
for wavelength in wavelengths:
  moveMono (wavelength, 0, 0)
  #t.sleep(delayTime)
  waveStr = 'CORR:WAV '+str(int(wavelength))+'\n'
  thorlabs.write(waveStr)
  
  t.sleep(2.5)
  
  for ai in range(0,nAve):
      #flipMirror(mirrormode)
      signalAve[ai] = thorlabs.query('READ?')
 
  readings[ii]=np.average(signalAve)
  readingserr[ii]=np.std(signalAve)    
  #readings[ii] = SRS830.getR(lockin)

  print("Scanned wavelength: ", wavelength, readings[ii],readingserr[ii])
  updatePlot(plt, wavelengths, readings)  

  ii = ii+1
  
################################
# Produce output
filterSelect(6)
ardfilter(1,0)  
ardfilter(2,0)  
plt.plot(wavelengths, readings)
plt.xlim(np.min(wavelengths), np.max(wavelengths))
plt.ylim(np.min(readings), np.max(readings)*1.1)

plt.savefig(figureFilename)
plt.show()
  
################################
# Write output to file

np.savetxt(outputFilename, (wavelengths, readings,readingserr), delimiter=',')
