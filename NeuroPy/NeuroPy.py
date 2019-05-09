##Copyright (c) 2013, sahil singh
##
##All rights reserved.
##
##Redistribution and use in source and binary forms, with or without modification,
##are permitted provided that the following conditions are met:
##
##    * Redistributions of source code must retain the above copyright notice,
##      this list of conditions and the following disclaimer.
##    * Redistributions in binary form must reproduce the above copyright notice,
##      this list of conditions and the following disclaimer in the documentation
##      and/or other materials provided with the distribution.
##    * Neither the name of NeuroPy nor the names of its contributors
##      may be used to endorse or promote products derived from this software
##      without specific prior written permission.
##
##THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
##"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
##LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
##A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
##CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
##EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
##PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
##PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
##LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
##NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import serial
import time
import sys
import struct
import _thread as thread


SYNC = b'\xaa'
POOR_SIGNAL = b'\x02'
ATTENTION = b'\x04'
MEDITATION = b'\x05'
BLINK_STRENGTH = b'\x16'
RAW_VALUE = b'\x80'
ASIC_EEG_POWER = b'\x83'

class NeuroPy(object):
    __attention=0
    __meditation=0
    __rawValue=0
    __delta=0
    __theta=0
    __lowAlpha=0
    __highAlpha=0
    __lowBeta=0
    __highBeta=0
    __lowGamma=0
    __midGamma=0
    __poorSignal=0
    __blinkStrength=0

    srl=None
    __port=None
    __baudRate=None
 
    callBacksDictionary = {}  # keep a track of all callbacks
    running = True #here we mark it start running

    # Laziz - changed baud rate from 57600 to 9600 for Sichiray support
    # 9th of May 2019
    def __init__(self, port, baudRate=9600):
        platform = sys.platform
        print(platform)
        self.__port,self.__baudRate=port,baudRate
        self.__packetsReceived = 0

    def __del__(self):
        if self.running == True:
            self.running = False
        self.srl.close()

    #need stderr in python
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
    # disconnect function should be no longer needed as long as we stop the srl
    '''def disconnect(self):
        self.__srl.write(DISCONNECT) '''
    # connect function no longer needed, we will do it in the start function
    '''def connect(self):
        self.__connected = True
        return # Only connect RF devices
        self.__srl.write(''.join([CONNECT, self.__devid.decode('hex')])) '''

    def start(self):
        # Try to connect to serial port and start a separate thread
        # for data collection
        self.running = True
        # Laziz - Moved check into Try and corrected typo in Except blocks
        # 9th of May 2019
        try:
            self.srl=serial.Serial(self.__port)
            print("Mindwave has already started!")
        except serial.serialutil.SerialException:
            print("Mindewave could not start due to Serial Exception")
        thread.start_new_thread(self.__packetParser,(self.srl,))
        self.__packetsReceived = 0


    def __packetParser(self, srl):
        "packetParser runs continously in a separate thread to parse packets from mindwave and update the corresponding variables"
        while self.running:
            p1 = srl.read(1).hex()  # read first 2 packets
            p2 = srl.read(1).hex()
            while (p1 != 'aa' or p2 != 'aa'):
                p1 = p2
                p2 = srl.read(1).hex()
            else:
                if self.running == False:
                    break
                # a valid packet is available
                self.__packetsReceived += 1
                payload = []
                checksum = 0
                payloadLength = int(srl.read(1).hex(), 16)
                for i in range(payloadLength):
                    tempPacket = srl.read(1).hex()
                    payload.append(tempPacket)
                    checksum += int(tempPacket, 16)
                checksum = ~checksum & 0x000000ff
                if checksum == int(srl.read(1).hex(), 16):
                    i = 0

                    while i < payloadLength:
                        code = payload[i]
                        if (code == 'd0'):
                            print("Headset connected!")
                        elif (code == 'd1' or code == 'd2' or code == 'd3' or code == 'd4'):
                            eprint("Headset connection failed")
                        elif(code == '02'):  # poorSignal
                                i = i + 1
                                self.poorSignal = int(payload[i], 16)
                        elif(code == '04'):  # attention
                                i = i + 1
                                self.attention = int(payload[i], 16)
                        elif(code == '05'):  # meditation
                            i = i + 1
                            self.meditation = int(payload[i], 16)
                        elif(code == '16'):  # blink strength
                            i = i + 1
                            self.blinkStrength = int(payload[i], 16)
                        elif(code == '80'):  # raw value
                            i = i + 1  # for length/it is not used since length =1 byte long and always=2
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            self.rawValue = val0 * 256 + int(payload[i], 16)
                            if self.rawValue > 32768:
                                self.rawValue = self.rawValue - 65536
                        elif(code == '83'):  # ASIC_EEG_POWER
                            i = i + 1  # for length/it is not used since length =1 byte long and always=2
                            # delta:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.delta = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # theta:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.theta = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # lowAlpha:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.lowAlpha = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # highAlpha:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.highAlpha = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # lowBeta:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.lowBeta = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # highBeta:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.highBeta = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # lowGamma:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.lowGamma = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                            # midGamma:
                            i = i + 1
                            val0 = int(payload[i], 16)
                            i = i + 1
                            val1 = int(payload[i], 16)
                            i = i + 1
                            self.midGamma = val0 * 65536 + val1 * 256 + int(payload[i], 16)
                        else:
                            pass
                        i = i + 1


    def stop(self):
        # Stops a running parser thread
        if self.running == True:
            self.running = False
            self.__srl.close()

    def setCallBack(self, variable_name, callback_function):
        """Setting callback:a call back can be associated with all the above variables so that a function is called when the variable is updated. Syntax: setCallBack("variable",callback_function)
            for eg. to set a callback for attention data the syntax will be setCallBack("attention",callback_function)"""
        self.callBacksDictionary[variable_name] = callback_function

    # setting getters and setters for all variables
    # packets received
    @property
    def packetsReceived(self):
        return self.__packetsReceived

    @property
    def bytesAvailable(self, srl):
        if self.running:
            return srl.inWaiting()
        else:
            return -1

    # attention
    @property
    def attention(self):
        "Get value for attention"
        return self.__attention

    @attention.setter
    def attention(self, value):
        self.__attention = value
        # if callback has been set, execute the function
        if "attention" in self.callBacksDictionary:
            self.callBacksDictionary["attention"](self.__attention)

    # meditation
    @property
    def meditation(self):
        "Get value for meditation"
        return self.__meditation

    @meditation.setter
    def meditation(self, value):
        self.__meditation = value
        # if callback has been set, execute the function
        if "meditation" in self.callBacksDictionary:
            self.callBacksDictionary["meditation"](self.__meditation)

    # rawValue
    @property
    def rawValue(self):
        "Get value for rawValue"
        return self.__rawValue

    @rawValue.setter
    def rawValue(self, value):
        self.__rawValue = value
        # if callback has been set, execute the function
        if "rawValue" in self.callBacksDictionary:
            self.callBacksDictionary["rawValue"](self.__rawValue)

    # delta
    @property
    def delta(self):
        "Get value for delta"
        return self.__delta

    @delta.setter
    def delta(self, value):
        self.__delta = value
        # if callback has been set, execute the function
        if "delta" in self.callBacksDictionary:
            self.callBacksDictionary["delta"](self.__delta)

    # theta
    @property
    def theta(self):
        "Get value for theta"
        return self.__theta

    @theta.setter
    def theta(self, value):
        self.__theta = value
        # if callback has been set, execute the function
        if "theta" in self.callBacksDictionary:
            self.callBacksDictionary["theta"](self.__theta)

    # lowAlpha
    @property
    def lowAlpha(self):
        "Get value for lowAlpha"
        return self.__lowAlpha

    @lowAlpha.setter
    def lowAlpha(self, value):
        self.__lowAlpha = value
        # if callback has been set, execute the function
        if "lowAlpha" in self.callBacksDictionary:
            self.callBacksDictionary["lowAlpha"](self.__lowAlpha)

    # highAlpha
    @property
    def highAlpha(self):
        "Get value for highAlpha"
        return self.__highAlpha

    @highAlpha.setter
    def highAlpha(self, value):
        self.__highAlpha = value
        # if callback has been set, execute the function
        if "highAlpha" in self.callBacksDictionary:
            self.callBacksDictionary["highAlpha"](self.__highAlpha)

    # lowBeta
    @property
    def lowBeta(self):
        "Get value for lowBeta"
        return self.__lowBeta

    @lowBeta.setter
    def lowBeta(self, value):
        self.__lowBeta = value
        # if callback has been set, execute the function
        if "lowBeta" in self.callBacksDictionary:
            self.callBacksDictionary["lowBeta"](self.__lowBeta)

    # highBeta
    @property
    def highBeta(self):
        "Get value for highBeta"
        return self.__highBeta

    @highBeta.setter
    def highBeta(self, value):
        self.__highBeta = value
        # if callback has been set, execute the function
        if "highBeta" in self.callBacksDictionary:
            self.callBacksDictionary["highBeta"](self.__highBeta)

    # lowGamma
    @property
    def lowGamma(self):
        "Get value for lowGamma"
        return self.__lowGamma

    @lowGamma.setter
    def lowGamma(self, value):
        self.__lowGamma = value
        # if callback has been set, execute the function
        if "lowGamma" in self.callBacksDictionary:
            self.callBacksDictionary["lowGamma"](self.__lowGamma)

    # midGamma
    @property
    def midGamma(self):
        "Get value for midGamma"
        return self.__midGamma

    @midGamma.setter
    def midGamma(self, value):
        self.__midGamma = value
        # if callback has been set, execute the function
        if "midGamma" in self.callBacksDictionary:
            self.callBacksDictionary["midGamma"](self.__midGamma)

    # poorSignal
    @property
    def poorSignal(self):
        "Get value for poorSignal"
        return self.__poorSignal

    @poorSignal.setter
    def poorSignal(self, value):
        self.__poorSignal = value
        # if callback has been set, execute the function
        if "poorSignal" in self.callBacksDictionary:
            self.callBacksDictionary["poorSignal"](self.__poorSignal)

    # blinkStrength
    @property
    def blinkStrength(self):
        "Get value for blinkStrength"
        return self.__blinkStrength

    @blinkStrength.setter
    def blinkStrength(self, value):
        self.__blinkStrength = value
        # if callback has been set, execute the function
        if "blinkStrength" in self.callBacksDictionary:
            self.callBacksDictionary["blinkStrength"](self.__blinkStrength)

