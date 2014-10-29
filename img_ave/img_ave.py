#!/usr/bin/env python
# encoding: utf-8
"""
img_ave.py - average images across argonne trials

Created by Dave Williams on 2014-09-29
"""

import os, sys
import warnings
import numpy as np
from PIL import Image
from scipy.io import loadmat


## File name handling

def tiff_name_parse(tn):
    """Parse out a tiff name to moth, trial, and image number"""
    moth = fn.split('-')[0].strip('Moth')
    trial = int(fn.split('-')[1].split('_')[0].strip('P1'))
    im_num = int(fn.split('-')[1].split('_')[1].strip('.tif'))
    return moth, trial, im_num

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


# Begin things I cut-and-paste used.

def get_tiffs_in_dir(dir):
    """Change into the specified directory and get a list of tiffs there."""
    # Get to the right directory
    try: 
        os.chdir(dir)
    except:
        raise Exception("No such dir, is it a full path?")
    fns = os.listdir(os.getcwd())
    # Ignore non-tiffs
    istiff = lambda s: s.endswith('tif') or s.endswith('tiff')
    fns = filter(istiff, fns)
    return fns

def get_trial_dirs_in_dir(dir):
    """Return all the directories that are like 'T002'"""
    os.chdir(dir)
    dirnames = os.walk('.').next()[1]
    return filter(lambda d: d.startswith('T'), dirnames)

def redo_dirs(dir):
    """Take the files in the directory and split them into sub directories by
    trial. Name the subdirectories after the trials they represent. Rename the
    files to reflect the fact that the subdirectory contains the trial number.
    """
    fns = get_tiffs_in_dir(dir)
    # Lambdas for names
    moth = lambda fn: fn.split('-')[0].strip('Moth')
    trial = lambda fn: int(fn.split('-')[1].split('_')[0][2:])
    im_num = lambda fn: int(fn.split('-')[1].split('_')[1].strip('.tif'))
    # Get trial names and make dirs
    trialset = list(set([trial(f) for f in fns])) 
    [os.mkdir("T%03i"%i) for i in trialset]  # make dirs
    # Move files
    mvfile = lambda fn: os.rename(fn, "T%03i/%03i.tif"%(trial(fn), im_num(fn)))
    [mvfile(fn) for fn in fns]

def img_mean(fns):
    """Average a list of images (filenames in fns) in the current dir"""
    # Create blank image
    width, height = Image.open(fns[0]).size
    mean = np.zeros((height, width), np.float)
    # Process each image
    for fn in fns:
        mean += np.array(Image.open(fn), dtype=np.float)/len(fns)
    return mean

def np_to_tiff(array, name):
    """Convert an np array of floats to a 32 bit tiff (thanks PILLOW)"""
    iarray = np.array(np.round(array), dtype=np.uint32)
    img_out = Image.fromarray(iarray, mode='I')
    img_out.save(name)


# Actual top level functions

def non_precess_ave(dir):
    """Average the images in a directory, from a non precessing trial.
    This means take the mean of every fifth image.
    """
    origdir = os.getcwd()
    fns = get_tiffs_in_dir(dir)
    if len(fns)>505 or len(fns)<490:
        warnings.warn('Number of files seems high or low. Check on it.')
    # Divide tiffs into the five sets non-precessive trials have
    fn_by_time = [fns[i::5] for i in range(5)]
    # Get means
    means = [img_mean(fns) for fns in fn_by_time]
    # Save as TIFs
    for i in range(len(means)):
        name = '../'+os.getcwd().split('/')[-1]+'Mean%03i.tif'%i
        np_to_tiff(means[i], name)
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
    if len(fns)>605 or len(fns)<590:
        warnings.warn('Number of tiffs seems high or low. Check on it.')
    # Divide tiffs into the 200 sets precessive trials have
    times = np.round(np.arange(interframe, loopdur*len(fns), interframe)
                     [:len(fns)]%loopdur, 1)
    fn_order = np.argsort(times)
    round_comp = lambda a,b: np.round(a, 1) == np.round(b, 1)
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
    time_and_mean = [[tf[0], img_mean(tf[1])] for tf in time_and_fn]
    outdir = '../'+dir.split('/')[-1]+'_means'
    os.mkdir(outdir)
    make_out_name = lambda t: outdir+'/time%04.1f.tif'%t
    [np_to_tiff(tm[1], make_out_name(tm[0])) for tm in time_and_mean]
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

def parse_dirs_for_moth(mothdir):
    """Look through all the trial directories in a moth's dir and run
    precess_ave or non_precess_ave on them
    """
    
# Precessing log filenames
fns = [
    'MothB6-P10012_.log',
    'MothB6-P10013_.log',
    'MothB6-P10023_.log',
    'MothB6-P10024_.log',
    'MothB6-P10025_.log',
    'MothB6-P10032_.log',
    'MothB6-P10033_.log',
    'MothB7-P10009_.log',
    'MothB8-P10011_.log',
    'MothB8-P10012_.log',
    'MothB8-P10019_.log',
    'MothB8-P10020_.log',
    'MothB8-P10027_.log',
    'MothB8-P10028_.log',
    'MothB9-P10012_.log',
    'MothB9-P10013_.log',
    'MothB9-P10021_.log',
    'MothB9-P10022_.log',
    'MothB9-P10033_.log',
    'MothB9-P10034_.log',
    'MothB9-P10035_.log',
    'MothB12-P10012_.log',
    'MothB12-P10013_.log',
    'MothB12-P10023_.log',
    'MothB12-P10024_.log',
    'MothB12-P10025_.log',
    'MothB12-P10033_.log',
    'MothB12-P10034_.log',
    'MothB12-P10035_.log',
    'MothB12-P10036_.log',
    'MothB13-P10010_.log',
    'MothB13-P10011_.log',
    'MothB13-P10012_.log',
    'MothB13-P10013_.log',
    'MothB13-P10036_.log',
    'MothB13-P10037_.log',  #not super sure about this due to numbering
    'MothB14-P10013_.log',
    'MothB14-P10014_.log',
    'MothB14-P10022_.log',
    'MothB14-P10023_.log',
    'MothB14-P10031_.log',
    'MothB14-P10032_.log',
    'MothB16-P10011_.log',
    'MothB16-P10012_.log',
    'MothB16-P10023_.log',
    'MothB16-P10024_.log',
    'MothB16-P10040_.log',
    'MothB16-P10041_.log',
    'MothB19-P10010_.log',
    'MothB19-P10011_.log',
    'MothB19-P10019_.log',
    'MothB19-P10021_.log',
    'MothB19-P10029_.log',
]
