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
    from random import shuffle

    with open(infilename, 'r') as f:
        lines = f.readlines()

    # append a newline in case the last line didn't end with one
    lines[-1] = lines[-1].rstrip('\n') + '\n'
    traingdata = len(lines)* 75 // 100
    print(traingdata)
    testdata = len(lines)- traingdata - 1
    print(testdata)
    with open(outfilename1, 'w') as f:
        f.writelines(lines[0:traingdata])
    with open(outfilename2, 'w') as f:
        f.write(lines[0])
        f.writelines(lines[traingdata:])

def correct_data():
	data_path = "./data/"
	cor_path = data_path + "cor/"
	if len(os.listdir(data_path)) == 0:
		print("data path is empty!\n")
		sys.exit(0)
	data_list = os.listdir(data_path)
	for elements in range(len(data_list)):
		if data_list[elements] == "cor":
			pass
		else:
			with open(data_path + data_list[elements], "r") as df:
				firstline = len(df.readline().split(","))
				secondline = len(df.readline().split(","))
				if secondline > firstline:
					print("data formate uncorrect!\n")
					sys.exit(0)
				else:
					try:
						shutil.copyfile(data_path + data_list[elements], cor_path + data_list[elements])
					except:
						pass
	
	# bubble sort
	data_list = os.listdir(cor_path)
	# COR filepath only exist 2 correct data file
	if len(data_list) > 1:
		for elements in range(len(data_list) - 1):
			var1 = cor_path + data_list[elements]
			var2 = cor_path + data_list[elements + 1]
			if os.path.exists(var1) and os.path.exists(var2) == True:
				time1 = os.path.getctime(var1) // 1000
				time2 = os.path.getctime(var2) // 1000
				if time1 > time2:
					os.remove(var2)
					shutil.move(var1, cor_path + "data.csv")
				else:
					os.remove(var1)
					shutil.move(var2, cor_path + "data.csv")
	
	data_list = os.listdir(cor_path)
	os.popen("mv " + cor_path + data_list[0] + " " + cor_path + "data.csv")
	shuffle_split(cor_path + "data.csv", cor_path + "train.csv", cor_path + "test.csv")
