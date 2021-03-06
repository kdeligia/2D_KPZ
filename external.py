#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 11:03:50 2019

@author: delis
"""

import os
import numpy as np

def confining(array, V_0, l):
    V = (V_0/l) * (np.exp(-(array - len(array)/2) ** 2 / (l**2)) + np.exp(-(array + len(array)/2) ** 2 / (l**2)))
    return V

def time(dt, N_steps, i1, i2, secondarystep):
    lengthindex = i2-i1
    length = lengthindex//secondarystep + 1
    t = np.zeros(length)
    for i in range(N_steps+1):
        if i>=i1 and i<=i2 and i%secondarystep==0:
            t[(i-i1)//secondarystep] = i*dt
    return t

def ensemble_average_total(path, t, N, n_batch):
    avg = np.zeros((len(t), int(N/2)), dtype=complex)
    for file in os.listdir(path):
        if '.npy' in file:
            item = np.load(path+os.sep+file)
            avg += item / n_batch
    return avg

def ensemble_average_space(path, obj, N, n_batch):
    avg = np.zeros((obj, N), dtype=complex)
    for file in os.listdir(path):
        if '.npy' in file:
            item = np.load(path+os.sep+file)
            avg += item / n_batch
    return avg

def ensemble_average_time(path, t, n_batch):
    avg = np.zeros(len(t), dtype=complex)
    for file in os.listdir(path):
        if '.npy' in file:
            item = np.load(path+os.sep+file)
            avg += item / n_batch
    return avg

'''
import matplotlib.pyplot as pl
ar = np.zeros((512,512))
cor = np.zeros((512,512), dtype=complex)
for i in range(100):
    xi = noise(ar.shape)
    cor += xi * np.conjugate(xi) / 100

pl.plot(cor[0])
pl.plot(cor[126])
pl.plot(cor [256])
pl.plot(cor[:,0])
pl.plot(cor[:, 126])
pl.plot(cor[:, 256])
'''