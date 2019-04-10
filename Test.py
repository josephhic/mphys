import visa
import numpy as np
import time
import sys
import pandas as pd
import csv
import matplotlib.pyplot as plt
from tqdm import tqdm # Progress meter
import math

print("Connecting to hardware...")

# Open visa resource manager
rm = visa.ResourceManager("C:/Windows/System32/visa32.dll")
rm.list_resources()

print("VRM connected...")

# Lock-in amplifier
lock_in_dict = {"Frequency": 0, "X": 1, "Y": 2, "Volts RMS": 3, "Volts dB": 4, "Phase": 5}
GPIB_SR844 = 2
address_SR844 = 'GPIB0::' + str(GPIB_SR844) + '::INSTR'
SR844 = rm.open_resource(address_SR844)

print("Lock-in online")

# Mid-frequency signal generator (30k - 30M)
#GPIB_SG = 10
#address_SG = 'GPIB0::' + str(GPIB_SG) + '::INSTR'
#SG = rm.open_resource(address_SG)

# High frequency signal generator (MAX)
GPIB_HFSG = 19
address_HFSG = 'GPIB0::' + str(GPIB_HFSG) + '::INSTR'
HFSG = rm.open_resource(address_HFSG)

print("Signal generator online")


#try : 
#    SG.query("*IDN?")
#    print("Low frequency signal generator connected")
#    GEN = SG
#except VI_ERROR_TMO as error :
#    GEN = HFSG
#    print("High frequency signal generator connected")

# Frequency sweeper
def sweep(frequencies, name):
    
    measurements = []

    for frequency in tqdm(frequencies) :
        
        # Set up individual measurement object. Will contain frequency and all parameters measured by lockin
        measurement = np.empty(6)

        # Set the signal generator's frequency
        GEN.write("SOUR:FREQ %s" % str(frequency))
        
        # Check lock-in is on the right frequency
        lock_in_freq = SR844.query("FRAQ?")
        lock_int = float(SR844.query("FRAQ?"))
        fract_delta = abs(lock_int - frequency)/frequency
        wait_count = 0
        
        while fract_delta > 0.001: 
            time.sleep(0.1)
            lock_in_freq = float(SR844.query("FRAQ?"))
            fract_delta = abs(lock_in_freq - frequency)/frequency
            wait_count += 1
        
        #print("Accuracy of %f achieved in %i tries at %f" % (fract_delta, wait_count, lock_in_freq))
        
        # Add lockin frequency to measurement object
        measurement[0] = lock_in_freq

        # Wait for the signal to settle and measure parameters
        time.sleep(0.5)
        for i in range(1, 6) :
            measurement[i] = SR844.query("OUTP? %d" % i)
            
        # Lists are easier!
        full_measurement = measurement.tolist()
        
        #Add single frequency measurement and data to full measurement array
        measurements.append(full_measurement)
        
    # Confirm the measurements have been completed
    print("Measurements finished")    
    
    filename = "20190326/%s.csv" % name 
    
    # Print measurements to file. Each measurement will be one row in CSV format
    with open(filename, "wb") as file : 
        writer = csv.writer(file)
        writer.writerows(measurements)
        
    return measurements

def plot_se_835(frequencies, voltage) :
    calibrated_measurement = pd.read_csv("calibration-835.csv", header = None)
    shielding_eff = []

    for i in range(len(calibrated_measurement[3])) :
        ratio = calibrated_measurement[3][i] / voltageRMS[i]
        shielding = 20 * math.log(ratio, 10)
        shielding_eff.append(shielding)
    
    plt.semilogx(frequencies, shielding_eff)
    
    
##############################################################################
     # Program start
  
# Select either mid-range signal generator (l: h) or high-range signal generator (h: HFSG)
#print("Which signal generator do you want to use? high/low frequency (h/l)")
#sig_gen = raw_input()
#if sig_gen == "l" :
#    GEN = SG
#    print("Low frequency signal generator selected")
#else :
#    GEN = HFSG
#    print("High frequency signal generator selected (default)")
 
# Set signal generator to be the high-frequency one (used in other methods)
GEN = HFSG

sensitivities = {"100n":0, "300n":1, "1u":2, "3u":3, "10u":4, "30u":5, "100u":6, "300u":7,
 "1m":8, "3m":9, "10m":10, "30m":11, "100m":12, "300m":13, "1":14}
    
sensitivity_list = ["100n", "300n", "1u", "3u", "10u", "30u", "100u", "300u", "1m", "3m", "10m", "30m", "100m", "300m", "1"]

# Set up frequency array 
start = 4.4

#if sig_gen == "l" :
#    end = 7.3
#else : 
#    end = 8.3

end = 8.3

increment = 0.01

#increment = 0.025
frequencies = [10.0**e for e in np.arange(start, (end + increment), increment)] 


# First frequency never seems to work, so just get rid of it
frequencies = frequencies[1:]

# Take the measurements
print("Please enter a descriptive filename:")
filename = raw_input()

print("Do you want to plot the shielding effectiveness (only for standard 835mm measurements)? [y/n]")
plot_se = raw_input()


# To change sensitivity of lock-in 
change_sens = False
sensitivity = SR844.query("SENS?")
print("Sensitivity is currently set to %s. Change? [y/n]" % sensitivity_list[int(sensitivity)])
change = raw_input()
if change == "y" :
    print("What to? (e.g. 300u, 3m. [1, 3, 10, 30, 100, 300; n, u, m])")
    new = raw_input()
    if new in sensitivities : 
        SR844.write("SENS %d" % sensitivities.get(new))
        print("Sensitivity changed to %s" % new)
        time.sleep(0.1)
else :
    print("Sensitivity has not been changed")



plot = False
if plot_se == "y" :
    plot = True

measurements = sweep(frequencies, filename)     

# Plotting for diagnostics
lock_in_frequencies = []
voltageDB = []
voltageRMS = []

for i in range(0, len(measurements)):
    lock_in_frequencies.append(measurements[i][0])
    voltageDB.append(measurements[i][4])
    voltageRMS.append(measurements[i][3])

plt.plot(lock_in_frequencies, voltageRMS)
plt.xscale("log")
plt.yscale("log")
plt.show()

if plot == True :
    plot_se_835(frequencies, voltageRMS)
    








