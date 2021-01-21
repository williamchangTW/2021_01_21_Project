# tmp: store temporary files
# others

import csv
import psutil as ps
import os
import numpy as np
import pandas as pd

# get file size
# get system memory infomation
# transfer data type to pandas.DataFrame
class CSVLoader:
	def __init__(self, fd):
		self.fd = fd
		
	def _protect_available_memory(self):
		# caculate mem that need to be protect for more stable environment
		total_memory = int(ps.virtual_memory().total * 0.05)
		data_size = os.path.getsize(self.fd)
		if  data_size > total_memory:
			#print("large")
			#protect_range = int(ps.virtual_memory().available * 0.05)
			protect_range = int(self._get_sys_available_memory() * 0.05)
			return protect_range
		else:
			#print("small")
			#protect_range = int(ps.virtual_memory().available * 0.1)
			protect_range = int(self._get_sys_available_memory() * 0.1)
			return protect_range
	
	def _get_sys_available_memory(self):
		return ps.virtual_memory().available
	
	def _get_file_size(self):
		return os.path.getsize(self.fd)
	
	def _dynamic_allocate(self):
		# workflow: check ckpt -> open file -> store records -> looping until finished
		# check ckpt
		file_size = self._get_file_size()
		ava_mem = self._protect_available_memory()
		if os.path.exists("./tmp/file_ckpt.txt") == True:
			# has records
			last_point = file_operation(self.fd)._file_load_pointer()
			if last_point < file_size:
				left_data_size = file_size - last_point
				if left_data_size < ava_mem:
					return dataframe_converter(self.fd, data_size = left_data_size, pos = last_point, rec = True)
				else:
					return dataframe_converter(self.fd, data_size = ava_mem, pos = last_point, rec = True)
				
		else:
			# first time
			if file_size < ava_mem:
				return dataframe_converter(self.fd, data_size = file_size, rec = False)._read()
			else:
				file_operation(self.fd, data_size = ava_mem)._file_store_pointer()
				return dataframe_converter(self.fd, data_size = ava_mem, rec = False)._read()

# rename numpy_converter to dataframe_converter
class dataframe_converter:
	def __init__(self, 
				 fd, 
				 data_size,
				 pos = None,
				 rec = False):
		self.fd = fd
		self.data_size = data_size
		self.pos = pos
		self.rec = rec
	
	def _read(self):
		# if rec = 0: hasn't record
		# if rec = 1: has record 
		if self.rec:
			with open(self.fd, "r") as df:
				# read label
				d_label = df.readline()
				d_label = d_label.strip().split(",")
				df.seek(self.pos, 0)
				reader = df.readlines(self.data_size)
				# not the first time, don't need to skip first row
				Lines = [line.strip().split(",") for line in reader[:]]
				# transfer data to dataframe
				data = pd.DataFrame(columns = d_label, data = Lines)
				del reader
				#data = np.array(Lines)
				del Lines
				return data
		else:
			with open(self.fd, "r") as df:
				# read label
				d_label = df.readline()
				d_label = d_label.strip().split(",")
				df.seek(0)
				reader = df.readlines(self.data_size)
				# first time need to skip first row
				Lines = [line.strip().split(",") for line in reader[1:]]
				data = pd.DataFrame(columns = d_label, data = Lines)
				del reader
				#data = np.array(Lines)
				del Lines
				return data
# write ckpt for data read
class file_operation:
	def __init__(self,
				fd, 
				data_size = None):
		self.fd = fd
		self.data_size = data_size
	
	def _file_store_pointer(self):
		# read file and build each length in list
		with open(self.fd, "rb") as csv_file:
			row_size = SizedReader(csv_file)
			reader = csv.reader(row_size)
			for row in reader:
				pos = row_size.size
				if pos > self.data_size:
					with open("./tmp/file_ckpt.txt", "w") as wf:
						wf.write(str(pos))
						break
	
	def _file_load_pointer(self):
		# load last position about csv file
		with open("./tmp/file_ckpt.txt", "r") as df:
			reader = df.read()
			last_pos = int(reader)
			return last_pos

# construct data array by line to line
class SizedReader:
    def __init__(self, fd, encoding='utf-8'):
        self.fd = fd
        self.size = 0
        self.encoding = encoding   # specify encoding in constructor
    def __next__(self):
        line = next(self.fd)
        self.size += len(line)
        return line.decode(self.encoding)   # returns a decoded line
    def __iter__(self):
        return self



