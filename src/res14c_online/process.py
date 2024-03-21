#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
**Radiocarbon Resolution Calculator**

Created on 20.3.2024

This script is designed to calculate the expected temporal resolution
of radiocarbon dating based on the expected actual age of the samples.

Author:	Peter Demján, Institute of Archaeology of the Czech Academy of Sciences <peter.demjan@gmail.com>
Home:	https://github.com/demjanp/res14c_online

Usage:	process.py [-h] [-from FROM] [-to TO] [-uncert UNCERT] [-curve CURVE] 
				[-result RESULT] [-max_cpus MAX_CPUS] [-max_queue MAX_QUEUE]
options:
  -h, --help            show this help message and exit
  -from FROM            Lower bound in years AD. Use negative values for BC 
						(default: -20000)
  -to TO                Upper bound in years AD. Use negative values for BC 
						(default: 1950)
  -uncert UNCERT        Basic measurement uncertainty for 0 BP (1950 AD) (default: 15)
  -curve CURVE          File path to load the radiocarbon age calibration curve 
						(default: intcal20.14c)
  -result RESULT        File path to store the result in CSV format 
						(default: c14_resolution_data.csv)
  -max_cpus MAX_CPUS    Maximum number of CPUs to use (-1 = all available) (default: -1)
  -max_queue MAX_QUEUE  Maximum number of jobs in the queue. 
						Use higher values on machines with sufficient RAM (>8 GB)
                        (default: 100)

'''

from lib.fnc_radiocarbon import (load_calibration_curve, calibrate, calc_range)
from lib.fnc_mp import process_mp

from scipy.interpolate import interp1d
from collections import defaultdict
import numpy as np
import argparse
import sys
import os

def calc_precentile(rng, Ps, k):
	# rngs = [range, ...]
	# Ps = [P, ...]; in order of rngs; probabilities of the particular ranges
	# k = percentile value (0..1)
	
	rng = rng.copy()
	Ps = Ps.copy()
	
	Ps = Ps[np.argsort(rng)]
	rng.sort()
	
	Ps_sum = np.cumsum(Ps)
	k_norm = k * Ps_sum[-1]
	idx = np.argmin(np.abs(Ps_sum - k_norm))
	if Ps_sum[idx] < k_norm:
		idx += 1
	return rng[idx]

def worker_fnc(params, uncert, curve, cal_BP):
	
	c14age, = params
	
	u = uncert * np.exp(c14age / (2*8033))
	
	dist = calibrate(c14age, u, curve[:,1], curve[:,2])
	dist = interp1d(curve[:,0], dist)(cal_BP)
	rng_min, rng_max = calc_range(cal_BP, dist)
	
	return dist, rng_max - rng_min, u

def collect_fnc(data, results):
	
	dist, rng, u = data
	results.append([dist, rng, u])

def parse_arguments(args):
	
	parser = argparse.ArgumentParser(description="Calculate expected resolution of radiocarbon dating", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-from', type=int, default=-20000, required=False, help="Lower bound in years AD. Use negative values for BC")
	parser.add_argument('-to', type=int, default=1950, required=False, help="Upper bound in years AD. Use negative values for BC")
	parser.add_argument('-uncert', type=int, default=15, required=False, help="Basic measurement uncertainty for 0 BP (1950 AD)")
	parser.add_argument('-curve', type=str, default="intcal20.14c", required=False, help="File path to load the radiocarbon age calibration curve")
	parser.add_argument('-result', type=str, default="c14_resolution_data.csv", required=False, help="File path to store the result in CSV format")
	parser.add_argument('-max_cpus', type=int, default=-1, required=False, help="Maximum number of CPUs to use (-1 = all available)")
	parser.add_argument('-max_queue', type=int, default=100, required=False, help="Maximum number of jobs in the queue. Use higher values on machines with sufficient RAM (>8 GB)")
	parsed_args = parser.parse_args(args)
	
	return vars(parsed_args)  # Directly return parsed arguments as a dictionary


if __name__ == '__main__':
	  
	arguments = parse_arguments(sys.argv[1:])
	max_cpus = arguments["max_cpus"]
	max_queue_size = arguments["max_queue"]
	cal_BP_from = 1950 + 1 - arguments["to"]
	cal_BP_to = 1950 + 1 - arguments["from"]
	uncert = arguments["uncert"]
	curve_path = arguments["curve"]
	fresult = arguments["result"]
	
	curve = load_calibration_curve(curve_path, interpolate = False)
	
	uncert_max = uncert * np.exp(cal_BP_to / (2*8033))
	
	print()
	print("Uncertainty at 0 BP: %f" % (uncert))
	print("Maximal Uncertainty: %f" % (uncert_max))
	
	c14_rng = curve[(curve[:,0] >= cal_BP_from) & (curve[:,0] <= cal_BP_to)][:,1]
	c14_from = max(0, int(round(c14_rng.min() - 2*uncert_max)))
	c14_to = int(round(c14_rng.max() + 2*uncert_max))
	
	cal_BP = np.arange(curve[:,0].min(), curve[:,0].max(), 0.5)
	
	params_list = [[c14age] for c14age in range(c14_from, c14_to + 1)]
	
	print()
	print("Calculating ranges")
	
	results = []
	process_mp(worker_fnc, params_list, [uncert, curve, cal_BP], collect_fnc = collect_fnc, collect_args = [results], progress_fnc = True, max_cpus = max_cpus, max_queue_size = max_queue_size)
	
	cal_BP_idxs = np.where((cal_BP >= cal_BP_from) & (cal_BP <= cal_BP_to))[0]
	
	collect = defaultdict(list) #  {year BP: [[rng, p, u], ...], ...}
	for dist, rng, u in results:
		for idx in cal_BP_idxs:
			collect[cal_BP[idx]].append([rng, dist[idx], u])
	
	print()
	print("Calculating means")
	
	res = []  # [[year BP, mean range, 5th percentile range, 95th percentile range], ...]
	cmax = len(cal_BP_idxs)
	cnt = 1
	for idx in cal_BP_idxs[::-1]:
		print("\r%d/%d          " % (cnt, cmax), end = "")
		cnt += 1
		year = cal_BP[idx]
		collect[year] = np.array(collect[year])
		m = (collect[year][:,0] * collect[year][:,1]).sum() / collect[year][:,1].sum()  # mean
		u_mean = (collect[year][:,2] * collect[year][:,1]).sum() / collect[year][:,1].sum()  # mean uncertainty used
		perc5 = calc_precentile(collect[year][:,0], collect[year][:,1], 0.05)
		perc95 = calc_precentile(collect[year][:,0], collect[year][:,1], 0.95)
		res.append([year, m, perc5, perc95, u_mean])
	
	text = "Sample Age,Mean Resolution,5th Percentile Resolution,95th Percentile Resolution, Uncertainty Used\n"
	for year, m, perc5, perc95, u_mean in res:
		text += "%f,%f,%f,%f,%f\n" % (1950 - year + 1, m, perc5, perc95, u_mean)
	with open(fresult, "w") as f:
		f.write(text)
	
	print()
	print()
	print("Result saved in %s" % (os.path.normpath(os.path.abspath(fresult))))
	print()
