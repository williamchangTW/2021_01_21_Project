import sys, subprocess, os
#import platform components
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Reshape, Conv2D, AveragePooling2D, Flatten
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.optimizers import Adam
from csv_loader import dy_checkpoint, csv_loader
from file_correctness import correct_model, correct_data, clear_path, correctness
from checkpoint import ckpt, ckpt_create
from recover_system_status import rss_initial, rss
from environment_detector import envir_daemon, start_daemon, env_initial

#data preprocessing part 
def datapreprocess(data_train, x_test):
    n_samples_test = x_test.shape[0]
    y_train = np.array(data_train[:, 0])
    x_train = np.array(data_train[:, 1:])
    y_train = keras.utils.to_categorical(y_train, num_classes = 10)
    return x_train, y_train

# make sure process is not duplicate
pid = os.getpid()
with open("train_pid.txt", "w") as wf:
	wf.write("tradinPID: " + str(pid) + "\n")
	wf.close()
# recieve user input and run file correctness check
# start to read user input
# dynamic loader
train = csv_loader("./data/cor/train.csv")._dynamic_allocate()
test = csv_loader("./data/cor/test.csv")._dynamic_allocate()
train, test = datapreprocess(train, test)
killer = envir_daemon.GracefulKiller()
# model part
