import os, shutil, base64
import datetime
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
import glob
'''
import keras
from keras.callbacks import ModelCheckpoint
'''
# checkpoint locate and select newest
# tensorflow
def training_ckpt():
	# try to get training path
	t_epochs = "./tmp/t_epochs.txt"
	t_path = "./tmp/training_path.txt"
	if os.path.exists(t_epochs) and os.path.exists(t_path):
		# get remains
		with open(t_epochs, "r") as df:
			t = df.read().split("\n")
			t = int(t[1])
			with open(t_path, "r") as df:
				path = df.read().strip()
			if t != 0:
				training_path = path
			else:
				if path == "./ckpt/training_A":
					print("Checkpoint: training_B is Selected.")
					training_path = "./ckpt/training_B"
				else:
					print("Checkpoint: training_A is Selected.")
					training_path = "./ckpt/training_A"
	elif os.path.exists(t_path) == True and os.path.exists(t_epochs) == False:
		# first time
		with open(t_path, "r") as df:
			training_path = df.read().split("\n")
	# write path to 
	# tf version modelcheckpoint
	return ModelCheckpoint(filepath = training_path,
						monitor="val_accuracy",
						verbose = 1,
						period = 1)
def tf_modelCkpt():
	# list path
	path_a = "./ckpt/training_A"
	path_b = "./ckpt/training_B"
	if os.path.exists(path_a) and os.path.exists(path_b):
		# get time on each file
		print("checkpoints selected")
		# select old one
		if os.path.getatime(path_a) > os.path.getatime(path_b):
			checkpoint_path = "./ckpt/training_B/checkpoints-weights.{epoch:02d}-{val_loss:.6f}.hdf5"		
		else:
			checkpoint_path = "./ckpt/training_A/checkpoints-weights.{epoch:02d}-{val_loss:.6f}.hdf5"
	else:
		print("ERROR:checkpoint path error!")
		with open("./tmp/check_path.txt", "w") as df:
			df.write("ERROR:checkpoint path error!")
	print(checkpoint_path)
	return ModelCheckpoint(filepath = checkpoint_path,
						verbose = 1,
						period = 1)

def checkLog():
	if os.path.exists("logs.txt") == True:
		os.remove("logs.txt")
	logs = os.listdir("./tmp/")
	for ele in logs:
		with open("./tmp/" + ele, "r") as df:
			og = df.read()
			with open("logs.txt", "a+") as wf:
				wf.write(og)
	for ele in logs:
		os.remove("./tmp/" + ele)
	# clean checkpoints when training done it work
	var1 = "ckpt/training_A"
	var2 = "ckpt/training_B"
	if os.path.getatime(var1) > os.path.getatime(var2):
		files = glob.glob(var2 + "/*")
		try:
			newest_file = max(files, key=os.path.getctime)
			os.replace(newest_file, "./output_model.hdf5")
			for ele in files:
				os.remove(ele)
		except:
			print("Checkpoint is empty!")
	else:
		try:
			files = glob.glob(var1 + "/*")
			newest_file = max(files, key=os.path.getctime)
			os.replace(newest_file, "./output_model.hdf5")
			for ele in files:
				os.remove(ele)
		except:
			print("Checkpoint is empty!")
	print("Done and Clean old files!")


