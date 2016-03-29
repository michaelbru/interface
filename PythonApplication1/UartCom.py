import ComInterface
import serial
import sys
import logging
import Util
class UartCom(ComInterface):
    """This class implements interface of abstract Interface class for serial communication"""
    def __init__(self,port=0,baud=115200,parity = serial.PARITY_NONE ,timeout = 0.1):
            self._port = port
            self._parity = parity
            self._baud = baud
            self._timeout = timeout
            self._serialPort = None
            try:
                self.open()
            except Exception:
                 sys.exc_info
     
              
    def open(self):
            self.close()
            self._serialPort = serial.Serial()
            self._serialPort.port = self._port
            self._serialPort.baudrate = self._baud
            self._serialPort.timeout = self._timeout 
            self._serialPort.parity =  self._parity                  
            self._serialPort.open()


    def close(self):
        if self._serialPort != None:
         if self._serialPort.isOpen():
                self.serialPort.close()


    #def setArray(self,toSend):
    #    self.setValue(toSend)

    #def getArray(self):
    #    return self.getValue()

    #def setValue(self,toSend,values):
        '''set value and send.
        toSend: list or str to send
        values: list or str to send
       if toSend and values are list then their length must be equal '''
        

    def getValue(self,cmd):
        return self.PingString(command)

    def sendCommand(self,command):
        self.PingString(command)


     # Send a string through a communication handle  
        # ToSend: The string to send 
    def SendString( self,ToSend , NodeId = None ) : 
        # Send a string         
        try:
            self._serialPort.write(ToSend.encode('ascii'))
        except IOError as ioe:
            logging.error(ioe)
            return -1
        except Exception as ex:
            logging.error(ex)
            return -1
        return 1
        
    ###############################################################################
    def PingString( self , ToSend , TimeOut = 0.030 ):
        '''Allows to caller to send a command and retrive the answer '''
        # A list of strings to send - send them one by one 
        if type(ToSend) is list : 
            ll = len(ToSend) 
            Rslt = [0] * ll 
            Err  = [0] * ll
            for cnt in range( len(ToSend)): 
                 Rslt[cnt] = self.PingString(  ToSend[cnt] , TimeOut)  
            return Rslt  
        assert type(ToSend) is str , 'Object to send [' + repr(ToSend) +'] should be a string'      
        ToSend = Util.decodeMessage(ToSend)      
        self._serialPort.flushInput()# it is buffering. required to get the data out *now*
        stringhand = self.SendString(  Util.encodeMessage(ToSend) )        
        if stringhand : # Done only if answer is already collected 
            n =  max( int(TimeOut / 0.001) ,1 )
            for cnt in range(n) : 
                back =  self.CollectString()    
                if back == None: # Nothing yet, just wait 
                    time.sleep (0.001) 
                    continue
                if back == ToSend + ';' : #ignore echo                    
                    back = None 
                    time.sleep (0.001) 
                    continue    
                break # found a non-echo response, go for it 
            # Assert if timed out
            assert ( back != None )  ,'Time out waiting answer for [' + ToSend + '] : ' + repr( self.GetComDescriptor(h) ) 
         #There is something, decode it  
        if (back != None) and len(back) >= 2 and back[-2] in self.ErrTermin:
#               return ( [],back[:-1]) 
            assert False, (
            'Answered with error ['+ '0x{0:x}'.format(self.ToNum(back,ErrorTerminator='?'))
            +'] for [' + ToSend + '] : ' + repr( self.GetComDescriptor() ) ) 
        else: 
            return back

       

    def CollectBytes(self, N , tout = 0.03, ReadAnyway = False):   
            maxwait = max( 1 , int( tout / 0.001 )) 
            for cnt in range ( maxwait) :
                nNext = self._serialPort.inWaiting() # Find the amount of newly recieved bytes 
                if nNext >= N : 
                    return self._serialPort.read(N)   # and read N of them 
                time.sleep( 0.001) ; 

            if ReadAnyway and (nNext > 0 )  :
                    return self._serialPort.read(nNext)   # and read them 
            else: 
                return None
       
 
    # Try to collect a string waiting at the serial communication output 
    def CollectString(self):     
            nNext = self._serialPort.inWaiting() # Find the amount of newly recieved bytes 
            if nNext  : 
                nNext = self._serialPort.inWaiting() # Find the amount of newly recieved bytes 
                newStr = self._serialPort.read(nNext)   # and read them 
                newStrA = newStr.decode('ascii') ; # put the newly read characters in the results buffer
                return newStrA         
            return None 
       
        
    def ToNum(self, R , ErrorTerminator = None):
        if type(R) is list : 
            return  [self.ToNum ( R[cnt]) for cnt in range ( len(R ) ) ] 
        else: 

            if ord(R[-1]) in self.Termin: # Get rid of a possible terminator 
                R = R[:-1]
            if ErrorTerminator != None and R[-1] in ErrorTerminator: 
                R = R[:-1]

            assert type(R) is str ,'Should be a string : ' + repr(R) 
            try: 
                return  int(R) 
            except:
                try:
                    return  float(R) 
                except: 
                    try: 
                        return  int(R,16) 
                    except:
                        try:
                            return int(R,2) 
                        except: 
                            assert False,'Could not read a number out of [' + repr(R) + ']'
 