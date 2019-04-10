#!/usr/bin/env python
# coding: utf-8

# In[9]:


import matplotlib.pyplot as plt
import numpy as np 
import matplotlib 
import pandas as pd
import csv
import os
import glob
import seaborn as sns
import math


# In[1]:


# Plotters and se 



# Plots standard frequency vs voltage measurements
def plot_single_measurement(measurement):
    '''
    send measurements and frequencies as list of those objects.
    '''
    frequencies = measurement[0]
    voltages = measurement[3]
    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    plt.loglog(frequencies, voltages)
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.yticks(fontsize=12)
    plt.ylabel("$V_{rms}$ (V)", fontsize = 18)
    plt.xlabel("Frequency (Hz)", fontsize = 18)
    
    plt.xlim(frequencies[0], frequencies[len(frequencies)-1])

# Plots standard frequency vs voltage measurements
def plot_frequency_response(measurement_list, legend):
    '''
    send measurements and frequencies as list of those objects.
    '''
    frequencies = []
    voltages = []
    for i in range(0, len(measurement_list)) :
        frequencies.append(measurement_list[i][0])
        voltages.append(measurement_list[i][3])

    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    # Plot all required data
    for i in range(0, (len(frequencies))) :
        plt.loglog(frequencies[i], voltages[i], label = legend[i])
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.yticks(fontsize=12)
    plt.ylabel("$V_{rms}$ (V)", fontsize = 18)
    plt.xlabel("Frequency (Hz)", fontsize = 18)
    
    for i in range(0, 10, 1):
        cl = colours[i]
        plt.axvspan(frequency_bands_start[i], frequency_bands_end[i], color=cl, alpha=0.1)
        
    plt.xlim(frequencies[0][0], frequencies[0][len(frequencies[0])-1])

    plt.legend(loc='upper left')
    

# For a given calibration and measurement, returns se. Must be same frequencies!
def se(calibration, measurement) :
    calibration_v = get_single_volt(calibration)
    measurement_v = get_single_volt(measurement)
    
    # Get rid of troublesome first data point
    #calibration_v = calibration_v[1:]
    #measurement_v = measurement_v[1:]
    
    se = []
    for i in range(0, len(measurement_v)):
        
        # Only a quick fix - change this somehow!
        if calibration_v[i] == 0 : 
            calibration_v[i] = calibration_v[i+1]
        
        ratio = calibration_v[i]/measurement_v[i]
        

        shield = 20 * math.log(ratio, 10)
        se.append(shield)
    return se

# Plot x as length look for room length 

def plot_comparative_se(calibration, measurements, legend) :
    
    shielding = []
    frequency = []    
    
    for measurement in measurements :
        shielding.append(se(calibration, measurement))
        frequency.append(get_single_freq(calibration))
    
    
    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    # Plot  data
    for i in range(0, len(frequency)) :
        plt.semilogx(frequency[i], shielding[i], label = legend[i])
        
        
    for i in range(0, 10, 1):
        cl = colours[i]
        plt.axvspan(frequency_bands_start[i], frequency_bands_end[i], color=cl, alpha=0.2)
        
    plt.xlim(frequency[0][0], frequency[0][len(frequency[0])-1])
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.yticks(fontsize=12)
    plt.ylabel("Shielding effectiveness (dB)", fontsize = 18)
    plt.xlabel("Frequency (Hz)", fontsize = 18)
    plt.legend(loc = 'upper left')


def print_se(calibration, measurement, frequency_range) :
    shielding = se(calibration, measurement)
    frequency = get_single_freq(calibration)
    
    frequency_min = frequency_range[0]
    frequency_max = frequency_range[1]
    

    first_index = [n for n,i in enumerate(frequency) if i>frequency_min][0]
    
    try :
        last_index = [n for n, i in enumerate(frequency) if i > frequency_max][0]
    except IndexError as error : 
        print("Max frequency used instead of max bound")
        last_index = len(frequency)

    for i in range(first_index, last_index) : 
        print("%d Hz:  %f" % (frequency[i], shielding[i]))
    
def plot_se(calibration, measurement) :
    shielding = se(calibration, measurement)
    frequency = get_single_freq(calibration)
    
    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    # Plot  data
    plt.semilogx(frequency, shielding)
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.yticks(fontsize=12)
    plt.ylabel("Shielding effectiveness (dB)", fontsize = 18)
    plt.xlabel("Frequency (Hz)", fontsize = 18)
    
    for i in range(0, 10, 1):
        cl = colours[i]
        plt.axvspan(frequency_bands_start[i], frequency_bands_end[i], color=cl, alpha=0.2)
        
    plt.xlim(frequency[0], frequency[len(frequency)-1])

    
def get_volts(list_of_measurements):
    '''Takes list of panda dfs'''
    volts = []
    for i in range(0, len(list_of_measurements)) :
        volts.append(list_of_measurements[i][list_of_measurements[i].columns[3]].tolist())
    
    return volts
        
def get_freq(list_of_measurements):
    '''Takes list of panda dfs'''
    freq = []
    for i in range(0, len(list_of_measurements)) :
        freq.append(list_of_measurements[i][list_of_measurements[i].columns[0]].tolist())
    return freq

def get_single_volt(measurement) :
    return measurement[measurement.columns[3].tolist()]

def get_single_freq(measurement) :
    return measurement[measurement.columns[0].tolist()]

def names_to_csv(names):
    'takes names of files and turns them into panda dfs'
    csv_files = []
    for name in names :
        name = name + ".csv"
        csv_files.append(pd.read_csv(name, header=None))
    return csv_files

def plot_se_metres(calibration, measurements, legend) :
    
    shielding = []
    frequencies = []    
    wavelengths = []
    c = 299792458
    
    for measurement in measurements :
        shielding.append(se(calibration, measurement))
        frequencies.append(get_single_freq(calibration))
    
    for frequency in frequencies :
        wl = []
        for i in range(0, len(frequency)) :
            wl.append(c / frequency[i])
        wavelengths.append(wl)
    
    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    # Plot  data
    for i in range(0, len(wavelengths)) :
        plt.semilogx(wavelengths[i], shielding[i], label = legend[i])
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.yticks(fontsize=12)
    plt.ylabel("Shielding effectiveness (dB)", fontsize = 18)
    plt.xlabel("Wavelength (m)", fontsize = 18)
    plt.legend(loc = 'upper left')

def plot_se_metres_under_10(calibration, measurements, legend) :
    
    shielding = []
    frequencies = []    
    wavelengths = []
    c = 299792458
    
    for measurement in measurements :
        shielding.append(se(calibration, measurement))
        frequencies.append(get_single_freq(calibration))
    
    for frequency in frequencies :
        wl = []
        for i in range(0, len(frequency)) :
            wl.append(c / frequency[i])
        wavelengths.append(wl)
    
    min_x = c/frequencies[0][len(frequencies[0])-1]
    
    # Set up figure
    plt.figure(figsize = (10, 6))
    ax = plt.subplot(111)  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False) 
    
    # Plot  data
    for i in range(0, len(wavelengths)) :
        plt.plot(wavelengths[i], shielding[i], label = legend[i])
    
    # A bit more tidying
    plt.xticks(fontsize=12)  
    plt.xlim(min_x, 10)
    plt.yticks(fontsize=12)
    plt.ylabel("Shielding effectiveness (dB)", fontsize = 18)
    plt.xlabel("Wavelength (m)", fontsize = 18)
    plt.legend(loc = 'upper right')

    


# In[23]:


# Frequency ranges for colours

colours = sns.color_palette("Set2", 12)

def colour_picker(frequency) : 
    
    frequency = float(frequency)
    if frequency > 9e3 and frequency < 16e3 : 
        return colours[0]
    elif frequency > 140e3 and frequency < 160e3 : 
        return colours[1]
    elif frequency > 14e6 and frequency < 16e6 : 
        return colours[2]
    elif frequency > 20e6 and frequency < 100e6 : 
        return colours[3]
    elif frequency > 100e6 and frequency < 300e6 : 
        return colours[4]
    elif frequency > 0.3e9 and frequency < 0.6e9 : 
        return colours[5]
    elif frequency > 0.6e9 and frequency < 1e9 : 
        return colours[6]
    elif frequency > 1e9 and frequency < 2e9 : 
        return colours[7]
    elif frequency > 2e9 and frequency < 4e9 : 
        return colours[8]
    elif frequency > 4e9 and frequency < 8e9 : 
        return colours[9]
    elif frequency > 8e9 and frequency < 18e9 : 
        return colours[10]
    else :
        return colours[11]
    
#colour = [colour_picker(item) for item in x]

frequency_bands_start = [9e3, 140e3, 14e6, 20e6, 100e6, 0.3e9, 0.6e9, 1e9, 2e9, 4e9, 8e9]
frequency_bands_end = [16e3, 160e3, 16e6, 100e6, 300e6, 0.6e9, 1e9, 2e9, 4e9, 8e9, 18e9]


# In[ ]:




