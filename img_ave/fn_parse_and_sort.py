#!/usr/bin/env python
# encoding: utf-8
"""
fn_parse_and_sort.py - parse and sort the run's file names

Created by Dave Williams on 2014-09-29
"""

import os

def trial_image_sets_in_dir(dirname):
    """Given a moth directory, return a dictionary with the trial numbers as
    keys to a list of the file names in that trial"""
    # Get all the tiffs
    chchdir(dirname)
    tiffs = get_tiffs_in_dir(dirname)
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


## Small utility function

def chchdir(dirname):
    """Checked chdir"""
    try:
        os.chdir(dirname)
    except:
        raise Exception("No such dir, is it a full path?")
    return

def get_tiffs_in_dir(dirname):
    """Change into the specified directory and get a list of tiffs there."""
    chchdir(dirname)
    fns = os.listdir(os.getcwd())
    istiff = lambda s: s.endswith('tif') or s.endswith('tiff')
    return filter(istiff, fns)


