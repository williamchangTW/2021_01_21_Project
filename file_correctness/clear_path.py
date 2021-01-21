import os, shutil

def clearPATH():
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
