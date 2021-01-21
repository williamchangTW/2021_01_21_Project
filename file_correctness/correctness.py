import os
import shutil
import sys
import time
# import correctness_check
# list file path and do correctness check
# move uncorrect file to TEMP
# searching DATA File
# checkDATA renew
# read file that content "DONE"

def shuffle_split(infilename, outfilename1, outfilename2):
	import time
	from random import shuffle
	flag = False
	while flag == False:
		while os.path.exists(infilename) == True:
			with open(infilename, 'r') as df:
				lines = df.readlines()	
			# append a newline in case the last line didn't end with one
			lines[-1] = lines[-1].rstrip('\n') + '\n'
			traingdata = len(lines)* 75 // 100
			print(traingdata)
			testdata = len(lines)- traingdata - 1
			print(testdata)
			with open(outfilename1, 'w') as wf1:
				wf1.writelines(lines[0:traingdata])
			with open(outfilename2, 'w') as wf2:
				wf2.writelines(lines[traingdata:])
			flag = True
			break
		time.sleep(3)


def correct_data():
	# get newest data
	# if here is more than 1 file
	data_path = "./data/"
	cor_path = "cor/"
	if len(os.listdir(data_path)) == 0:
		print("data path is empty!\n")
		sys.exit(1)
	
	if len(os.listdir(data_path)) > 1:
		print("has too many files, system will select newest one\n")
	
	data_list = os.listdir(data_path)
	cor_dict = {}
	o_t = 0
	for i in range(0, len(data_list)):
		if data_list[i] == "cor":
			pass
		else:
			try:
				data_form = data_list[i].split(".")
				print("data formate is " + data_form[1] + "\n")
			except:
				pass
			if data_form[1] != "csv":
				print("Data formate is wrong!\n")
				sys.exit(1)
			else:
				# keep newest one
				with open(data_path + data_list[i], "r") as df:
					firstline = len(df.readline().split(","))
					secondline = len(df.readline().split(","))
					if secondline > firstline:
						print("{}data formate uncorrect!\n".format(data_list[i]))
					else:
						if o_t == 0:
							t = os.path.getctime(data_path + data_list[i])
							if o_t < t:
								newest = data_list[i]
								print(newest)
							else:
								pass
						else:
							o_t = os.path.getctime(data_path + data_list[i])
						# adding to dict
						cor_dict[elements] = os.path.getctime(data_path + data_list[i])
						#shutil.copyfile(data_path + data_list[elements], data_path + cor_path + data_list[elements])
	
	# check if there has no correct file
	if bool(cor_dict) == False:
		print("There is no correct file!\n")
		return IOError
		sys.exit(1)
	'''
	# sorting dict by value
	sort_cor_dict = OrderedDict(sorted(cor_dict.items(), key = lambda x:x[1]))
	'''
	# Select newest one and open it
	shutil.move(data_path + newest, data_path + cor_path + "data.csv")
	# random shuffle data to train and test
	shuffle_split(data_path + cor_path + "data.csv", data_path + cor_path + "train.csv", data_path + cor_path + "test.csv")
# correct data section end
# correct model section start
# import correctness_check
# list file path and do correctness check
# move uncorrect file to TEMP
# read file that content "DONE"
# mantain COR filepath only exist 2 correct data file
# check model file structure
# add checkpoint to model file
# mantian COR filepaht only exist 1 correct model file
def correct_model():
	model_path = "./model/"
	cor_path = "cor/"
	# check file path
	if len(os.listdir(model_path)) == 0:
		print("model path is empty!\n")
		sys.exit(0)
	if len(os.listdir(model_path)) > 1:
		print("has too many files, system will select newest one\n")
	
	model_list = os.listdir(model_path)
	cor_dict = {}
	o_t = 0
	# if path file more than 1 then just read newest
	# list all model file
	for i in range(0, len(model_list)):
		if model_list[i] == "cor":
			pass
		else:
			try:
				model_form = model_list[i].split(".")
				print("Model formate is " + model_form[1] + "\n")
			except:
				pass
			if model_form[1] != "csv":
				print("Model formate is wrong!\n")
				sys.exit(1)
			else:
				df = open(model_path + model_list[i], "rt")
				pos1 = df.read().find("model.fit(")
				df.seek(0)
				pos2 = df.read().find("train")
				df.seek(0)
				pos3 = df.read().find("test")
				# keyword can not found
				if pos1 == -1 or pos2 == -1 or pos3 == -1:
					print("model file doesnt follow the rules to write\n")
				# move all model file to cor
				else:
					if o_t == 0:
						t = os.path.getctime(model_path + model_list[i])
						if o_t < t:
							newest = model_list[i]
						else:
							pass
					else:
						o_t = os.path.getctime(model_path + model_list[i])
					cor_dict[model_list[i]] = os.path.getctime(model_path + model_list[i])
	# check if there has no correct file
	if bool(cor_dict) == False:
		print("There is no correct file!\n")
		return IOError
		sys.exit(1)
	shutil.move(model_path + newest, model_path + cor_path + "model.py")
	# keep a newest one
	# add checkpoint to file
	# write to corrct file
	with open(model_path + cor_path + "model.py", "rt") as wf:
		pos = wf.read().find("model.fit(")
		wf.seek(pos + 10)
		ch = wf.read().find("callbacks")
		if ch != -1:
			pos = pos + ch
			wf.seek(pos)
			ch_leftbracket = wf.read().find("[")
			wf.seek(pos + ch_leftbracket)
			ch_rightbracket = wf.read().find("]")
			length = ch_rightbracket
			wf.seek(pos + ch_leftbracket + 1)
			rep = wf.read(length - 1)
			wf.seek(0)
			data = wf.read().replace(rep, "checkpoint.modelCkpt()")
			fout = open(model_path + cor_path + "model.py", "wt")
			fout.write(data)
			fout.close()
		else:
			cor_flag = False
			while cor_flag == False:
				wf.seek(pos)
				left_bracket = wf.read().find("(")
				wf.seek(pos)
				terminator = wf.read().find("\n")
				if terminator < left_bracket:
						wf.seek(pos)
						right_bracket = wf.read().find(")")
						if right_bracket < terminator:
							pos = pos + right_bracket - 2
							wf.seek(0)
							data = wf.read()
							with open(model_path + cor_path + "model.py", "wt") as fout:
								fout.write(data)
								fout.seek(0)
								fout.seek(pos)
								fout.write(", callbacks=[ckpt.training_ckpt()])")
								fout.close()
							cor_flag = True
				elif left_bracket == -1:
					wf.seek(pos)
					right_bracket = wf.read().find(")")
					pos = pos + right_bracket - 2
					wf.seek(0)
					data = wf.read()
					with open(model_path + cor_path + "model.py", "wt") as fout:
						fout.write(data)
						fout.seek(0)
						fout.seek(pos)
						fout.write(", callbacks=[ckpt.training_ckpt()])")
						fout.close()
					cor_flag = True
				else:
					pos = pos + terminator + 2	

# correct model section end
def clear_path():
	data_path = "./data/"
	cor_path = "cor/"
	model_path = "./model/"
	if os.path.exists(data_path + "__pycache__") == True:
		shutil.rmtree(data_path + "__pycache__")
	if os.path.exists(data_path + cor_path + "__pycache__") == True:
		shutil.rmtree(data_path + cor_path +"__pycache__")
	if os.path.exists(model_path + "__pycache__") == True:
		shutil.rmtree(model_path + "__pycache__")
	if os.path.exists(model_path + cor_path + "__pycache__") == True:
		shutil.rmtree(model_path + cor_path +"__pycache__")
	if os.path.exists(data_path + cor_path + "train.csv") == True:
		os.remove(data_path + cor_path + "train.csv")
	if os.path.exists(data_path + cor_path + "test.csv") == True:
		os.remove(data_path + cor_path + "test.csv")

# testing functiomnality
if __name__ == "__main__":
	# correct every input file
	correct_data()
	correct_model()