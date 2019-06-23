# Built-in models for peak fitting from lmfit

import numpy as np
from lmfit.models import LorentzianModel, \
                         GaussianModel, \
                         PseudoVoigtModel, \
                         LinearModel


def gauss(x, amp, center, sigma):
    '''
        Returns array
    '''
    f = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-center)/sigma)**2)
    return f

def gauss_mod(N):
    '''
        Returns a model consisting of N gaussian curves
    '''
    # initialize model
    model = GaussianModel(prefix='gau1_')
    # Add N-1 gaussians
    for i in range(N-1):
        model += GaussianModel(
            prefix='gau' + str(i+2) + '_'
        )
    return model

def lor_mod(N):
    '''
        Returns a model consisting of N lorentzian curves
    '''
    # initialize model
    model = LorentzianModel(prefix='lor1_')
    # Add N-1 lorentzians
    for i in range(N-1):
        model += LorentzianModel(
            prefix='lor' + str(i+2) + '_'
        )
    return model

def voigt_mod(N):
    '''
        Returns a model consisting of N pseudo-voigt curves
    '''
    # initialize model
    model = PseudoVoigtModel(prefix='voi1_')
    # Add N-1 pseudo-voigts
    for i in range(N-1):
        model += PseudoVoigtModel(
            prefix='voi' + str(i+2) + '_'
        )
    return model

def line_mod(N):
    '''
        Returns a model consisting of N lines 
    '''
    # initialize model
    model = LinearModel(prefix='lin1_')
    # Add N-1 lines
    for i in range(N-1):
        model += LinearModel(
            prefix='lin' + str(i+2) + '_'
        )
    return model
