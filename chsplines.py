#!/bin/env/python
# coding: utf-8

# This script is written by Makoto NAGAI at NAOJ

import numpy

def pL(x):
#def phi_value_left(x):
	return 2*(x-0.5)**3 - 3*(x-0.5)/2 + 0.5

def pR(x):
#def phi_value_right(x):
	return -2*(x-0.5)**3 + 3*(x-0.5)/2 + 0.5

def pdL(x):
#def phi_deriv_left(x):
	return (x-2./3.)**3 - (x-2./3.)/3 + 2./27

def pdR(x):
#def phi_deriv_right(x):
	return (x-1./3.)**3 - (x-1./3.)/3 - 2./27

def make_func(xmin, xmax, n_interval=10):
	deltaX = (xmax-xmin)/float(n_interval)
#	print(deltaX)
	
	''' Dynamic definition of a function ''' 
	from types import FunctionType
	
	args_dummy_s = 's000'
	args_dummy_a = 'a000'
	for i in range(1, n_interval+1):
		args_dummy_s = args_dummy_s+', s{0:03}'.format(i)
		args_dummy_a = args_dummy_a+', a{0:03}'.format(i)
#	print(args_dummy_s)
#	print(args_dummy_a)
	
	source = 'def foo(x, {0}, {1}): s = numpy.array([{0}]); a = numpy.array([{1}]); norm = (x-{2})/{3}; idInterval = ((x-{2})/{3}).astype(int); d = norm - idInterval; sL = s[idInterval]*pL(d); res = sL+a[idInterval]*pdL(d)+s[idInterval+1]*pR(d)+a[idInterval+1]*pdR(d); return res'.format(args_dummy_s, args_dummy_a, xmin, deltaX)
#	print(source) # Here, x is a numpy array. 

	foo_code = compile(source, "<string>", "exec")
	foo_func = FunctionType(foo_code.co_consts[0], globals(), "foo")
	return foo_func

