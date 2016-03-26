import Interface 
import CanOpenImpl as canopen
import sys
class CanOpenCom(Interface.Interface):
    """This class implements interface of astract Interface class 
       for Can communication"""
    def __init__(self):
        self.canopen = canopen.CanOpenKvaserImpl()
        self.Termin = [ord(';'),10,13,0] 
        self.ErrTermin = ['?']
        pass
  
     
    def open(self,ch,baud=500000,flags=0):
        try:
          self.canopen.open(ch ,baud,flags)
        except Exception as ex:
            print ( ex )   
            sys.exit(1)


    def close(self):
        try:
          self.canopen.close()
        except Exception (ex):
            print ( ex )
    

    def setArray(self,ToSend ,Ind , Numval ):
        ''''''
        assert (type(ToSend) is str) and (type(Numval) is list) and (type(Ind) is list) and (len(Ind) == len(Numval)) , 'ToSend must be a string and the Ind and values be a lists of same length'
        Rslt = [0] * len(Numval)
        for cnt in range(len(Numval)) :
            Rslt[cnt] = self.SetValue(   ToSend + '[{0}]'.format(Ind[cnt]) , Numval[cnt] )


    def getArray(self, ToSend , Ind):
        ''''''
        assert (type(ToSend) is str) and (type(Ind) is list) , 'ToSend must be a string and the Ind and values be a lists of same length'
        Rslt = [0] * len(Ind)
        for cnt in range(len(Ind)) :
            Rslt[cnt] = self.GetValue(  h , ToSend + '[{0}]'.format(Ind[cnt])  )
        return Rslt


    def setValue(self,ToSend,values):
        '''set value and send.
        toSend: list or str to send
        values: list or str to send
        if toSend and values are list then their length must be equal '''
        if type(ToSend) is list : 
            assert (type(values) is list) and (len(ToSend)==len(values)), 'ToSend and Numval must be lists of the same length'
            Rslt = [0] * len(values)
            for cnt in range(len(values)) :
                Rslt[cnt] = self.SetValue(  ToSend[cnt] , values[cnt] )
        return self.PingString( ToSend + '={0}'.format(values) )


    def getValue(self,cmd):
        '''send command and return value
        cmd : string command to send 
        return value of type int or float ( see toNum method)'''
        rslt = self.PingString(cmd)
        rstl = self.toNum(rstl)
        return rstl

    
    def ToNum(self, R , ErrorTerminator = None):
        '''get result and convert it to number
        R: list or string 
        return number of type float or int'''
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
 

    def PingString( self , ToSend  ):
        # A list of strings to send - send them one by one 
        if type(ToSend) is list : 
            ll = len(ToSend) 
            Rslt = [0] * ll 
            #Err  = [0] * ll

            for cnt in range( len(ToSend)): 
                 Rslt[cnt] = self.PingString( ToSend[cnt] )  
            return Rslt
        # A simple string 
        assert type(ToSend) is str , 'Object to send [' + repr(ToSend) +'] should be a string'
        #############################################
        while ord(ToSend[-1]) in self.Termin:
            ToSend = ToSend[:-1]
        ###############################################             
        return self.canopen.sendStr( ToSend + ';') 

    def sendCommand(self,command):
        self.PingString(command)


    def getNodeId(self):
        return self.canopen.getNodeId()

    def setNodeId(self,id):
        if isinstance( id,int) and 1<=id<=127:
            self.canopen.setNodeId(id)
        else: 
            raise ValueError('Probably {0} is out of range or type is {1} but [int] was expected'.format( repr(id),type(id))) 

if __name__ == '__main__':
    c =  CanOpenCom()
    c.open(0)
    c2 = CanOpenCom()
    c2.open(1)

    c.setNodeId(1)
    c2.setNodeId(2)
    c.sendCommand('vr')
    print('ok')