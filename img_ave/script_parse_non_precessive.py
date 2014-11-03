#!/usr/bin/env python
# encoding: utf-8
"""
SCRIPT_test_parse.py - test our parsers

Created by Dave Williams on 2014-09-29
"""

import fn_parse_and_sort as pns
import img_ave


in_dir = '/Volumes/APSWORKING/Argonne_2013_temperature_workloops/Detector_1' 
out_dir = '/Volumes/APSWORKING/Argonne_2013_temperature_workloops/Detector_1/non_precessive_means'
to_parse = {
    'MothB4': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    'MothB6': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20,
               21, 22, 26, 27, 28, 29, 30, 31, 34],
    'MothB7': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
               20, 21, 22, 23],
    'MothB8': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 21, 22, 
               23, 24, 25, 26],
    'MothB13': [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                23, 24, 25, 28, 29, 30, 31, 32, 33, 34],
    'MothB12': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 26, 27, 28, 29, 30, 31, 32, 33],
    'MothB9': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20,
               23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36],
    'MothB19': [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 22, 23,
                24, 25, 26, 27, 28],
    'MothB14': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20,
                21, 24, 25, 26, 27, 28, 29, 30],
    'MothB16': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
                39]
}

for moth in to_parse:
    print "Working on moth: %s"%moth
    dir = in_dir+'/'+moth
    fn_by_trial = pns.trial_image_sets_in_dir(dir)
    for trial_num in to_parse[moth]:
        tiffs = fn_by_trial[str(trial_num)]
        img_ave.non_precess_ave(dir, tiffs, out_dir)

