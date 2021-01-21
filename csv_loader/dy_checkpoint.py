import csv
import csv_loader
import datetime
def CheckpointWrite(par1 = None, par2 = None, par3 = None, flag = 0):
    # par1 = file pointer
    # par2 = program name
    # par3 = program ID
    temp = hash(datetime.datetime.now().date())
    if flag == 0:
        with open("checkpointsA.txt", "w") as df:
            df.write(str(temp) + "\n")
            df.write(str(par1))
            if par2 != None:
                df.write(str(par2))
            if par3 != None:
                df.write(str(par3))
            df.write(str(temp) + "\n")
    elif flag == 1:
        with open("checkpointsB.txt", "w") as df:
            df.write(str(temp) + "\n")
            df.write(str(par1))
            if par2 != None:
                df.write(str(par2))
            if par3 != None:
                df.write(str(par3))
            df.write(str(temp) + "\n")

def fileStore(file_name, data_size):
	csv_file = open(file_name, "rb")
	rowsize = csv_loader.SizedReader(csv_file)
	reader = csv.reader(rowsize)
	for row in reader:
		pos = rowsize.size
		if pos > data_size:
			with open("./tmp/file_ckpt.txt", "w") as wf:
				wf.write(str(pos))
			break
	csv_file.close()

def fileLoad():
    with open("./tmp/file_ckpt.txt", "r") as df:
        reader = df.read()
        last = int(reader)
        #last = df.seek(int(reader), 0)
        return last
