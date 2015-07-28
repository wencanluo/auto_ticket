#!/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import json
import sys

def remove_file(file):
    if is_exist(file):
        os.remove(file)

def clean_dir(path):
    cmd = 'rm ' + os.path.join(path, '*.*')
    os.system(cmd)
    
def new_path(path):
	if not os.path.exists(path):
		os.makedirs(path)

def is_exist(file):
	return os.path.isfile(file)
    
def save_list(List, file, linetag="\n"):
	"""
	Save a list into a file. Each item is a line
	"""
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	f = open(file, "w")
	for item in List:
		f.write(str(item))
		f.write(linetag)
	f.flush()
	f.close()

def save_dict(dict, file, SortbyValueflag = False):
	"""
	@function:save a dict
	@param dict: dictionary
	"""
	SavedStdOut = sys.stdout
	sys.stdout = open(file, 'w')
	
	if SortbyValueflag:
		for key in sorted(dict, key = dict.get, reverse = True):
			print str(key) + "\t" + str(dict[key])
	else:
		for key in sorted(dict.keys()):
			print str(key) + "\t" + str(dict[key])
	sys.stdout = SavedStdOut    
    
def save_dict2json(dict, file):
	with open(file, "w") as fout:
		json.dump(dict, fout, indent=2, encoding="utf-8")
        
def load_dictjson(file):
	with open(file, "r") as fin:
		dict = json.load(fin, encoding="utf-8")
	return dict
    
def read_matrix(file, hasHead=True):
	"""
	Function: Load a matrix from a file. The matrix is M*N
	@param file: string, filename
	@param hasHead: bool, whether the file has a header
	"""
	tm = []
	for line in open(file):
		row = []
		line = line.strip()
		if len(line) == 0: continue
		for num in line.split("\t"):
			row.append(num.strip())
		tm.append(row)
        
	if hasHead:
		header = tm[0]
		body = tm[1:]
		return header, body
	else:
		return tm

def write_matrix(file, data, header=None):
	"""
	Function: save a matrix to a file. The matrix is M*N
	@param file: string, filename
	@param data: M*N matrix,  
	@param header: list, the header of the matrix
	"""
	reload(sys)
	sys.setdefaultencoding('utf8')
    
	SavedStdOut = sys.stdout
	sys.stdout = open(file, 'w')
	
	if header != None:
		for j in range(len(header)):
			label = header[j]
			if j == len(header)-1:
				print label
			else:
				print label, "\t",
	for row in data:
		for j in range(len(row)):
			col = row[j]
			if j == len(row) - 1:
				print col
			else:
				print col, "\t",
	
	sys.stdout = SavedStdOut    
    
