import sys, subprocess, os, time
import signal
import threading
import build_train
from csv_loader import dynamic_memory, numpy_converter, dy_checkpoint, csv_loader
from file_correctness import correct_model, correct_data, clear_path, correctness
from checkpoint import ckpt, ckpt_create
from recover_system_status import rss_initial, rss
from environment_detector import envir_daemon, start_daemon, env_initial
# description: for control all procedure, user only run this file in terminal
# don't need additional steps 
# target: 
# 1. combine modle.py file and framework.py
# 2. start daemon process in background or check daemon process is active for sure
# 3. start running trainnig task and give monitor opertunity to daemon process
# 4. done

if __name__ == "__main__":
    # check package version
    try:
        env_initial.environment_check()
        print("Package version check done.")
    except:
        print("Error happened when package check")
    # check file paths
    try:
        env_initial.path_check()
        print("Workspace check done.")
    except IOError:
        raise RuntimeError("Error happened when path check") from None
    #TODO: restart check
    if os.path.exists("restart.txt") == False:
        with open("restart.txt", "w") as wf:
            wf.write("process start")	
    if os.path.exists("flag.txt"):
        with open("flag.txt", "r") as df:
            ckpt = df.read()
        if ckpt == "training_A" and len(os.listdir("ckpt/training_A/")) == 0:
            os.remove("flag.txt")
        elif ckpt == "training_B" and len(os.listdir("ckpt/training_B/")) == 0:
            os.remove("flag.txt")
    if os.path.exists("pid.txt") == True:
        try:
            with open("pid.txt", "r") as df:
                pid = df.read()
                pid = pid.strip().split(" ")
                pid = pid[1]
                os.kill(pid, signal.SIGTERM)
                df.close()
        except:
            os.remove("pid.txt")
    pid = os.getpid()
    with open("pid.txt", "w") as wf:
        wf.write("mainPID: " + str(pid) + "\n")
        wf.close()
    '''
    data_path = "data/"
    model_path = "model/"
    cor_path = "cor/"
    '''
    correctness.clearPATH()
    correctness.correct_data()
    correctness.correct_model()
    if os.path.exists("flag.txt") == True:
        # print("checkpoint exist")
        sys.stdout.write("checkpoint exist\n")
        recovery_check.check_data()
        recovery_check.check_model()
        recovery_check._find_epochs()
    else:
        # print("first time")
        sys.stdout.write("first time\n")
        correctness.dataDebug()
        checkpoint_debug.modelDebug()
    build_train.build()
    path = os.getcwd()
    os.system("python3 " + path + "/model.py")
    #checkpoint.checkLog()
    #print("Done")
    #os.remove("restart.txt")
    sys.stdout.write("Done\n")
