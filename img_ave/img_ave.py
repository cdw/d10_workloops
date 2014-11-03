#!/usr/bin/env python
# encoding: utf-8
"""
img_ave.py - average images across argonne trials

Created by Dave Williams on 2014-09-29
"""

import os
import warnings
import numpy as np
from PIL import Image
from fn_parse_and_sort import get_tiffs_in_dir


## Image conversions and transforms

def _img_mean(fns):
    """Average a list of images (filenames in fns) in the current dir"""
    # Create blank image
    width, height = Image.open(fns[0]).size
    mean = np.zeros((height, width), np.float)
    # Process each image
    for fn in fns:
        mean += np.array(Image.open(fn), dtype=np.float)/len(fns)
    return mean

def _np_to_tiff(array, name):
    """Convert an np array of floats to a 32 bit tiff (thanks PILLOW)"""
    iarray = np.array(np.round(array), dtype=np.uint32)
    img_out = Image.fromarray(iarray, mode='I')
    img_out.save(name)


## Top level functions

def non_precess_ave(dir, fns=None, outdir=None):
    """Average the images in a directory or list of image names in a directory,
    from a non precessing trial. This means take the mean of every fifth image.
    """
    origdir = os.getcwd()
    os.chdir(dir)
    if fns is None:
        fns = get_tiffs_in_dir(dir)
    if len(fns) > 505 or len(fns) < 490:
        warnings.warn('Number of files seems high or low. Check on it.')
    # Divide tiffs into the five sets non-precessive trials have
    fn_by_time = [fns[i::5] for i in range(5)]
    # Get means
    means = [_img_mean(fns) for fns in fn_by_time]
    # Save as TIFs
    if outdir is not None:
        os.chdir(outdir)
    else:
        os.chdir('..')
    for i in range(len(means)):
        name = '%s_T%03i_Mean%03i.tif'%(fns[0].split('-')[0],
                int(fns[0].split('-')[1].split('_')[0][2:]), i)
        _np_to_tiff(means[i], name)
    os.chdir(origdir)

def precess_ave(dir, interframe=9, loopdur=40):
    """Average the images in a directory which contains images from a
    precessing trial. The interframe option lets you specify the time
    between frames. This means, assuming every image is 5.4ms from the
    last one and that we wrap at 40ms, the timings look something like:
        5.4,  10.8,  16.2,  21.6,  27. ,  32.4,  37.8,   3.2,   8.6,
        14. ,  19.4,  24.8,  30.2,  35.6
    Takes:
        dir: directory to look for images in
        interframe: time interval between frames, defaults to 9 ms
        loopdur: the duration of the loop, defaults to 40 ms
    Gives: 
        None
    """
    origdir = os.getcwd()
    fns = get_tiffs_in_dir(dir)
    if len(fns) > 605 or len(fns) < 590:
        warnings.warn('Number of tiffs seems high or low. Check on it.')
    # Divide tiffs into the 200 sets precessive trials have
    times = np.round(np.arange(interframe, loopdur*len(fns), interframe)
                     [:len(fns)]%loopdur, 1)
    fn_order = np.argsort(times)
    round_comp = lambda a, b: np.round(a, 1) == np.round(b, 1)
    curr_time = times[fn_order[0]]
    time_and_fn = [[curr_time, []]]
    for ind in fn_order:
        if round_comp(curr_time, times[ind]):
            time_and_fn[-1][-1].append(fns[ind])
        else:
            curr_time = times[ind]
            time_and_fn.append([curr_time, []])
            time_and_fn[-1][-1].append(fns[ind])
    # Average each set and record it to disk
    time_and_mean = [[tf[0], _img_mean(tf[1])] for tf in time_and_fn]
    outdir = '../'+dir.split('/')[-1]+'_means'
    os.mkdir(outdir)
    make_out_name = lambda t: outdir+'/time%04.1f.tif'%t
    [_np_to_tiff(tm[1], make_out_name(tm[0])) for tm in time_and_mean]
    os.chdir(origdir)
    # Doesn't look to be working quite right? Check timing.

def parse_log_for_interval(fn):
    """Parse a log file for the interframe interval (to nearest ms)"""
    raw = np.loadtxt(fn, skiprows=1, usecols=(2,), dtype=np.str)
    diffs = np.round(np.diff([float(r.split(':')[-1]) for r in raw[:-5]]), 5)
    times = list(set(diffs))
    counts = [np.count_nonzero(np.equal(diffs, t)) for t in times]
    print fn + '\n ---------'
    for pair in zip(times, counts):
        t = np.round(pair[0], 4)
        print str(t)+":  "+str(pair[1])
    print '\n ---------- \n\n'
    #TODO: check for function, left off here


