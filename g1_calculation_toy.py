#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 15:09:50 2020

@author: delis
"""

c = 3E2 #μm/ps
hbar = 6.582119569 * 1E2 # μeV ps

import os
from scipy.fftpack import fft2, ifft2
import numpy as np
import external as ext
from qutip import *

parallel_tasks = 512
n_batch = 128
n_internal = parallel_tasks//n_batch
qutip.settings.num_cpus = n_batch

N = 2**7
L = 2**7
hatt = 1 #ps
hatx = 1 #μm
hatpsi = 1/hatx #μm^-1

star_m = 5e-6
gamma0 = 0.19 #ps^-1
gammar = 0.015 #ps^-1
gamma2 = 100/hbar #μm^2 ps^-1

P = 1.026e2
R = 5e-5

p = P*R / (gamma0*gammar)
ns = gammar/R
n0 = ns*(p-1)
nres = P/(gammar+R*n0)
gr = 0.025
g = 4.42

def arrays():
    x_0 = - N * dx / 2
    kx0 = - np.pi / dx
    x = x_0 + dx * np.arange(N)
    kx = kx0 + dkx * np.arange(N)
    return x, kx

L *= hatx
L /= hatx
dx = L/N
dkx = 2 * np.pi / (N * dx)
x, kx =  arrays()
X, Y = np.meshgrid(x, x)
KX, KY = np.meshgrid(kx, kx)

m =  star_m * 0.510998950 * 1E12 / c**2 #μeV/(μm^2/ps^2)
star_gamma_l0 = (gamma0*hbar)  # μeV 
star_gamma_l2 = (gamma2*hbar) # μeV μm^2 
star_gamma_r = (gammar*hbar) # μeV

time_steps = 100000
dt = 4e-2 * hatt
every = 100
i1 = 0
i2 = time_steps
lengthwindow = i2-i1
t = ext.time(dt, time_steps, i1, i2, every)

#np.savetxt('/Users/delis/Desktop/dt.dat', np.arange(1001))
#np.savetxt('/Users/delis/Desktop/dr_2_7,dat', x-x[0])

print('--- Energy scales ---')
print(r'losses/kinetic %.4f' % (hbar*gamma0/(hbar**2/(2*abs(m)*dx**2))))
print(r'p-p interaction/kinetic %.4f' % (g*n0/(hbar**2/(2*abs(m)*dx**2))))
print(r'p-r interaction/kinetic %.4f' % (gr*nres/(hbar**2/(2*abs(m)*dx**2))))
print(r'Total blueshift from interactions in μeV %.4f' % (g*n0 + gr*nres))
print(r'Truncated Wigner  ratio %.4f' % (g/(hbar*gamma0*dx**2)))
print(r'dx/healing length %.4f' % (dx / (hbar/np.sqrt(2*abs(m)*g*n0))))
print('--- Losses ---')
print('gamma_0 in μeV %.4f' % star_gamma_l0)
print('gamma_r in μeV %.4f' % star_gamma_r)
print('gamma_2 in μeV μm^2 %.4f' % star_gamma_l2)
print('--- Interactions ---')
print('Polariton-reservoir in μeV μm^2 %.4f' % gr)
print('Polariton-polariton in μev μm^2 %.4f' % g)
print('--- Densities ---')
print('Saturation in μm^-2 %.2f' % (gammar/R))
print('Steady-state in μm^-2 %.2f' % n0)
print('Reservoir in μm^-2 %.2f' % (nres))
print('--- Dimensionless pump ---')
print('p %.4f' % p)

def finalparams():
    alpha = 1
    beta = 0
    #om = 50*gamma0
    #alpha = 1 + p*gr*gamma0/(hbar*om*R)
    #beta = p*gamma0/(2*om)
    Kc = (hatt/hatx**2) * hbar/(2*m)
    Kd = (hatt/hatx**2) * gamma2/2
    rc = hatt * p*gamma0*gr/(R*hbar)
    rd = hatt * gamma0*(p-1)/2
    ud = hatt/(hatx**2) * p*R*gamma0/(2*gammar)
    uc = hatt/(hbar*hatx**2) * g*(1 - p*(gr/g)*(gamma0/gammar))
    sigma = hatt * gamma0*(p+1)/(2*dx**2)
    z = alpha + beta*1j
    return Kc, Kd, rc, rd, uc, ud, sigma, z

def bogoliubov():
    z = 1
    r = (1/z).real
    q = (1/z).imag
    n0 = (rd - z.imag*rc/z.real)/(ud + uc*z.imag/z.real)
    omsol = (rc+n0*uc)/z.real
    a = -z.real*omsol + Kc*kx**2 + rc + 2*n0*uc
    b = -Kd*kx**2 + rd - 2*n0*ud - z.imag*omsol
    c = n0 * uc
    d = -n0 * ud
    im_plus = np.zeros(len(kx))
    im_minus = np.zeros(len(kx))
    #re_plus = np.zeros(len(kx))
    #re_minus = np.zeros(len(kx))
    for i in range(len(kx)):
        if (a[i]**2 - c**2 - d**2) < 0:
            im_plus[i] = b[i]*r + r*np.sqrt(np.abs(a[i]**2 - c**2 - d**2))
            im_minus[i] = b[i]*r - r*np.sqrt(np.abs(a[i]**2 - c**2 - d**2))
            #re_plus[i] = -b[i]*q + q*1j*np.sqrt(np.abs(a[i]**2 - c**2 - d**2))
            #re_minus[i] = -b[i]*q - q*1j*np.sqrt(np.abs(a[i]**2 - c**2 - d**2))
        else:
            im_plus[i] = b[i]*r + q*np.sqrt(a[i]**2 - c**2 - d**2)
            im_minus[i] = b[i]*r - q*np.sqrt(a[i]**2 - c**2 - d**2)
            ##re_plus[i] = -b[i]*q + r*np.sqrt(a[i]**2 - c**2 - d**2)
            #re_minus[i] = -b[i]*q - r*np.sqrt(a[i]**2 - c**2 - d**2)
    return im_plus, im_minus

class model:
    #def __init__(self, Kc, Kd, Kc2, rc, rd, uc, ud, sigma, z, psi_x=0):
        #self.Kc = Kc
        #self.Kd = Kd
        #self.Kc2 = Kc2
        #self.rc = rc
        #self.rd = rd
        #self.uc = uc
        #self.ud = ud
        #self.sigma = sigma
        #self.z = z
        #self.psi_x = psi_x
        #self.psi_x = np.full((N, N), 2)
        #self.psi_x /= hatpsi
        #self.psi_mod_k = fft2(self.psi_mod_x)
    def __init__(self, psi_x=0):
        self.sigma = hatt * gamma0*(p+1)/(2*dx**2)
        self.Kc = (hatt/hatx**2) * hbar/(2*m)
        self.Kd = (hatt/hatx**2) * gamma2/2
        self.psi_x = psi_x
        self.psi_x = np.full((N, N), 2)
        self.psi_x /= hatpsi
        self.psi_mod_k = fft2(self.psi_mod_x)

# =============================================================================
# Discrete Fourier pairs
# =============================================================================
    def _set_fourier_psi_x(self, psi_x):
        self.psi_mod_x = psi_x * np.exp(-1j * KX[0,0] * X - 1j * KY[0,0] * Y) * dx * dx / (2 * np.pi)

    def _get_psi_x(self):
        return self.psi_mod_x * np.exp(1j * KX[0,0] * X + 1j * KY[0,0] * Y) * 2 * np.pi / (dx * dx)

    def _set_fourier_psi_k(self, psi_k):
        self.psi_mod_k = psi_k * np.exp(1j * X[0,0] * dkx * np.arange(N) + 1j * Y[0,0] * dkx * np.arange(N))

    def _get_psi_k(self):
        return self.psi_mod_k * np.exp(-1j * X[0,0] * dkx * np.arange(N) - 1j * Y[0,0] * dkx * np.arange(N))

    psi_x = property(_get_psi_x, _set_fourier_psi_x)
    psi_k = property(_get_psi_k, _set_fourier_psi_k)
# =============================================================================
# Definition of the split steps
# =============================================================================
    def n(self):
        return np.abs(self.psi_x * np.conjugate(self.psi_x)) - 1/(2*dx**2)

    def n_r(self, nr_update):
        q = gammar + R*self.n()
        return P/q - P/q*np.exp(-q*dt/2) - nr_update*np.exp(-q*dt/2)

    def prefactor_x(self):
        self.uc_tilde = hatt/(hbar*hatx**2) * g*(self.n() + (hatx**2*gr/g) * (p*gamma0/R) * (1/(1+self.n()/(hatx**2*ns))))
        self.I_tilde = 1j*hatt*gamma0/2 * (p/(1+self.n()/(hatx**2*ns)) - 1)
        #return np.exp(-1j*0.5*dt*((self.rc + 1j*self.rd) + (self.uc - 1j*self.ud)*self.n())/self.z)
        return np.exp(-1j*0.5*dt*(self.uc_tilde + self.I_tilde))

    def prefactor_k(self):
        #return np.exp(-1j*dt*((KX**2 + KY**2)*(self.Kc - 1j*self.Kd)-(KX**4 + KY**4)*self.Kc2)/self.z)
        return np.exp(-1j*dt*((KX**2 + KY**2)*(self.Kc - 1j*self.Kd)))

# =============================================================================
# Time evolution
# =============================================================================
    def noise(self, shape):
        mu = 0
        sigma = 1  #standard deviation of the real gaussians, so the variance of the complex number is 2*sigma^2
        re = np.random.normal(mu, sigma, shape)
        im = np.random.normal(mu, sigma, shape)
        xi = re + 1j * im
        return xi

    def time_evolution(self, seed):
        g1_x = np.zeros(int(N/2), dtype = complex)
        d1_x = np.zeros(int(N/2))
        g2_x = np.zeros(int(N/2), dtype = complex)
        d2_x = np.zeros(int(N/2))
        g3_x = np.zeros(int(N/2), dtype = complex)
        d3_x = np.zeros(int(N/2))
        g4_x = np.zeros(int(N/2), dtype = complex)
        d4_x = np.zeros(int(N/2))
        g5_x = np.zeros(int(N/2), dtype = complex)
        d5_x = np.zeros(int(N/2))
        np.random.seed(seed)
        for i in range(time_steps+1):
            self.psi_x *= self.prefactor_x()
            self.psi_mod_k = fft2(self.psi_mod_x)
            self.psi_k *= self.prefactor_k()
            self.psi_mod_x = ifft2(self.psi_mod_k)
            self.psi_x *= self.prefactor_x()
            self.psi_x += np.sqrt(dt) * np.sqrt(self.sigma) * self.noise((N,N))
        for i in range(0, N, int(N/2)):
            g1_x += np.conjugate(self.psi_x[i, int(N/2)]) * self.psi_x[i, int(N/2):] / 2 + np.conjugate(self.psi_x[int(N/2), i]) * self.psi_x[int(N/2):, i] / 2
            d1_x += self.n()[i, int(N/2):] / 2 + self.n()[int(N/2):, i] / 2
        g1_x[0] -= 1/(2*dx**2)
        for i in range(0, N, int(N/4)):
            g2_x += np.conjugate(self.psi_x[i, int(N/2)]) * self.psi_x[i, int(N/2):] / 4 + np.conjugate(self.psi_x[int(N/2), i]) * self.psi_x[int(N/2):, i] / 4
            d2_x += self.n()[i, int(N/2):] / 4 + self.n()[int(N/2):, i] / 4
        g2_x[0] -= 1/(2*dx**2)
        for i in range(0, N, int(N/8)):
            g3_x += np.conjugate(self.psi_x[i, int(N/2)]) * self.psi_x[i, int(N/2):] / 8 + np.conjugate(self.psi_x[int(N/2), i]) * self.psi_x[int(N/2):, i] / 8
            d3_x += self.n()[i, int(N/2):] / 8 + self.n()[int(N/2):, i] / 8
        g3_x[0] -= 1/(2*dx**2)
        for i in range(0, N, int(N/32)):
            g4_x += np.conjugate(self.psi_x[i, int(N/2)]) * self.psi_x[i, int(N/2):] / 32 + np.conjugate(self.psi_x[int(N/2), i]) * self.psi_x[int(N/2):, i] / 32
            d4_x += self.n()[i, int(N/2):] / 32 + self.n()[int(N/2):, i] / 32
        g4_x[0] -= 1/(2*dx**2)
        for i in range(0, N, int(N/32)):
            g4_x += np.conjugate(self.psi_x[i, int(N/2)]) * self.psi_x[i, int(N/2):] / 32 + np.conjugate(self.psi_x[int(N/2), i]) * self.psi_x[int(N/2):, i] / 32
            d4_x += self.n()[i, int(N/2):] / 32 + self.n()[int(N/2):, i] / 32
        g4_x[0] -= 1/(2*dx**2)
        g5_x = np.conjugate(self.psi_x[int(N/2), int(N/2)]) * self.psi_x[int(N/2), int(N/2):]
        d5_x = self.n()[int(N/2), int(N/2):]
        g5_x[0] -= 1/(2*dx**2)
        return g1_x, d1_x, g2_x, d2_x, g3_x, d3_x, g4_x, d4_x, g5_x, d5_x

'''
Kc, Kd, rc, rd, uc, ud, sigma, z = finalparams()
print('--- Simulation Parameters ---')
print('Kc', Kc)
print('Kd', Kd)
print('rc', rc)
print('rd', rd)
print('uc', uc)
print('ud', ud)
print('σ', sigma)
print('z', z)
'''

def g1(i_batch):
    g1_x_batch = np.zeros(int(N/2), dtype=complex)
    d1_x_batch = np.zeros(int(N/2))
    g2_x_batch = np.zeros(int(N/2), dtype=complex)
    d2_x_batch = np.zeros(int(N/2))
    g3_x_batch = np.zeros(int(N/2), dtype=complex)
    d3_x_batch = np.zeros(int(N/2))
    g4_x_batch = np.zeros(int(N/2), dtype=complex)
    d4_x_batch = np.zeros(int(N/2))
    g5_x_batch = np.zeros(int(N/2), dtype=complex)
    d5_x_batch = np.zeros(int(N/2))
    seed = i_batch
    for i_n in range(n_internal):
        gpe = model()
        g1_x, d1_x, g2_x, d2_x, g3_x, d3_x, g4_x, d4_x, g5_x, d5_x = gpe.time_evolution(seed)
        g1_x_batch += g1_x / n_internal
        d1_x_batch += d1_x / n_internal
        g2_x_batch += g2_x / n_internal
        d2_x_batch += d2_x / n_internal
        g3_x_batch += g3_x / n_internal
        d3_x_batch += d3_x / n_internal
        g4_x_batch += g4_x / n_internal
        d4_x_batch += d4_x / n_internal
        g5_x_batch += g5_x / n_internal
        d5_x_batch += d5_x / n_internal
        print('The core', i_batch, 'has completed realisation number', i_n)
        seed += n_batch
    name_g1_x = '/scratch/konstantinos/'+'g1_'+'g'+str(g)+'gr'+str(gr)+os.sep+'g1_x'+str(i_batch+1)+'.npy'
    name_d1_x = '/scratch/konstantinos/'+'d1_'+'g'+str(g)+'gr'+str(gr)+os.sep+'d1_x'+str(i_batch+1)+'.npy'
    name_g2_x = '/scratch/konstantinos/'+'g2_'+'g'+str(g)+'gr'+str(gr)+os.sep+'g2_x'+str(i_batch+1)+'.npy'
    name_d2_x = '/scratch/konstantinos/'+'d2_'+'g'+str(g)+'gr'+str(gr)+os.sep+'d2_x'+str(i_batch+1)+'.npy'
    name_g3_x = '/scratch/konstantinos/'+'g3_'+'g'+str(g)+'gr'+str(gr)+os.sep+'g3_x'+str(i_batch+1)+'.npy'
    name_d3_x = '/scratch/konstantinos/'+'d3_'+'g'+str(g)+'gr'+str(gr)+os.sep+'d3_x'+str(i_batch+1)+'.npy'
    name_g4_x = '/scratch/konstantinos/'+'g4_'+'g'+str(g)+'gr'+str(gr)+os.sep+'g4_x'+str(i_batch+1)+'.npy'
    name_d4_x = '/scratch/konstantinos/'+'d4_'+'g'+str(g)+'gr'+str(gr)+os.sep+'d4_x'+str(i_batch+1)+'.npy'
    name_g5_x = '/scratch/konstantinos/'+'g5_'+'g'+str(g)+'gr'+str(gr)+os.sep+'g5_x'+str(i_batch+1)+'.npy'
    name_d5_x = '/scratch/konstantinos/'+'d5_'+'g'+str(g)+'gr'+str(gr)+os.sep+'d5_x'+str(i_batch+1)+'.npy'
    np.save(name_g1_x, g1_x_batch)
    np.save(name_d1_x, d1_x_batch)
    np.save(name_g2_x, g2_x_batch)
    np.save(name_d2_x, d2_x_batch)
    np.save(name_g3_x, g3_x_batch)
    np.save(name_d3_x, d3_x_batch)
    np.save(name_g4_x, g4_x_batch)
    np.save(name_d4_x, d4_x_batch)
    np.save(name_g5_x, g5_x_batch)
    np.save(name_d5_x, d5_x_batch)

parallel_map(g1, range(n_batch))
g1_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'g1_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
d1_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'d1_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
D1_x = np.sqrt(d1_x[0]*d1_x)

g2_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'g2_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
d2_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'d2_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
D2_x = np.sqrt(d2_x[0]*d2_x)

g3_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'g3_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
d3_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'d3_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
D3_x = np.sqrt(d3_x[0]*d3_x)

g4_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'g4_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
d4_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'d4_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
D4_x = np.sqrt(d4_x[0]*d4_x)

g5_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'g5_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
d5_x = ext.ensemble_average_space(r'/scratch/konstantinos/'+'d5_'+'g'+str(g)+'gr'+str(gr), int(N/2), n_batch)
D5_x = np.sqrt(d5_x[0]*d5_x)

np.savetxt('/scratch/konstantinos/'+os.sep+'g'+str(g)+'gr'+str(gr)+'_1.dat', (np.abs(g1_x)/D1_x).real)
np.savetxt('/scratch/konstantinos/'+os.sep+'g'+str(g)+'gr'+str(gr)+'_2.dat', (np.abs(g2_x)/D2_x).real)
np.savetxt('/scratch/konstantinos/'+os.sep+'g'+str(g)+'gr'+str(gr)+'_3.dat', (np.abs(g3_x)/D3_x).real)
np.savetxt('/scratch/konstantinos/'+os.sep+'g'+str(g)+'gr'+str(gr)+'_4.dat', (np.abs(g4_x)/D4_x).real)
np.savetxt('/scratch/konstantinos/'+os.sep+'g'+str(g)+'gr'+str(gr)+'_5.dat', (np.abs(g5_x)/D5_x).real)