from NeuroPy import NeuroPy
import time
import datetime

# Initialise my headset
headset = NeuroPy.NeuroPy("COM6") #If baud rate not given, it's set automatically

# Call start method 
headset.start() 

# Provide output with each parameter and a time stamp
while True:
    time.sleep(0.5)
    print('My headset values: ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + \
        '\n\tAttention: {0}, \n\tMeditation: {1}, \n\tDelta: {2}, \n\tTheta: {3}, \
        \n\tLow Alpha: {4}, \n\tHigh Alpha: {5}, \n\tLow Beta: {6}, \
        \n\tHigh Beta: {7}, \n\tLow Gamma: {8}, \n\tMid Gamma: {9}\
        '.format(headset.attention, headset.meditation, headset.delta, headset.theta, headset.lowAlpha, headset.highAlpha, headset.lowBeta, headset.highBeta, headset.lowGamma, headset.midGamma))
    if(headset.meditation > 100):
        headset.stop() # You've reached Nirvana !!