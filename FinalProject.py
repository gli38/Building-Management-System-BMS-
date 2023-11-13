import RPi.GPIO as GPIO
import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT11 #this line defines the sensor object we will use
DHT_PIN = 16

ledPin = 12 # define ledPin
sensorPin = 11 #define sensorPin

SecurityButton = 29 #define SecurityButton

ACButton = 31 #define ACButton 
HeaterButton = 35 #define HeaterButton
ACled = 40 #define ACled
Heaterled = 38 #define Heaterled

class DHT(object):
    DHTLIB_OK = 0
    DHTLIB_ERROR_CHECKSUM = -1
    DHTLIB_ERROR_TIMEOUT = -2
    DHTLIB_INVALID_VALUE = -999
    
    DHTLIB_DHT11_WAKEUP = 0.020#0.018       #18ms
    DHTLIB_TIMEOUT = 0.0001         #100us
    
    humidity = 0
    temperature = 0
    
    def __init__(self,pin):
        self.pin = pin
        self.bits = [0,0,0,0,0]
        GPIO.setmode(GPIO.BOARD)
    #Read DHT sensor, store the original data in bits[] 
    def readSensor(self,pin,wakeupDelay):
        mask = 0x80
        idx = 0
        self.bits = [0,0,0,0,0]
        # Clear sda
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(0.5)
        # start signal
        GPIO.output(pin,GPIO.LOW)
        time.sleep(wakeupDelay)
        GPIO.output(pin,GPIO.HIGH)
        # time.sleep(0.000001)
        GPIO.setup(pin,GPIO.IN)
        
        loopCnt = self.DHTLIB_TIMEOUT
        # Waiting echo
        t = time.time()
        while True:
            if (GPIO.input(pin) == GPIO.LOW):
                break
            if((time.time() - t) > loopCnt):
                return self.DHTLIB_ERROR_TIMEOUT
        # Waiting echo low level end
        t = time.time()
        while(GPIO.input(pin) == GPIO.LOW):
            if((time.time() - t) > loopCnt):
                #print ("Echo LOW")
                return self.DHTLIB_ERROR_TIMEOUT
        # Waiting echo high level end
        t = time.time()
        while(GPIO.input(pin) == GPIO.HIGH):
            if((time.time() - t) > loopCnt):
                #print ("Echo HIGH")
                return self.DHTLIB_ERROR_TIMEOUT
        for i in range(0,40,1):
            t = time.time()
            while(GPIO.input(pin) == GPIO.LOW):
                if((time.time() - t) > loopCnt):
                    #print ("Data Low %d"%(i))
                    return self.DHTLIB_ERROR_TIMEOUT
            t = time.time()
            while(GPIO.input(pin) == GPIO.HIGH):
                if((time.time() - t) > loopCnt):
                    #print ("Data HIGH %d"%(i))
                    return self.DHTLIB_ERROR_TIMEOUT        
            if((time.time() - t) > 0.00005):    
                self.bits[idx] |= mask
            #print("t : %f"%(time.time()-t))
            mask >>= 1
            if(mask == 0):
                mask = 0x80
                idx += 1    
        #print (self.bits)
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,GPIO.HIGH)
        return self.DHTLIB_OK
    #Read DHT sensor, analyze the data of temperature and humidity
    def readDHT11Once(self):
        rv = self.readSensor(self.pin,self.DHTLIB_DHT11_WAKEUP)
        if (rv is not self.DHTLIB_OK):
            self.humidity = self.DHTLIB_INVALID_VALUE
            self.temperature = self.DHTLIB_INVALID_VALUE
            return rv
        self.humidity = self.bits[0]
        self.temperature = self.bits[2] + self.bits[3]*0.1
        sumChk = ((self.bits[0] + self.bits[1] + self.bits[2] + self.bits[3]) & 0xFF)
        if(self.bits[4] is not sumChk):
            return self.DHTLIB_ERROR_CHECKSUM
        return self.DHTLIB_OK
    def readDHT11(self):
        result = self.DHTLIB_INVALID_VALUE
        for i in range(0,15):
            result = self.readDHT11Once()
            if result == self.DHTLIB_OK:
                return self.DHTLIB_OK
            time.sleep(0.1)
        return result
        
# def getHumidiy():
#     global humidity
#     while True:
#         date = datetime.datetime.now().strftime('%Y-%m%-d')
#         url = ('http://et.water.ca.gov/ap/data?appkey=' + appKey + '&targets=' + station + '&startDate-' + date + '&endDate-' + date + '&dataItems-' + 'hly-rel-hum,&unitOfMeasure-M')
#         try:
#             content = request.urlopen(url).read().decode('utf-8')
#             data = json.loads(content)
#         except:
#             data = None
#             
#         if(data is None):
#             return None
#         else
#         humidtyData = data['Data']['Providers'][0]['Records']
#         humidity = int(humidityData[(datetime.datetime.now().hour) - 3]['HlyRelHum']['Value'])
#         

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) #use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT) #set ledPin to OUTPUT mode
    GPIO.setup(sensorPin, GPIO.IN) #set sensorPin to INPUT mode
    GPIO.setup(SecurityButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ACButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HeaterButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ACled, GPIO.OUT)
    GPIO.setup(Heaterled, GPIO.OUT)
    
def HVAC():
    desiredTemp = dht.temperature
    weather_index = dht.temperature + 0.05 * dht.humidity
    EnergyBill = 0
    TotalEnergyConsume = 0
    
    
    while True:
        ACButtonState = GPIO.input(ACButton)
        if ACButtonState == False:
            desiredTemp = desiredTemp + 1
        HeaterButtonState = GPIO.input(HeaterButton)
        if HeaterButtonState == False:
            desiredTemp = desiredTemp - 1
            
        TurnOn = weather_index - desiredTemp
        if TurnOn > 3:
            GPIO.output(ACled, GPIO.HIGH)
            EnergyBill = 18000 * 0.50
            TotalEnergyConsume = 18000
            print('energy: ' + str(TotalEnergyConsume) + 'KWh ' +  'cost: $', + str(EnergyBill))
        elif TurnOn < 0:
            GPIO.output(Heaterled, GPIO.HIGH)
            EnergyBill = 36000 * 0.50
            TotalEnergyConsume = 36000
            print('energy: ' + str(TotalEnergyConsume) + 'KWh, ' +  'cost: $', + str(EnergyBill))
        else:
            GPIO.output(ACled, GPIO.LOW)
            GPIO.output(Heaterled, GPIO.LOW)
def loop():
    counter = 0
    Door = 0
    
    dht = DHT(16)
    sumCnt = 0
    okCnt = 0
    
    while True:
            
        if GPIO.input(sensorPin)==GPIO.HIGH:
            GPIO.output(ledPin,GPIO.HIGH) #turn on led
            print ('led turned on >>>')
            time.sleep(0.1)
        else:
            #counter = counter + 1
            #if counter == 10:
                #break
            GPIO.output(ledPin,GPIO.LOW) #turn off led
            print('led turned off <<<')
            time.sleep(0.1)
            
        sumCnt += 1
        chk = dht.readDHT11()   
        if (chk is 0):
            okCnt += 1      
        okRate = 100.0*okCnt/sumCnt;
        SecurityButtonState = GPIO.input(SecurityButton)
        if SecurityButtonState == False and Door == 0:
            Door = 1
            print ('Door/Window open!')
            time.sleep(10)
        elif SecurityButtonState == False and Door == 1:
            Door = 0
            print ('Door/Window closed!')
            HVAC()
        print("sumCnt : %d, \t okRate : %.2f%% "%(sumCnt,okRate))
        print("chk : %d, \t Humidity : %.2f, \t Temperature : %.2f "%(chk,dht.humidity,dht.temperature))
        time.sleep(3)
        
    
            
def destroy():
    GPIO.cleanup() #Release GPIO resource

_name_ = '_main_'

if _name_ == '_main_':    # Program entrance
    print('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()
    