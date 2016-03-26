import struct
from ctypes import *
import canlib 
import inspect
import time
import sys
#CAN communication variable types 
#TypeLength = {'integer8': (1,True) , 'integer16':  (2,True) , 'integer32':  (4,True) , 'unsigned8' :  (1,False) , 'unsigned16': (2,False) , 'unsigned32': (4,False) ,'vis string': (-1,False)} 
#CAN communication variable types 
TypeLength = {'integer8': (1,True,'b') , 'integer16':  (2,True,'<h') , 'integer32':  (4,True,'<l') , 
              'unsigned8' :  (1,False,'B') , 'unsigned16': (2,False,'<H') , 'unsigned32': (4,False,'<L') ,'vis string': (-1,False,'B')} 
MapOpt = {'rx':{0x1400,0x1600,0x100},'tx':{0x1800,0x1a00,0x80}}

 

#CAN error flags of the KVASER library 
canStatusFlags = { 
  0: 'canOK' , 
 -1:  'canERR_PARAM' , 
 -2:  'canERR_NOMSG' , 
 -3:  'canERR_NOTFOUND' , 
 -4:  'canERR_NOMEM' , 
 -5:  'canERR_NOCHANNELS' , 
 -6:  'canERR_RESERVED_3' , 
 -7:  'canERR_TIMEOUT' , 
 -8:  'canERR_NOTINITIALIZED' , 
 -9:  'canERR_NOHANDLES' , 
 -10:  'canERR_INVHANDLE' , 
 -11:  'canERR_INIFILE' , 
 -12:  'canERR_DRIVER' , 
 -13:  'canERR_TXBUFOFL' , 
 -14:  'canERR_RESERVED_1' , 
 -15:  'canERR_HARDWARE ', 
 -16:  'canERR_DYNALOAD ', 
 -17:  'canERR_DYNALIB ', 
 -18:  'canERR_DYNAINIT' , 
 -19:  'canERR_NOT_SUPPORTED ', 
 -20:  'canERR_RESERVED_5 ', 
 -21:  'canERR_RESERVED_6 ', 
 -22:  'canERR_RESERVED_2 ', 
 -23:  'canERR_DRIVERLOAD ', 
 -24:  'canERR_DRIVERFAILED ', 
 -25:  'canERR_NOCONFIGMGR ', 
 -26:  'canERR_NOCARD ', 
 -27:  'canERR_RESERVED_7 ', 
 -28:  'canERR_REGISTRY ', 
 -29:  'canERR_LICENSE ', 
 -30:  'canERR_INTERNAL ', 
 -31:  'canERR_NO_ACCESS' , 
 -32:  'canERR_NOT_IMPLEMENTED' , 
 -33:  'canERR_DEVICE_FILE ', 
 -34:  'canERR_HOST_FILE ', 
 -35:  'canERR_DISK ', 
 -36:  'canERR_CRC' , 
 -37:  'canERR_CONFIG' , 
 -38:  'canERR_MEMO_FAIL ', 
 -39:  'canERR_SCRIPT_FAIL ', 
 -40:  'canERR_SCRIPT_WRONG_VERSION ', 
-41 : 'canERR__RESERVED  '
}
SdoAbortCode = { 
0x05030000:
   'Toggle bit not alternated.',
0x05040000: 
   'SDO protocol timed out.',
0x05040001: 
   'Client/server command specifier not valid or unknown.',
0x05040002: 
   'Invalid block size (block mode only).',
0x05040003: 
   'Invalid sequence number (block mode only).',
0x05040004: 
   'CRC error (block mode only)',
0x05040005: 
   'Out of memory',
0x06010000: 
   'Unsupported access to an object',
0x06010001: 
   'Attempt to read a write only object',
0x06010002: 
   'Attempt to write a read only object',
0x06020000: 
   'Object does not exist in the object dictionary',
0x06040041: 
   'Object can not be mapped to the PDO',
0x06040042: 
   'The number and length of the objects to be mapped would exceed PDO length',
0x06040043: 
   'General parameters incompatibilty reason',
0x06040047: 
   'General internal incompatibilty in the device',
0x06060000: 
   'Access failed due to an hardware error',
0x06070010: 
   'Data type does not match, length of service parameters does not match',
0x06070012: 
   'Data type does not match, length of service parameters is too high',
0x06070013: 
   'Data type does not match, length of service parameters is too low',
0x06090011: 
   'Sub-index does not exist',
0x06090030: 
   'Value range of parameters exceeded (only for write access)',
0x06090031: 
   'Value of parameters written too high',
0x06090032: 
   'Value of parameters written too low',
0x06090036: 
   'Maximum value is less then minimum value',
0x08000000: 
   'General error',
0x08000020: 
   'Data can not be transfered or stored to the application',
0x08000021: 
   'Data can not be transfered or stored to the application because of local\ncontrol',
0x08000022: 
   'Data can not be transfered or stored to the application because of the\npresent device state',
0x08000023: 
   'Object dictionary dynamic generation fails or no object dictionary is\npresent (e.g. object dictionary is generated from file and generation fails\nbecause of an file error)',
}

 

"""
Ingerited class, based on the Kvaser original canlib
The difference is by over-riding the original error checking by the routine ReadImmediateErrorCheck
so that no exception shall be raised if the receive buffer is empty
"""


def convertListToByteArray(lst,length=8):
    return bytearray(lst)


class MyCanLib(canlib.canlib) : 
    def __init__(self,debug=None) : 
        canlib.canlib.__init__(self,debug) 
        self.dll.canRead.argtypes = [c_int, POINTER(c_long), POINTER(None),
                                            POINTER(c_uint), POINTER(c_uint),
                                            POINTER(c_ulong)]
        self.dll.canRead.restype = c_short
        self.dll.canRead.errcheck = self.ReadImmediateErrorCheck

    def  ReadImmediateErrorCheck(self, result, func, arguments):
        if result == canlib.canERR_NOMSG or result >= 0 :
            return result
        raise canError(self, result)


class CAN_msg:
    def __init( self , CobId = 0 , Data = (0).to_bytes(8,'little') , dlc = 0 , cobTime = 0  ) : 
        seld.Data = Data  
        seld.CobId = CobId 
        seld.dlc = dlc 
        seld.CobTime = cobTime 


class CanOpenKvaserImpl(canlib.canlib):
    
    
    """This class is derived from canlib module.
    Its purpose is to incapsulate CanOpen format found above Can communication
    the next functions are created:
    openkvaser(ch,baud,flags)  - open channels (e.i.0 or 1")
    closekvaser
    """
    def __init__(self, debug=None):

        canlib.canlib.__init__(self,debug)
        #self.canLib = MyCanLib
        self.timeout=1
        self.nodeId = -1
        self.h = -1
        self.ch = -1
        pass


    def open(self,ch,baud=500000,flags=0):
        try:
           self.ch = ch
           self.h =  self.openChannel(ch,flags)
           self.h.setBusParams(baud)
           self.h.setBusOutputControl(canlib.canDRIVER_NORMAL)
           self.h.busOn()
        except (canlib.canError) as ex:
           # print ( ex )
           raise ex

    def close(self):
        try:
            self.h.busOff()
            self.h.close()
        except (canlib.canError) as ex:
           # print ( ex )
           raise ex

    def setNodeId(self,nodeId):
        self.nodeId = nodeId

    def getNodeId(self):
        return self.nodeId

    def pingCanMessage(self,msg ):
        try:
            self.h.write(self.ch+0x600,msg)
            #wait  = int(self.timeout/0.001)
            #while True :
                # id.value, msgList[:dlc.value], dlc.value, flag.value, time.value
           # retval = self.h.read(self.timeout)
            retval = 0,[1,2,3,4,5,6,7,8],8,32,152
            return retval  
                  
        except (canlib.canError) as ex:
           # print ( ex )
           raise ex


    def getbytePingCanMessage(self,msg):
             id, mesg, dlc, flg, tim = self.pingCanMessage(msg)
             if mesg==[]:
                 raise IndexError            
             return  convertListToByteArray(mesg)
    
    def AnalyzeSdoAbort( self, errcode): 
        try:
            return SdoAbortCode[ errcode ] ;
        except:
            return 'Unknow SDO abort code'


    def GetSdo(self , Index , SubIndex , TypeIn , AbortMsg = None , decode = True ): 
        # function [Value,AbortFlag,CobId,Data] = GetSdo( h , NodeId , Index , SubIndex , Type , Timeout )
        # Purpose: Get SDO 
        #
        # Arguments: 
        # h: Handle to opened communication port 
        # NodeId: Node ID
        # Index: Object index
        # SubIndex: Object sub index 
        # Type: Received data type, may be:		
        #                          'integer8'
        #                          'integer16'
        #                          'integer32'
        #                          'unsigned8'
        #                          'unsigned16'
        #                          'unsigned32'
        #                          'vis string'
        # Timeout: timeout [sec]
        # AbortMsg: Set to string if a faiure should abort with this string displayed
        #
        # Returns: 
        # Value: Array with received data, or abort code
        # AbortFlag: if 1 then abort code recieved, normaly 0
        # CobId: Received additional communication objects identifiers
        # Data : Received additional data

        #NodeId = self.GetNodeId(h , NodeId) 
        #ch = self.ComPars.handles[h]['ChannelNum']


        Type = TypeIn.lower()
        assert Type in TypeLength.keys() ,'SDO desired for ilegal type, found['+repr(Type)+'] , permitted: ' + repr(TypeLength.keys()) 
        msg =  (64).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(5,'little') # SDO upload init 
       
        try:
            msgRet = self.getbytePingCanMessage(msg)
        except Exception as ex:
            print ( ex )
            sys.exit(1)



        if msgRet[0] & 0x80 : 
            AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
            assert not( type(AbortMsg) is str), AbortMsg+ ': GetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( self.nodeId , Index , SubIndex) 
            return AbortCode,1 # Return error code + abort 
        if (((msgRet[0] & 0xe0 ) >> 5 ) != 2) or ( msgRet[1:4] != msg[1:4] ) : #Bad CCS, multiplexor does not fit 
            #error ('Bad response to SDO upload init') 
            print('Bad response to SDO upload init') 
        if msgRet[0] & 2 : #expedited upload 
            n = 4 - (( msgRet[0] >> 2 ) & 3 ) if ( msgRet[0] & 2 ) else 4 #get number of expedited bytes
            assert ( n >= TypeLength[Type][0] ) ,'No enough bytes in the return message for the desired data type' 
            if Type == 'vis string' :
                return msgRet[4:4+n].decode('ascii') ,0 
            return  struct.unpack_from(TypeLength[Type][2],msgRet,4)[0],0 #Return result, no abort 
        #Segmented
        buf =  (0).to_bytes(8,'little') # Stam 
        msg =  (0x60).to_bytes(8,'little')
        nDelivery = struct.unpack_from('L',msgRet,4)[0] if ( msgRet[0] & 1 ) else -1
        while True:
             
            try:
                msgRet = self.getbytePingCanMessage(msg)
            except Exception as ex:
                print ( ex )
                sys.exit(1)

            #msgRet = self.ComPars.CanComServer.PingCanMessage( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout ) 
            msg = (msg[0] ^ 0x10).to_bytes(1,'little') + msg[1:]
            if msgRet[0] & 0x80 : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0] # Return error code + abort 
                assert not ( type(AbortMsg) is str), AbortMsg+ ': GetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( NodeId , Index , SubIndex) 
                return AbortCode,1 # Return error code + abort 
            assert (msgRet[0] & 0xe0 ) == 0 , 'Bad response to SDO upload init' # scs error 
            n = 7 - (( msgRet[0] >> 1 ) & 7 )
            buf = buf + msgRet[1:n+1]
            if ( len( buf ) >= nDelivery + 8 ) or msgRet[0] & 1 : # Complete or already message length exceeded
                break

        nDelivery = len(buf)-8 if nDelivery < 0 else nDelivery
        assert nDelivery ==  len(buf)-8 and nDelivery >= TypeLength[Type][0],'Length of SDO upload not as expected'
        if Type == 'vis string' and decode:
            return buf[8:].decode('ascii') ,0 
        else:
            return buf[8:] ,0 
        return  struct.unpack_from(TypeLength[Type][2],buf,8)[0],0 #Return result, no abort 



        '''
    Send an SDO to CAN target 
    h     : Communication handle 
    NodeId: The target node ID (None for channel default) 
    Index, SubIndex : OD multiplexor 
    Data  : Numeric or string data 
    Type : A valid data type, refer TypeLength
    Timeout: Timeout for every SDO transmission (for strings making N messages, the total timeout is up to N*Timeout) 
    AbortMsg: If None, SDO abort will return with AbortCode, else it will throw an exception with the AbortMsg string
    returns: 
    AbortCode, SDO abort code if error, otherwise 0 

    '''
    def SetSdo( self ,Index , SubIndex  , data , Type  , AbortMsg = None ): 
        #NodeId = self.GetNodeId(h , NodeId) 
        #ch = self.ComPars.handles[h]['ChannelNum']

        Type = Type.lower()
        assert Type in TypeLength.keys() ,'SDO desired for ilegal type, found['+repr(Type)+'] , prmitted: ' + repr(TypeLength.keys()) 
        if Type == 'vis string': 
            assert type(data) is str ,'Required visible string for non string data'
            msg =  ((1<<5)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(1,'little')+(len(data)).to_bytes(4,'little') # SDO dnload init 
        else:
            msg =  ((1<<5)+((4-TypeLength[Type][0])<<2)+(1<<1)+1).to_bytes(1,'little')+(Index).to_bytes(2,'little')+(SubIndex).to_bytes(1,'little')+data.to_bytes(4,'little') # SDO dnload init 
        #self.ComPars.handles[h]['CAN_InPool'].clean('cobId',[ NodeId + 0x600 ,  NodeId + 0x580]) # Clear any old junk refering that COB ID 
        #msgRet = self.ComPars.CanComServer.PingCanMessage( ch , NodeId + 0x600 ,  NodeId + 0x580 ,msg , Tout = Timeout)
        try:
            msgRet = self.getbytePingCanMessage(msg)
        except Exception as ex:
            print ( ex )
            sys.exit(1)
       
            
        if msgRet[0] & 0x80 : 
            AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
            assert not (type(AbortMsg) is str), AbortMsg+ ': SetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( self.nodeId , Index , SubIndex) 
            return AbortCode,1 # Return error code + abort 
        if (((msgRet[0] & 0xe0 ) >> 5 ) != 3) or ( msgRet[1:4] != msg[1:4] ) : #Bad CCS, multiplexor does not fit 
           # error ('Bad response to SDO download init') 
           print ('Bad response to SDO download init') 
        #Segmented
        t = 1 ; 
        while len(data) :
            t = 1-t 
            if len(data) > 7 : 
                nNext = 7 
                Complete = 0 
                meser = data[:7]
                data = data[7:]
            else: 
                nNext = len(data)  
                meser  = data + chr(0) * (7-nNext) 
                Complete = 1 
                data = [] 

            msg =  ((t<<4)+((7-nNext)<<1)+Complete).to_bytes(1,'little')+ meser.encode('ascii')

            try:
                msgRet = self.getbytePingCanMessage(msg)
            except Exception as ex:
                print ( ex )
                sys.exit(1)

            if msgRet[0] & 0x80 : 
                AbortCode =  struct.unpack_from('L',msgRet,4)[0]  # Return error code + abort 
                assert not ( type(AbortMsg) is str), AbortMsg+ ': SetSdo Abort code [' + self.AnalyzeSdoAbort(AbortCode) + '] for object Node ID:{0} index {1} subindex {2} '.format( self.nodeId , Index , SubIndex) 
                return AbortCode,1 # Return error code + abort 

        return 0 




    
    def SetPdoMapping( self , PdoNum , FlagRxTxIn , TransType , IndexArr , SubIndexArr , LenArr , PdoCobId =None ):
# function SetPdoMapping( h , NodeId , PdoNum , FlagRxTx , TransType , IndexArr , SubIndexArr , LenArr )
#
# Purpose: Map the specified PDO 
#
# Arguments: 
# h: Handle to opened communication port 
# NodeId: Node ID
# PdoNum: Number of PDO [1,4]
# FlagRxTx: If PDO Rx then 'Rx', if PDO Tx then 'Tx' 
# TransType: Transmission type. May be in the range  [0...255]
# IndexArr: Array of indices of objects to be mapped
# SubIndexArr: Array of sub-indices of objects to be mapped
# LenArr: Array of lengths of objects to be mapped [bites]
# PdoCobId: Not obligatory, if exists, set PDO cob-id parameter
        FlagRxTx = FlagRxTxIn.tolower()
        assert FlagRxTx in FlagRxTx.keys() ,'Ilegal Tx Rx type : found ['+repr(FlagRxTxIn) +']' 
        assert PdoNum in range(4) ,'Ilegal PdoNum'
        pdoPar = MapOpt[FlagRxTx][0]
        pdoMap = MapOpt[FlagRxTx][1]
        cobId = PdoNum*256 + MapOpt[FlagRxTx][2]
#For changing the PDO mapping the previous PDO must be deleted, the sub-index 0 must be set to 0. 	
        self.SetSdo(  pdoMap, 0 , 0 , 'unsigned8' , AbortMsg = 'Cannot delete previous mapping') ;

        if PdoCobId != None : 
            Value,AbortFlag= self.GetSdo(  pdoPar, 1 , 'unsigned32' ) ;
            if AbortFlag: 
                error( 'Cannot program PDO parameters' )
                pdoCobId = PdoCobId | (3<<30) # No RTR allowed
                self.SetSdo( pdoPar , 1 , pdoCobId , 'unsigned32' ,'Cannot set transmission type') 

# Send SDO download to set transmission type.
# Transmission type resides at the sub-index 2h of the PDO Communication Parameter record.				
        self.SetSdo( pdoPar , 2 , TransType , 'unsigned8' ,'Cannot set transmission type') ;

# Mapping loop for all PDO objects to be mapped
        for subIndex in range(len(IndexArr)):
        # The sub-indices from 1 to n contain the information about the mapped objects.
        # Every entry  describes the PDO by its index, sub-index and length
        # according to the Fig.66 CiA DS301 : 
        # 16 most significant bits is object index
        # 8 next bits is sub-index
        # 8 least significant bits is length of object	
            data = IndexArr(subIndex)*65536 + SubIndexArr(subIndex)*256 + LenArr(subIndex) ;
            AbortFlag = self.SetSdo(  pdoMap , subIndex , data , 'unsigned32' ) ;
            if AbortFlag:
                err = self.AnalyzeSdoAbort( AbortFlag ) ;
                error( 'Cannot set mapping: '+err) 

# Send SDO download to set number of entries of the PDO mapped objects 
# Subindex 0 is number of mapped objects in PDO
# For changing the PDO mapping the previous PDO must be deleted, the sub-index 0 must be set to 0. 	
        AbortFlag = self.SetSdo(  pdoMap, 0 , length(IndexArr) , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error( 'Cannot delete previous mapping: {0}'+err) 


        AbortFlag = self.GetSdo(  pdoMap, 0 , 'unsigned8' ) 
        if AbortFlag:
            err = self.AnalyzeSdoAbort( AbortFlag ) ;
            error('Cannot delete previous mapping: '+err ) ;




            
    def sendStr( self  , str  ): 
    #function str = SetOsIntCmd( h , NodeId , str , Timeout )
    # Purpose: Send string to OS interpreter 
    #
    # Arguments: 
    # h: Handle to opened communication port 
    # NodeId: Node ID
    # str: String to transmit
    # timeout: Timeout [sec]
    #
    # Returns: 
    # str: Received string
    # Set object 0x1024 (OS mode) to execute immediate      
        self.SetSdo(  4131 , 1 , str , 'vis string' ,  'OS interpreter send cmd'); # 4131 = 0x1023

    #Wait till target is ready 
    #Result = 0 for completed, no reply 
    #1 no errors, reply 
    #2 error , no reply 
    #3 error , reply there 
        Value = 255 ;
        while Value == 255 : 
           Value,AbortFlag = self.GetSdo( 4131 , 2 , 'unsigned8' ,'OS interpreter wait ready ');# 4131 = 0x1023

        assert Value & 1 , 'Os interpreter failed' 

        Value,ErrCode = self.GetSdo( 4131 , 3 , 'vis string' ,'OS interpreter get result ');# 4131 = 0x1023
        return Value.replace(chr(0),'') 
        #return ''.join(([chr(i) for i in Value if i]))


