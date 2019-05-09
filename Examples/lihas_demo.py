from NeuroPy import NeuroPy

object1 = NeuroPy("COM6") #If baud rate not given, it's set automatically 

def attention_callback(attention_value): 
"called everytime NeuroPy has a new value for attention" 
    print("Value of attention is", attention_value)
    #do some more stuff 
    return None 

#set call back: 
object1.setCallBack("attention",attention_callback) 

#call start method 
object1.start() 

while True: 
    if(object1.meditation > 70): #another way of accessing headset data (1st being callbacks)
        object1.stop() #if meditation level reaches above 70, stop fetching data