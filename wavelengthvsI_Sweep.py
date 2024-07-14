################################
## This program performs a wavelength sweep on a bentham monocromator,and meaeured the photcurretn rspinse of devices with a SMU

from IPython import get_ipython
get_ipython().magic('reset -sf')

import os
import visa
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import serial
import struct
import time as t
import datetime
import shutil
import subprocess as sp 


plt.clf()
arduino = serial.Serial(port='COM4',baudrate=9600, timeout=.1)
arduino2 = serial.Serial(port='COM5',baudrate=9700, timeout=.1)
################################
# Funcitons used below
def moveMono (wavelength, delay, park):
  proc = sp.Popen([moveWavelengthExe, str(wavelength), str(delay), str(park)], shell=True)
  proc.wait()
  
def flipMirror (position):
  # 0 for straight through, 1 for side exit
  sp.Popen([flipMirrorExe, str(position)], shell=True)
  
def updatePlot (plt, wavelengths, readings,pins):
  for pin in pins:
    ip = pins.index(pin)
    plt.scatter(wavelengths, readings[ip][:],label = ("Pin "+str(pin)))
 
  plt.ylim(np.min(readings), np.max(readings)*1.1)
  plt.pause(0.1)
  plt.clf()
  
def filterSelect (position):
  # 0 for straight through, 1 for side exit
  sp.Popen([filterExe, str(position)], shell=True)  
  
def ardfilter(wheelnum,filternum):
  arduino.write(struct.pack('>BB',wheelnum,filternum))
  t.sleep(1)
  data = arduino.readline()
  #return data
def ardOssilaSw(pin_num,pinstate):
  arduino2.write(struct.pack('>BB',int(pin_num-1),int(pinstate)))
  t.sleep(1)
  data = arduino2.readline()
  #return data
################################
#file locations
#rm = visa.ResourceManager()

#lockin = rm.open_resource('USB0::0xB506::0x2000::002881::INSTR')

moveWavelengthExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setWLbentham.exe"
flipMirrorExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\flipMirrorBentham.exe"
filterExe = "C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\setFilterBentham.exe"
outputPath = "C:\\Users\\e47018kr\\Documents\\MonoSweepOutput\\"


# Mono parameters
wavelengths = np.flip(np.arange(300, 750.1, 5))
mirrormode = 0
grating = 1 #1:200-750 2:250-1100 3:300-2000
wfilter = 0#0:open, 1:400lp, 2:800lp, 3:1400lp
WFset = [0, 400, 800, 1400]
NDfilter = 0 #stepper 1 0: 0OD 1:0.3 2:1.0OD 3:2.0OD 4:3.0OD 5:4.0OD
NDFset = [0.0 ,0.3, 1.0, 2.0, 3.0, 4.0]
#filter name
filters = ''    
if wfilter != 0:
    filters = filters + "LP" +str(WFset[wfilter])
if NDfilter != 0:
    filters = filters + "_ND" +str(NDFset[NDfilter])   

###################################
#editing grating and mirror setting by overwriting file System-35838.atr. DO NOT EDIT System-35838_base.atr
wmin = min(wavelengths)
#if grating == 1 and (min(wavelengths) < 200 or max(wavelengths)>750):
mono_id = str(min(wavelengths))+"_"+str(max(wavelengths))+"_" + filters + "_G" + str(grating)
#Keithley settings    
nAve = 25
delayTime = 5
delayTimeG = 5
 # seconds
voltage = 5
pins = [1]#,2,3,4,5,6,7,8]
#sample name
batch = 7
sample = 2
pin = 1
sample_id = "MAPI_B"+str(batch)+"S"+str(sample)+"P"+str(pin)
t.sleep(2.5)
#ardOssilaSw(int(pin),int(1))
t.sleep(5)
#source name
if mirrormode == 1:
    source = "IL6_"
else:
    source = "IL1_"

 



now = datetime.datetime.now()
folderName = now.strftime("%Y-%m-%d-%H.%M")
outputFolder = "".join([outputPath, folderName])

specs = sample_id+"_"+source+mono_id+"_"+str(voltage)+"V"
outputFilename = "".join([outputFolder, "\\output"+specs+".csv"])
figureFilename = "".join([outputFolder, "\\figure.png"])

################################
# Initialise Keithley through GPIB
rm = pyvisa.ResourceManager()
smu = rm.get_instrument('GPIB0::24::INSTR',send_end=False)
smu.timeout = 3000
smu.write("*RST")
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

#flipMirror(0)
moveMono (wavelengths[0],0,1)              # Park
flipMirror(mirrormode)
################################
# Perform sweep
signalAve = np.zeros(nAve)
readings = np.zeros([len(pins),wavelengths.size])
background = np.zeros(len(pins))
for pin in pins:
    ip = pins.index(pin)
    plt.plot(wavelengths, readings[ip][:],label = ("Pin "+str(pin)))
plt.xlim(np.min(wavelengths), np.max(wavelengths))
smu.write("OUTP ON") 
smu.write(":SOUR:VOLT "+"{:.3e}".format(voltage))
smu.write(":SENS:CURR:RANG:AUTO 0")
smu.write(":SENS:CURR:RANG:UPP 1e-4")#"4")

filterSelect(6)
t.sleep(delayTime)
for pin in pins:
    ip = pins.index(pin)

    ardOssilaSw(pin,1)
    t.sleep(delayTimeG)
    for ai in range(0,nAve): 
      signalAve[ai]=smu.query('READ?').split(',')[1].replace('+','0')

    background[ip]=-np.average(signalAve) 
    ardOssilaSw(pin,0)
#t.sleep(60)
ardfilter(1,NDfilter)
ardfilter(2,wfilter)

#filterSelect(1)
ii = 0;
#for NDnum in NDnums:
#    ardfilter(NDnum)
filterSelect(1)
for pin in pins:
    ip = pins.index(pin)
    #ardOssilaSw(pin,1)
    #t.sleep(delayTimeG)
    filterSelect(1)
    print('Pin '+str(pin))
    moveMono (wavelengths[0], 0, 1)
    for wavelength in wavelengths:
      ii = np.where(wavelengths == wavelength) 
      # if wavelength >= 400 and wavelength < 700:
      #     ardfilter(1,1)
      #     print('Switching to 400-700nm BP')
      # if wavelength >= 700:
      #     ardfilter(1, 2)
      #     print('Switching to 700-1100nm BP')
      #ardfilter(1,1)
      moveMono (wavelength, 0, 0)
      #t.sleep(1)
      #flipMirror(mirrormode)
      #SRS830.autoScale(lockin)
    
      t.sleep(delayTime)
      
      for ai in range(0,nAve):    
        signalAve[ai]=smu.query('READ?').split(',')[1].replace('+','0') 
      #filterSelect(6)
      readings[ip,ii]=(np.average(signalAve)) #- background[ip]
      #readings[ii] = SRS830.getR(lockin)
    
      print("Scanned wavelength: ", wavelength, readings[ip,ii])
      updatePlot(plt, wavelengths, readings, pins)
    #ardOssilaSw(pin,0)
    filterSelect(6)

  #ii = ii+1
filterSelect(6)  
################################
# Produce output
  
for pin in pins:
    ip = pins.index(pin)
    plt.plot(wavelengths, readings[ip][:],label = ("Pin "+str(pin)))
plt.legend()
plt.xlim(np.min(wavelengths), np.max(wavelengths))
plt.ylim(np.min(readings), np.max(readings))


for pin in pins:
    ip = pins.index(pin)
    print('Pin '+str(pin)+':')
    print('Max Photocurrent: ', np.max(readings[ip][:]))
    print('Max Photocurrent Wavelength: ', wavelengths[readings[ip][:].argmax()])
plt.savefig(figureFilename)
plt.show()
filterSelect(6)
ardfilter(1,0)
ardfilter(2,0)
#arduino.close()
#arduino2.close()
################################
# Write output to file
smu.write(":SOUR:VOLT "+"{:.3e}".format(0))
smu.write('beeper.beep(1, 1500)')
Pinheader = 'Wavelength'
for pin in pins:
    Pinheader = Pinheader +', Pin '+str(pin)
data = np.concatenate((wavelengths.reshape([1,wavelengths.size]),readings))
np.savetxt(outputFilename, np.transpose(data), delimiter=',',header=Pinheader)
