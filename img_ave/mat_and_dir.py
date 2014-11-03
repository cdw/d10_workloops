#!/usr/bin/env python
# encoding: utf-8
"""
mat_and_dir.py - reorganize directories and read in .MAT files

Let's be honest here, this is storage for stuff we don't need in
fn_parse_and_sort.

Created by Dave Williams on 2014-11-03
"""

import os
from scipy.io import loadmat
from fn_parse_and_sort import chchdir

## Post processing of dirs

def get_trial_dirs_in_dir(dirname):
    """Return all the directories that are like 'T002'"""
    chchdir(dirname)
    dirnames = os.walk('.').next()[1]
    return filter(lambda d: d.startswith('T'), dirnames)

def tiff_name_parse(fn):
    """Parse out a tiff name to moth, trial, and image number"""
    moth = fn.split('-')[0].strip('Moth')
    trial = int(fn.split('-')[1].split('_')[0][2:])
    im_num = int(fn.split('-')[1].split('_')[1].strip('.tif'))
    return moth, trial, im_num


## .MAT file processing

def parse_mat(fn):
    """Load data from a .mat file, namely Argonne_2013_mothdata_sansWL.mat"""
    mat = loadmat(fn, chars_as_strings=True, struct_as_record=False,
                  squeeze_me=True)
    data = mat.items()[0][-1]
    return data

def extract_precession(data):
    """From .mat file, create dict of moths and trial precession values"""
    precession = dict([(d.moth_label, map(bool, d.precess)) for d in data])
    return precession

