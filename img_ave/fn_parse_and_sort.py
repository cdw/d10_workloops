#!/usr/bin/env python
# encoding: utf-8
"""
fn_parse_and_sort.py - parse and sort the run's file names

Created by Dave Williams on 2014-09-29
"""

import os, sys
from scipy.io import loadmat

def tiff_name_parse(fn):
    """Parse out a tiff name to moth, trial, and image number"""
    moth = fn.split('-')[0].strip('Moth')
    trial = int(fn.split('-')[1].split('_')[0][2:])
    im_num = int(fn.split('-')[1].split('_')[1].strip('.tif'))
    return moth, trial, im_num

def trial_image_sets_in_dir(dir):
    """Given a moth directory, return a dictionary with the trial numbers as
    keys to a list of the file names in that trial"""
    # Get all the tiffs
    chchdir(dir)
    fns = os.listdir(os.getcwd())
    tiffs = get_tiffs_in_dir(dir)
    # Find all the trials
    trial = lambda fn: int(fn.split('-')[1].split('_')[0][2:])
    t_info = [trial(f) for f in tiffs]
    unique_trials = list(set(t_info))
    # Sort by trial
    output = {} 
    for trial_num in unique_trials:
        is_trial = lambda fn: trial(fn) == trial_num
        output[str(trial_num)] = filter(is_trial, tiffs)
    return output

## Post processing of dirs

def get_trial_dirs_in_dir(dir):
    """Return all the directories that are like 'T002'"""
    chchdir(dir)
    dirnames = os.walk('.').next()[1]
    return filter(lambda d: d.startswith('T'), dirnames)


## .MAT file processing

def parse_mat(fn):
    """Load data from a .mat file, namely Argonne_2013_mothdata_sansWL.mat"""
    m = loadmat(fn, chars_as_strings=True, struct_as_record = False, 
                squeeze_me = True)
    data = m.items()[0][-1]
    return data

def extract_precession(data):
    """From .mat file, create dict of moths and trial precession values"""
    precession = dict([(d.moth_label, map(bool, d.precess)) for d in data])
    return precession


## Small utility function

def chchdir(dir):
    """Checked chdir"""
    try: 
        os.chdir(dir)
    except:
        raise Exception("No such dir, is it a full path?")
    return

def get_tiffs_in_dir(dir):
    """Change into the specified directory and get a list of tiffs there."""
    chchdir(dir)
    fns = os.listdir(os.getcwd())
    istiff = lambda s: s.endswith('tif') or s.endswith('tiff')
    return filter(istiff, fns)


