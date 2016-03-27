class ComInterface:
    
    ''' This is a simple interface communication
    derived from DftInterp.py written by Y.Theodor in april 2015
   The purpose of this class is to create common interface for all
   types of communications 
    '''
    def setArray(self,toSend):
        raise NotImplementedError

    def getArray(self):
        raise NotImplementedError

    def getValue(self,cmd):
        raise NotImplementedError

    def sendCommand(self,command):
        '''send command as string to target
        command : string to send'''
        raise NotImplementedError

    def setValue(self,toSend,values):
        '''set value and send.
        toSend: list or str to send
        values: list or str to send
       if toSend and values are list then their length must be equal '''
        raise NotImplementedError

   

