# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:20:13 2023

@author: e47018kr
"""
#imports
from pylablib.devices import Thorlabs
import serial
import time as t
import struct
import pyvisa as visa
import numpy as np
import generatorCommands as gc
import datetime
import os
#hardware connections
relay = serial.Serial(port='COM4',baudrate=9600,timeout=0.1)
stageX = Thorlabs.KinesisMotor("27601599",scale = 34555)
stageY = Thorlabs.KinesisMotor("27601581",scale = 34555)

rm = visa.ResourceManager()
smu = rm.open_resource('GPIB1::10::INSTR')
smu.timeout = 60000
smu.write('reset()')
smu.write('errorqueue.clear()')

gc.takeRemoteControl(smu)
gc.closeShutter(smu)
#functions
def move_stage(x, y):
    # Simulated function to move the XY stage to the specified coordinates
    #print(f"Moving stage to ({x}, {y})")
    stageX.move_to(x)
    stageX.wait_move()
    stageY.move_to(y)
    stageY.wait_move()
    
def ardOssilaSw(pin_num, pin_state):
    relay.write(struct.pack('>BB',int(pin_num-1),int(pin_state)))
    t.sleep(1)
    data = relay.readline()
    return data

def measure_vs_time(t_on, t_off,t_all):
    currentStore = []
    timeStore = []

    time0 = t.time()
    timeout = time0 + t_all
    opened = False
    while True:
        
        current = np.array(smu.query_ascii_values('print(smua.measure.v(smua.nvbuffer1))'));    
        currentStore.append(current.item())
        
        time = t.time() - time0
        timeStore.append(time)
        
        if (time >= t_on) and (time < t_off)  and not opened:
            gc.openShutter(smu)
            opened = True
            
        if (time >= t_off) and opened:
            gc.closeShutter(smu)
            opened = False
            
        if t.time() > timeout:
            print('time out')
            break
        
    return currentStore, timeStore

def query_detector(x, y):
    #move detector to x y position
    move_stage(x, y)
    # Simulated function to query the detector for data at the specified coordinates
    #print(f"Querying detector at ({x}, {y})")
    currentStore_on = np.zeros(buffercount)
    smu.write('smua.measure.count = '+str(buffercount))
    smu.query_ascii_values('print(smua.measure.v(smua.nvbuffer1))')
    currentStore_on = np.array(smu.query_ascii_values('printbuffer(1, '+str(buffercount)+', smua.nvbuffer1.readings)'));
    # Simulate detector response and return the signal value and standard deviation
    signal = np.mean(currentStore_on)  #detector's response
    std_dev = np.std(currentStore_on)  # detector's characteristic standard error
    print('X:'+str(x)+',Y:'+str(y)+' Sig:'+str(signal)+'±'+str(std_dev))
    return signal, std_dev

def align_stage(init_x, init_y, learning_rate=0.01, precision=0.1):
    
    current_x = init_x  # Start at the middle of the XY stage
    current_y = init_y
    best_signal, _ = query_detector(current_x, current_y)
    #print('best signal '+str(best_signal))
    while True:
        signal, std_dev = query_detector(current_x, current_y)
        weight = 1 / std_dev if std_dev > 0 else 1  # Avoid division by zero

        gradient_x = weight * (query_detector(current_x + precision, current_y)[0] - best_signal) / precision
        gradient_y = weight * (query_detector(current_x, current_y + precision)[0] - best_signal) / precision

        move_x = learning_rate * gradient_x
        move_y = learning_rate * gradient_y
        if move_x > 1:
            move_x = 1
        if move_x < -1:
            move_x = -1
            
        if move_y > 1:
            move_y = 1
        if move_y < -1:
            move_y = -1    
            
        if abs(move_x) < precision and abs(move_y) < precision:
            break  # Stop if the movement is below the specified precision

        current_x -= move_x
        current_y -= move_y
        
        if current_x > 13.3:
            current_x = 13.3
        if current_x < -0.3:
            current_x = -0.3
        
        if current_y > 13.3:
            current_y = 13.3
        if current_y < -0.3:
            current_y = -0.3
            
        signal = query_detector(current_x, current_y)[0]

        if signal > best_signal:
            best_signal = signal
            print('best signal '+str(best_signal))

    # Move the stage to the best position
    move_stage(current_x, current_y)

    print(f"Alignment complete. Best position: ({current_x}, {current_y})")
    print(f"Best signal value: {best_signal}")
    return current_x, current_y
def grid_snake_query_detector(Xarr, Yarr):
    signal_grid = np.zeros([len(Xarr),len(Yarr)])
    #Create traversal grid
    xygrid = [(i,j) for j in Yarr for i in Xarr]
    #Iterate
    for iy in range(len(Yarr)):
        start_index = iy*len(Xarr)
        end_index = start_index + len(Xarr)
        row = xygrid[start_index:end_index]
        if iy % 2 == 1:
            row = row[::-1]
        for point in row:
            x = point[0]
            y = point[1]
            signal, std_dev = query_detector(x, y)
            ix = np.where(Xarr == x)[0]
            signal_grid[ix[0]][iy] = signal
    return signal_grid
def grid_query_detector(Xarr, Yarr):
    signal_grid = np.zeros([len(Xarr),len(Yarr)])
    for ix in range(len(Xarr)):
        x = Xarr[ix]
        for iy in range(len(Yarr)):
            y = Yarr[iy]
            signal, std_dev = query_detector(x, y)
            signal_grid[ix][iy] = signal
    return signal_grid
def align_stage_grid(init_x, init_y, precision_grid):
    midX = init_x
    midY = init_y
    aligned = False
    coarse_aligned = False
    fineloop = 0
    buffercount = 100
    smu.write('smua.measure.nplc = 10') 
    while not aligned:
        gc.openShutter(smu)
        for ip in range(len(precision_grid)):
            DX = precision_grid[ip][0]
            DY = precision_grid[ip][1]
            if ip == 0:
                while not coarse_aligned:
                    MinX = midX - DX
                    MaxX = midX + DX
                    MinY = midY - DY
                    MaxY = midY + DY
                    
                    if DY == 0:
                        Yarr = [MinY]
                    else:
                        Yarr = np.arange(MinY,MaxY+DY/2,DY)
                        
                    if DX == 0:
                        Xarr = [MinX]
                    else:
                        Xarr = np.arange(MinX,MaxX+DX/2,DX)
                    print('DX: '+str(DX)+' DY: '+str(DY))    
                    SigMatrix = grid_snake_query_detector(Xarr, Yarr)
                    argX, argY = np.unravel_index(np.argmax(SigMatrix),(len(Xarr),len(Yarr)))
                    if argX == 1:
                        coarse_aligned = True
                    midX = Xarr[argX]
                    midY = Yarr[argY]
            
            else:
                buffercount = 25
                smu.write('smua.measure.nplc = 5') 
                MinX = midX - DX
                MaxX = midX + DX
                MinY = midY - DY
                MaxY = midY + DY
                
                if DY == 0:
                    Yarr = [MinY]
                else:
                    Yarr = np.arange(MinY,MaxY+DY/2,DY)
                    
                if DX == 0:
                    Xarr = [MinX]
                else:
                    Xarr = np.arange(MinX,MaxX+DX/2,DX)
                print('DX: '+str(DX)+' DY: '+str(DY))        
                SigMatrix = grid_snake_query_detector(Xarr, Yarr)
                argX, argY = np.unravel_index(np.argmax(SigMatrix),(len(Xarr),len(Yarr)))
                fineloop = fineloop + 1
                if ((not(ip == 0)) and (argX == 1 and argY == 1)) or fineloop >= 3:
                    aligned = True
                midX = Xarr[argX]
                midY = Yarr[argY]
        gc.closeShutter(smu)
    return midX, midY       
            
## Main program
now = datetime.datetime.now()
samplename = 'MAPIB9S11'

xrayCurrent = 50
xrayVoltage = 25
voltage = 0
folderName = now.strftime("%Y-%m-%d_%H.%M")
outputPath = "C:\\Users\\ATLab2\\Desktop\\Kieran\\" + str(folderName) + ' ' + str(samplename) + '\\'
pins = [1,2,3,4,5,6,7,8]
#pins = [1,2]
for pin in pins:
    ardOssilaSw(pin, 1)
while True:    
    answer = input('is dark voltage low?')
    if answer.upper() == 'Y':
        break
for pin in pins:
    ardOssilaSw(pin, 0)
buffercount = 25  
  
delay = 0.02
t_on = 10
t_off = t_on+120
t_all = t_off+60
filedata = []
pinX = [1.00, 4.25, 6.00, 8.25, 8.25, 6.00, 4.25, 1.00]
pinY = [4.50, 4.50, 4.50, 4.50, 7.50, 7.50, 7.50, 7.50]
#flipped
#pinX = [8.75, 7.00, 6.00, 1.50, 1.50, 6.00, 7.00, 8.75]
#pinY = [8.00, 8.00, 8.00, 8.00, 4.50, 4.50, 4.50, 4.50]

precision_grid = [[1,0],[0.5,0.5],[0.25,0.25]]
newX = np.zeros(8)
newY = np.zeros(8)
for pin in pins:
    #keithley setting for alignment
    print('Pin: '+str(pin))
    smu.write('reset()')
    smu.write('errorqueue.clear()')           
    smu.write('smua.source.output = smua.OUTPUT_ON')
    smu.write('smua.measure.nplc = 5') # minimum in manual  1 PLC for 50 Hz is 20 ms (1/50) 1m to 25
    smu.write('smua.source.limitv = 1e-7')
    #smu.write('smua.measure.interval = 0.1')
    smu.write('smua.measure.count = '+str(buffercount))
    #smu.write('smua.source.levelv = 0')#'1e-3')
    #smu.query_ascii_values('print(smua.measure.i(smua.nvbuffer1))')
    
    ardOssilaSw(pin, 1)
    gc.openShutter(smu)
    #newX[pin-1], newY[pin-1] = align_stage(pinX[pin-1], pinY[pin-1])
    newX[pin-1], newY[pin-1] = align_stage_grid(pinX[pin-1], pinY[pin-1], precision_grid)
    move_stage(newX[pin-1], newY[pin-1])
    gc.closeShutter(smu)
    #keithley setting for time response
    t.sleep(90)
    smu.write('reset()')
    smu.write('errorqueue.clear()')

    smu.write('smua.measure.delay = ' + str(delay)) # settling time
    smu.write('smua.measure.nplc = 10') # minimum in manual
    currentStore, timeStore = measure_vs_time(t_on, t_off,t_all)
    
    ardOssilaSw(pin, 0)
    filedata.append(timeStore)
    filedata.append(currentStore)
maxlen = 0
for info in filedata:
    if len(info) > maxlen:
        maxlen = len(info) 
npfiledata=np.array(filedata)
dataout = np.zeros([16,maxlen])
for ip in range(len(pins)*2):
    linedata = np.array(npfiledata[ip])
    dataout[ip][0:len(linedata)] = linedata
if (os.path.exists(outputPath) == False):
    os.makedirs(outputPath)
outfilename = outputPath + samplename+str(xrayCurrent) + 'mA' + str(xrayVoltage) + 'kV'+ str(voltage) + 'V.csv'
np.savetxt(outfilename, dataout, delimiter=',')
