from machine import Pin

class Button:
    
    NONE = 0
    PRESS = 1
    RELEASE = 2
    
    def __init__(self,pinNum):
        self.pinNum = pinNum
        self.pin = Pin(pinNum, Pin.IN, Pin.PULL_UP)
        self.state = self.pin.value()
        
        
    def getEvent(self):
        newState = self.pin.value()
        if(newState != self.state):
            self.state = newState
            if(newState == 0):
                return self.PRESS
            else:
                return self.RELEASE
            
        return self.NONE