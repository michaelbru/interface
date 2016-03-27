import ComInterface
import serial
import sys
import logging
import util
class UartCom(ComInterface):
    """This class implements interface of astract Interface class for serial communication"""
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
            self._serialPort.open()


    def close(self):
        if self._serialPort != None:
         if self._serialPort.isOpen():
                self.serialPort.close()


    def setArray(self,toSend):
        self.setValue(toSend)

    def getArray(self):
        return self.getValue()

    def setValue(self,toSend,values):
        '''set value and send.
        toSend: list or str to send
        values: list or str to send
       if toSend and values are list then their length must be equal '''
        

    def getValue(self,cmd):
        raise NotImplementedError

    def sendCommand(self,command):
        pass


     # Send a string through a communication handle  
        # ToSend: The string to send 
    def SendString( self,ToSend , NodeId = None ) : 
        # Send a string         
        try:
            self._serialPort.write(ToSend.encode('ascii'))
        except IOError as ioe:
            logging.error(ioe)
        except Exception as ex:
            logging.error(ex)

        return 1,'' 
        

    #def SetArray( self , h , ToSend , Ind , Numval ,TimeOut = 0.030 , NodeId = None ) : 
    #    assert (type(ToSend) is str) and (type(Numval) is list) and (type(Ind) is list) and (len(Ind) == len(Numval)) , 'ToSend must be a string and the Ind and values be a lists of same length'
    #    Rslt = [0] * len(Numval)
    #    for cnt in range(len(Numval)) :
    #        Rslt[cnt] = self.SetValue(  h , ToSend + '[{0}]'.format(Ind[cnt]) , Numval[cnt] ,TimeOut  , NodeId  )

    #def GetArray( self , h , ToSend , Ind ,TimeOut = 0.030 , NodeId = None ) : 
    #    assert (type(ToSend) is str) and (type(Ind) is list) , 'ToSend must be a string and the Ind and values be a lists of same length'
    #    Rslt = [0] * len(Ind)
    #    for cnt in range(len(Ind)) :
    #        Rslt[cnt] = self.GetValue(  h , ToSend + '[{0}]'.format(Ind[cnt]),TimeOut  , NodeId  )
    #    return Rslt

    #def GetValue( self, h , ToSend , TimeOut = 0.03 , SimRslt = False ) : 
    #    # A list of strings to send - send them one by one 
    #    if SimRslt == False :
    #        Rslt,err = self.PingString( h , ToSend , TimeOut )
    #        Rslt =  util.decodeMessage(Rslt)
    #    try :
    #        return float(Rslt)
    #    #    if not Rslt.isdigit():              
    #    #        return Rslt
    #    #    Rslt = self.ToNum(Rslt) 
    #    #else:
    #    #    Rslt = SimRslt 
    #    #    #Err = [] 
    #    except ValueError as ve:
            
    #        return Rslt 

    ###############################################################################
    def PingString( self , ToSend , TimeOut = 0.030 , NodeId = None ):

        # A list of strings to send - send them one by one 
        if type(ToSend) is list : 
            ll = len(ToSend) 
            Rslt = [0] * ll 
            Err  = [0] * ll

            for cnt in range( len(ToSend)): 
                 Rslt[cnt],Err[cnt] = self.PingString(  ToSend[cnt] , TimeOut)  
            return Rslt,Err

        # A simple string 
        assert type(ToSend) is str , 'Object to send [' + repr(ToSend) +'] should be a string'

        #while ToSend[-1] in self.Termin:
        #    ToSend[-1] = ''
        #############################################
        #while ord(ToSend[-1]) in self.Termin:
        ToSend = util.decodeMessage(ToSend)
        ###############################################
        #self.KillString(h) 
        self._serialPort.flushInput()#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        stringhand,back = self.SendString( ToSend + ';') ; 
        bilbo = None 
        if stringhand != 'Done' : # Done only if answer is already collected 

            n =  max( int(TimeOut / 0.001) ,1 )
            for cnt in range(n) : 
                back =  self.CollectString( h )    
                if back == None: # Nothing yet, just wait 
                    time.sleep (0.001) 
                    continue
                if back == ToSend + ';' : #ignore echo 
                    bilbo = back 
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
            +'] for [' + ToSend + '] : ' + repr( self.GetComDescriptor(h) ) ) 
        else: 
            return (back,[]) 

          # Send a string through a communication handle 
        # h : Open communication handle 
        # ToSend: The string to send 
        # NodeId: (only relevant for CAN) Node ID. If None, the default node ID (see sct) is used
        def SendString(self,h, ToSend , NodeId = None , TimeOut = 0.1) : 
            # Send a string through the interface defined by h 
            assert h in self.handles.keys(),'Attempt to send a string to an unrecognized communication handle ['+repr(h)+']'
            if self.handles[h]['ComType'] == 'can':
                assert  self.handles[h]['CANType'] == 'kvaser' ,'Can interface of type ['+repr(self.handles[h]['CANType'])+'] is not supported'
                return 'Done', self.CanOpen.SetOsIntCmd(  h , ToSend , NodeId , TimeOut )

            if self.handles[h]['ComType'] == 'rs232':
                try:
                    self.handles[h]['SerialClass'].write(ToSend.encode('ascii'))
                except:
                    error('Cant write into a com port') 
            return 1,'' 
        

        def CollectBytes(self,h , N , tout = 0.03, ReadAnyway = False):
            if self.handles[h]['ComType'] == 'rs232': # for SCI 
                maxwait = max( 1 , int( tout / 0.001 )) 
                for cnt in range ( maxwait) :
                    nNext = self.handles[h]['SerialClass'].inWaiting() # Find the amount of newly recieved bytes 
                    if nNext >= N : 
                        return self.handles[h]['SerialClass'].read(N)   # and read N of them 
                    time.sleep( 0.001) ; 

                if ReadAnyway and (nNext > 0 )  :
                     return self.handles[h]['SerialClass'].read(nNext)   # and read them 
                else: 
                    return None
            else:
                error ( 'CollectString method only valid for SCI communication') 

 
        # Try to collect a string waiting at the serial communication output 
        def CollectString(self,h ):
            if self.handles[h]['ComType'] == 'rs232': # for SCI 
                nNext = self.handles[h]['SerialClass'].inWaiting() # Find the amount of newly recieved bytes 

                if nNext  : 
                    nNext = self.handles[h]['SerialClass'].inWaiting() # Find the amount of newly recieved bytes 
                    newStr = self.handles[h]['SerialClass'].read(nNext)   # and read them 
                    newStrA = newStr.decode('ascii') ; # put the newly read characters in the results buffer

                    # Place in the read buffer 
                    for cCnt in range(nNext) : 
                        c = newStrA[cCnt]
                        self.handles[h]['CharBuf'].push(c) 

                return self.handles[h]['CharBuf'].Rslt.fetch()

                retstr = None 

                if nNext ==  0 : 
                    return retstr 
            else:
                error ( 'CollectString method only valid for SCI communication') 
    