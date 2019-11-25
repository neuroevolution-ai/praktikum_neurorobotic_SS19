# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 09:54:23 2019

@author: dzimmer
"""

import csv
import numpy as np
import matplotlib.pyplot as plt

with open('output1.csv', 'r') as f1:
    reader1 = csv.reader(f1)
    logging_information = list(reader1)
    
with open('output2.csv', 'r') as f2:
    reader2 = csv.reader(f2)
    output = list(reader2)
    
# Convert to numpy array
out_arr1 = np.asarray(logging_information, dtype=np.float)
out_arr2 = np.asarray(output, dtype=np.float)

# Get vectors
age, voltage_left1, voltage_right1, red_left_rate1, red_right_rate1, non_red_rate1 = np.hsplit(out_arr1, 6)
voltage_left2, voltage_right2 = np.hsplit(out_arr2, 2)

voltage_left_stack = np.hstack((voltage_left1, voltage_left2))
voltage_left_diff = np.absolute(np.diff(voltage_left_stack, axis=1))
voltage_left_error = np.sum(voltage_left_diff)

voltage_right_stack = np.hstack((voltage_right1, voltage_right2))
voltage_right_diff = np.absolute(np.diff(voltage_right_stack, axis=1))
voltage_right_error = np.sum(voltage_right_diff)

plt.plot(age, voltage_left1)
plt.plot(age, voltage_left2)

#plt.plot(age, voltage_right1)
#plt.plot(age, voltage_right2)

plt.grid()
plt.show()

