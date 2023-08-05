#!/bin/env/python
# coding: utf-8

# This script is written by Makoto NAGAI at NAOJ

import sys
import os
import math
import numpy
import lmfit

import ddsv
import chsplines

def fit(xFit, yFit, x_min, x_max, n_interval, y_min=-100, y_max=100, dy_min=-100, dy_max=100):
	func = chsplines.make_func(x_min, x_max, n_interval)
#	print(func)
	model=lmfit.Model(func)
	model.make_params(verbose=False)
	nParam = len(model.param_names)
	for i in range(0, nParam//2):
		model.set_param_hint('s{:03}'.format(i), value=0, min=y_min, max=y_max)
		model.set_param_hint('a{:03}'.format(i), value=0, min=dy_min, max=dy_max)
	print('parameter:', model.param_names, 'independent_variables:',model.independent_vars)

	result=model.fit(yFit, x=xFit)
#	print(result.fit_report())
	return result


def work(filename, x_idColumn, y_idColumn, n_interval):
	dat = ddsv.trimmer1.trim(ddsv.load(filename))
	xStart = dat[0][x_idColumn]
	xEnd = dat[-1][x_idColumn]
	if xStart < xEnd:
		x = [float(d[x_idColumn]) for d in dat]
		y = [float(d[y_idColumn]) for d in dat]
	else:
		x = [float(d[x_idColumn]) for d in reversed(dat)]
		y = [float(d[y_idColumn]) for d in reversed(dat)]
	result=fit(x, y, x[0], x[-1]+(x[-1]-x[-2]), n_interval)
	print(result.fit_report())
	
	ddsvres = [['#']]
	for i in range(len(x)):
		ddsvres.append([x[i], y[i], result.best_fit[i]])
	ddsv.dump(ddsvres, "result.txt")

def work_with_mask(filename, x_idColumn, y_idColumn, mask_idColumn, n_interval):
	dat = ddsv.trimmer1.trim(ddsv.load(filename))
	xStart = dat[0][x_idColumn]
	xEnd = dat[-1][x_idColumn]
	x = [float(d[x_idColumn]) for d in dat]
	y = [float(d[y_idColumn]) for d in dat]
	mask  = [int(d[mask_idColumn]) for d in dat]
	'''
	if xStart < xEnd:
		x = [float(d[x_idColumn]) for d in dat]
		y = [float(d[y_idColumn]) for d in dat]
		mask  = [int(d[mask_idColumn]) for d in dat]
		invert = False
	else:
		x = [float(d[x_idColumn]) for d in reversed(dat)]
		y = [float(d[y_idColumn]) for d in reversed(dat)]
		mask  = [int(d[mask_idColumn]) for d in reversed(dat)]
		invert = True
	'''
	ind_no_mask = numpy.where(numpy.array(mask)<1)
#	print(ind_no_mask)
	xFit = numpy.array(x)[ind_no_mask]
	yFit = numpy.array(y)[ind_no_mask]
	result=fit(xFit, yFit, x[0], x[-1]+(x[-1]-x[-2]), n_interval)
#	print(result.fit_report())
	
	res = result.eval(x=numpy.array(x))
	n = len(dat)
	res = [dat[i]+[y[i]-res[i]] for i in range(n)]
	fname=os.path.splitext(filename)[0]
#	print(fname)
	ddsv.dump(res, "{0}_base{1}.txt".format(fname, n_interval))

def work_with_mask_n_sweep(filename, x_idColumn, y_idColumn, mask_idColumn, n_min, n_max):
	dat = ddsv.trimmer1.trim(ddsv.load(filename))
	xStart = dat[0][x_idColumn]
	xEnd = dat[-1][x_idColumn]
	x = [float(d[x_idColumn]) for d in dat]
	y = [float(d[y_idColumn]) for d in dat]
	mask  = [int(d[mask_idColumn]) for d in dat]
	ind_no_mask = numpy.where(numpy.array(mask)<1)
	xFit = numpy.array(x)[ind_no_mask]
	yFit = numpy.array(y)[ind_no_mask]
	
	info = []
	for n_interval in range(n_min, n_max+1):
		result=fit(xFit, yFit, x[0], x[-1]+(x[-1]-x[-2]), n_interval)
#		print(result.fit_report())
		info.append([n_interval, result.chisqr, result.redchi, result.aic, result.bic])
	fname=os.path.splitext(filename)[0]
#	print(fname)
	ddsv.dump(info, "{0}_info.txt".format(fname))

	
def main(args):
	if len(args) == 4:
		filename = args[0]
		x_idColumn = int(args[1])
		y_idColumn = int(args[2])
		n_interval = int(args[3])
		work(filename, x_idColumn, y_idColumn, n_interval)
	elif len(args) == 5:
		filename = args[0]
		x_idColumn = int(args[1])
		y_idColumn = int(args[2])
		mask_idColumn = int(args[3])
		n_interval = int(args[4])
		work_with_mask(filename, x_idColumn, y_idColumn, mask_idColumn, n_interval)
	elif len(args) == 6:
		filename = args[0]
		x_idColumn = int(args[1])
		y_idColumn = int(args[2])
		mask_idColumn = int(args[3])
		n_min = int(args[4])
		n_max = int(args[5])
		work_with_mask_n_sweep(filename, x_idColumn, y_idColumn, mask_idColumn, n_min, n_max)
	else:
		print("Usage: python lst2_chsplines.py filename.txt x_idColumn y_idColumn n_intervals")
		print("Usage: python lst2_chsplines.py filename.txt x_idColumn y_idColumn mask_idColumn n_intervals")
		print("Usage: python lst2_chsplines.py filename.txt x_idColumn y_idColumn mask_idColumn n_min n_max")

if __name__ == '__main__':
	args = sys.argv
	main(args[1:])
