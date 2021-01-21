import sys, subprocess, os, signal
#import platform components
import numpy as np
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Reshape, Conv2D, AveragePooling2D, Flatten
from keras.layers import MaxPooling2D
from keras.optimizers import adam
from DynamicLoader import dynamic_memory, numpy_converter
from FileCorrect import correct_model, correct_data, clear_path
from Checkpoint import checkpoint, checkpoint_debug
from Recovery import recovery_process, recovery_check
from EnvironmentCheck import envir_daemon, wifi_check, bat_check, sys_check, mem_check, start_daemon

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
train = dynamic_memory.dynamicLoad("./DATA/COR/train.csv")
test = dynamic_memory.dynamicLoad("./DATA/COR/test.csv")
train, test = datapreprocess(train, test)
# model part
# test comment
# test comment
#testtemp
'''
test comment
'''
model = Sequential()
model.add(Reshape(target_shape=(1, 28, 28), input_shape=(784,)))
model.add(Conv2D(kernel_size=(3, 3), filters=6, padding="same", data_format="channels_first", kernel_initializer="uniform", use_bias=False))
model.add(MaxPooling2D(pool_size=(2, 2), data_format="channels_first"))
model.add(Conv2D(kernel_size=(5, 5), filters=16, padding="same", data_format="channels_first", kernel_initializer="uniform", use_bias=False))
model.add(MaxPooling2D(pool_size=(2, 2), data_format="channels_first"))
model.add(Conv2D(kernel_size=(5, 5), filters=120, padding="same", data_format="channels_first", kernel_initializer="uniform", use_bias=False))
model.add(Flatten())
model.add(Dense(output_dim=120, activation='relu'))
model.add(Dense(output_dim=120, activation='relu'))
model.add(Dense(output_dim=10, activation='softmax'))

adam = keras.optimizers.Adam(lr=0.0005, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])
model.load_weights('./CHECKPOINTS/training_B/checkpoints-weights.02-0.967273.hdf5')
model.fit(train, test, validation_split=0.33,epochs=7, batch_size=64, callbacks=[checkpoint.modelCkpt()])
