Termin = [ord(';'),10,13,0] 

def decodeMessage(mes):
     while  ord(mes[-1]) in Termin:
                    mes =  mes[:-1] 
     return mes
def encodeMessage(mes):
    return mes+';'