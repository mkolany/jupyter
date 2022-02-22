# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import csv
import RTD

## pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pin_1 = 4
pin_2 = 19

GPIO.setup(pin_1, GPIO.OUT)
GPIO.setup(pin_2, GPIO.OUT)
pwm_1 = GPIO.PWM(pin_1, 10)
pwm_2 = GPIO.PWM(pin_2, 10)
pwm_1.start(0)
pwm_2.start(0)

sensor_1 = RTD.max31865(csPin = 16)
sensor_2 = RTD.max31865(csPin = 12)

## variables
Duty_min=0
Duty_max=50

step = 10
delta_temp = 5
set_temp_1 = 30
set_temp_2 = set_temp_1 - delta_temp
swinia = set_temp_2
flag = 1

temp_1_lista=[]
temp_2_lista=[]

old_error_1 = 0
old_error_2 = 0
old_time = 0
temp_1 = 0
temp_2 = 0
Mvolt = ''
Mresi = ''
Mtime = ''

p_term_1 = 0
p_term_2 = 0
i_term_1 = 0
i_term_2 = 0
d_term_1 = 0
d_term_2 = 0

#### pid
kp = .7
ki = .002
kd = .01

#### eps
EPSILON = 0.2

############ FUNKCJE ################################

#### plikozapisywcz
# f = open('/home/pi/Documents/python/TE_measurements/outputs/'+str(int(time.time()))+'.csv', 'w', newline='')
import sys

timestamp = str(int(time.time()))

if len(sys.argv)==1:
    nazwa_pliku = timestamp
elif len(sys.argv)==2:
    nazwa_pliku = sys.argv[1]
else:
    nazwa_pliku = sys.argv[1]+'_err_'+timestamp

f = open('/home/pi/Documents/python/TE_measurements/outputs/'+ nazwa_pliku +'.csv', 'w', newline='')
writer = csv.writer(f,  delimiter=',')

def zapisz(*args):
    writer.writerow([*args])

def constrain(value, min, max): # (5)
    if value < min :
        return 0
    if value > max :
        return max
    else:
        return value

def update_pid_hot():   # (6)
    global old_time_1, old_error_1, temp_1, set_temp_1, de_hot
    global p_term_1, i_term_1, d_term_1
    now = time.time()
    dt_hot = now - old_time_1 # (7)

    error_hot = set_temp_1 - temp_1 # (8)
    de_hot = error_hot - old_error_1       # (9)

    p_term_1 = kp * error_hot                     # (10)
    i_term_1 += ki * error_hot                    # (11)
    i_term_1 = constrain(i_term_1, 0, 100)      # (12)
    d_term_1 = (de_hot / dt_hot) * kd                 # (13)

    old_error_1 = error_hot
    # print((temp_1, p_term_1, i_term_1, d_term_1))
    output = p_term_1 + i_term_1 + d_term_1      # (14)
    output = constrain(output, Duty_min, Duty_max)
    return output

def update_pid_cold():   # (6)
    global old_time_2, old_error_2, temp_2, set_temp_2, de_cold
    global p_term_2, i_term_2, d_term_2
    now = time.time()
    dt_cold = now - old_time_2 # (7)

    error_cold = set_temp_2 - temp_2 # (8)
    de_cold = error_cold - old_error_2       # (9)

    p_term_2 = kp * error_cold                     # (10)
    i_term_2 += ki * error_cold                    # (11)
    i_term_2 = constrain(i_term_2, 0, 100)      # (12)
    d_term_2 = (de_cold / dt_cold) * kd                 # (13)

    old_error_2 = error_cold
    # print((temp_1, p_term_1, i_term_1, d_term_1))
    output = p_term_2 + i_term_2 + d_term_2      # (14)
    output = constrain(output, Duty_min, Duty_max)
    return output

### smu2450
def beep(notes):
    noteToHz = {
    'A': 440,
    'B': 493.88,
    'C': 523.25,
    'D': 587.33,
    'E': 659.25,
    'F': 698.46,
    'G': 783.99
    }
    for note in notes:
        smu2450.write('SYSTEM:BEEP %s,0.1' %noteToHz.get(str(note).upper(), '20'))

def voltMeas():
    dmm6500.write('*RST')
    dmm6500.write('SENS:FUNC "VOLT:DC", (@1)')
    dmm6500.write('SENS:VOLT:RANG 0.1, (@1)')
    dmm6500.write('SENS:VOLT:INP AUTO, (@1)')
    dmm6500.write('SENS:VOLT:NPLC 10, (@1)')
    dmm6500.write('SENS:VOLT:AZER ON, (@1)')
    dmm6500.write('ROUT:CLOS (@1)')

    V = dmm6500.query('READ?')
    return float(V)*(-1)

def resMeas():
    dmm6500.write('*RST')
    dmm6500.write('SENS:FUNC "VOLT:DC", (@1)')
    dmm6500.write('SENS:VOLT:RANG 0.1, (@1)')
    dmm6500.write('SENS:VOLT:INP AUTO, (@1)')
    dmm6500.write('SENS:VOLT:NPLC 10, (@1)')
    dmm6500.write('SENS:VOLT:AZER ON, (@1)')
    dmm6500.write('ROUT:CLOS (@1)')

    smu2450.write('SOURCE:CURR 0.01')
    smu2450.write('OUTP ON')
    V1=float(dmm6500.query('READ?'))
    smu2450.write('OUTP OFF')

    smu2450.write('SOURCE:CURR -0.01')
    smu2450.write('OUTP ON')
    V2=float(dmm6500.query('READ?'))
    smu2450.write('OUTP OFF')

    R=(V1-V2)/.02
    return float(R)

########## START ######################################

# podłączanie smu2450
print("Loading visa package (it takes a while)")
import visa

print("Connecting to a device\n")
rm = visa.ResourceManager('@py')
smu2450 = rm.open_resource('USB0::1510::9296::04384536::0::INSTR')
smu2450.timeout = None
dmm6500 = rm.open_resource('USB0::1510::25856::04507180::0::INSTR')
dmm6500.timeout = None

beep('C')

print(smu2450.query('*IDN?'))
print(dmm6500.query('*IDN?'))
print(dmm6500.query('SYST:CARD1:IDN?'))

print("\nSetting it up (this is quite fast)")

smu2450.write('*RST')
smu2450.write('OUTP:SMOD HIMP')
smu2450.write('SOUR:FUNC CURR')
smu2450.write('SOUR:CURR:VLIM .5')
smu2450.write('SOUR:DEL .1')

beep('CEC')

print("Duty range: [%d, %d]"%(Duty_min, Duty_max))

print("PID constants: kp=%.1f, ki=%.3f, kd=%.3f"%(kp,ki,kd))

print("Set temperature hot: ",set_temp_1)
print("Set temperature cold: ",set_temp_2)

zapisz('Time','Temp1','Temp2','delta','Duty1','SetTemp1','Duty2','SetTemp2','V','R') # testowy zapis i wiersz nagłówkowy

time0 = time.time()
old_time_1 = time.time()
old_time_2 = time.time()
old_time2 = time.time()
counter = 0

try:
    while True:
        if set_temp_2 <= 105:
            # pomiar temperatury (co 1s)
            counter = counter + 1
            now = time.time()
            if now > old_time + 1:
                old_time_1 = now
                old_time_2 = now
                temp_1 = sensor_1.readTemp()
                temp_2 = sensor_2.readTemp()

                if (temp_1>300 or temp_1<0 or temp_2>300 or temp_2<0):
                    raise Exception("Sensor is idle")

                delta = temp_1 - temp_2
                Mtime=time.time() - time0

                duty_1 = update_pid_hot()
                duty_2 = update_pid_cold()
                pwm_1.ChangeDutyCycle(duty_1)
                pwm_2.ChangeDutyCycle(duty_2)

                temp_1_lista.append(temp_1)
                temp_2_lista.append(temp_2)

                print("set_temp_1=%.0f    temp_1=%.2f    temp_2=%.2f    R=%.6s    V=%s \r" %(set_temp_1,temp_1,temp_2,Mresi,Mvolt), end="")

                if counter%2 == 0:
                    Mresi=resMeas()
                else:
                    Mvolt=voltMeas()
                    zapisz(Mtime, temp_1, temp_2, delta, duty_1, set_temp_1, duty_2, set_temp_2, Mvolt, Mresi) # zapisanie do csv

            if (all(abs(temp_1-set_temp_1)<EPSILON for temp_1 in temp_1_lista[-30:]) and all(abs(temp_2-set_temp_2)<EPSILON for temp_2 in temp_2_lista[-30:])):
                if now > old_time2 + 1200:
                    beep('COC')
                    old_time2 = now

                    print('\n')

                    if flag == 1:
                        set_temp_2 = set_temp_1
                        set_temp_1 = swinia
                        flag = 2
                    elif flag == 2:
                        set_temp_1 = set_temp_1 + step
                        set_temp_2 = set_temp_2 + step
                        swinia = set_temp_2
                        flag = 1

        else:
            zapisz(Mtime, temp_1, temp_2, delta, duty_1, set_temp_1, duty_2, set_temp_2, Mvolt, Mresi) # zapisanie do csv
            print("Done")
            break

finally:
    GPIO.cleanup()
    pwm_1.ChangeDutyCycle(0)
    pwm_2.ChangeDutyCycle(0)
