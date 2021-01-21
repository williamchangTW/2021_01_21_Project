# target:
# 1. daemon registration
# 2. daemon execution
# 3. chekc data
# 4. check model
# 5. change epoch

import os
import glob
import sys
import subprocess
import filecmp
import threading


# produce a semaphore key
key = threading.Semaphore(value = 1)

# call daemon to work in background
class start_daemon:
    def __init__(self):
        path = os.getcwd()
        subprocess.Popen(args=["gnome-terminal", "--command=python3 " + path + "./environment_detector/envir_daemon.py"], shell=False)

# find epoch position and return its value
class find_epoch:
    def __init__(self, 
                 path):
        self.path = path
    def get_epochs(self):
        with open(self.path, "r") as df:
	        # checkpoint compare epochs
            pos_begin = df.read().find("epochs")
            if pos_begin != -1:
                # <<epoch search section>>
                # scan next char
                loc = pos_begin + 5
                df.seek(loc)
                pos_eq = df.read().find("=")
                # scan next char
                loc_eq = pos_begin
                df.seek(loc_eq)
                pos_end = df.read().find(",")
                # <<epoch search section>>
                # <<model fit search section>>
                df.seek(0)
                pos_fit = df.read().find("model.fit")
                # scan next char
                df.seek(loc + pos_eq + 1)
                tar = df.readline().split(",")
                # <<model fit search section>>
                # <<validation search section>>
                # scan validation
                df.seek(0)
                val_loc = df.read().find("validation_split")
                df.seek(val_loc + 16)
                temp_eq = df.read().find("=")
                df.seek(val_loc + 16 + temp_eq + 1)
                tar = df.readline().split(",")
                pos_val = tar[0]
                # <<validatino search section>>
                # returm position in a file
                # pos_begin: epochs begin point
                # pos_end: epochs end point
                # pos_fit: model fit point
                # pos_val: validation point
                return pos_begin, pos_end, pos_fit, pos_val
            else:
                print("file is not correct!")
                return IOError 


# recover system status
class recovery_check:
    def __init__(self,
                 fd = None):
        self.fd = fd
    
    def _check(self):
        # col0: data seek pointer
        # col1: data path
        # col2: model path
        # col3: training ckpt path
        # col4: training epochs
        # col5: training last epochs
        df = open(self.fd, "r")
        data_path = df.readline().strip()
        if data_path != "empty":
                self._check_data(path = data_path)
        else:
                print("File corrupt. No records!")
                return IOError		
        model_path = df.readline().strip()
        if model_path != "empty":
                self._check_model(path = model_path)
        else:
                print("File corrupt. No records!")
                return IOError
        file_pointer = df.readline().strip()
        if file_pointer != "empty":
                with open("./tmp/file_pointer.txt", "w") as wf:
                        wf.write(file_pointer)
        else:
                print("File corrupt. No records!")
                return IOError
        ckpt_path = df.readline().strip()
        if file_pointer != "empty":
                with open("./tmp/ckpt_path.txt", "w") as wf:
                        wf.write(ckpt_path)
        else:
                print("File corrupt. No records!")
                return IOError
        epochs = df.readline().strip()
        if epochs != "empty":
                print("left: " + str(epochs) + "training epochs")
        else:
                print("File corrupt. No records!")
                return IOError
    
    def _check_data(self, path):
        # data procedure path
        if os.path.exists(path) and filecmp.cmp("./data/cor/data.csv", path):
                print("(Data)Files are same!")
        else:
                print("(Data)Files are different!")
                return IOError

    def _check_model(self, path):
        # model ckpt path
        if os.path.exists(path) and filecmp.cmp("./model/cor/model.py", path):
                print("(Model)Files are same!")
        else:
                print("(Model)Files are different!")
                return IOError

    def _change_epochs(self, path, epochs):
	# change epochs
        pos1, pos2, pos3, pos4 = find_epoch(path).get_epochs()
        with open(path, "r+") as df:
            forehead = df.read(pos3)
            df.seek(0)
            df.seek(pos1 + pos2)
            button = df.read()
            with open(path, "w+") as wf:
                wf.write(forehead + 
                        "model.load_weights('" +
                        epochs + 
                        "')\n" +
                        "model.fit(train, test, validation_split=" +
                        str(pos3) + 
                        ",epochs=" + 
                        str(pos4) +
                        button)
        

# starting recovery training task
# steps:
# 1. loading process of file operation
# 2. loading model training result and keep training until finish
def recovert_system_status():
    # call ckpt to run tarining task
    subprocess.call([sys.executable, "model.py"])

if __name__ == "__main__":
	recovery_check("records/checkpoint_1.txt")._check()
