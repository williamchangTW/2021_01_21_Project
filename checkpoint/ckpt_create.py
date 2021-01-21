# make a single checkpoint file
import os
def make_ckpt():
    log_path = "tmp/"
    store_path = "records/checkpoint.txt"
    with open(store_path, "w") as wf:
        if os.path.exists(log_path + "csv_back_path.txt"):
            with open(log_path + "csv_back_path.txt", "r") as df:
                csv_path = df.read().strip()
            wf.write(csv_path + "\n")
            if os.path.exists(log_path + "model_back_path.txt"):
                with open(log_path + "model_back_path.txt") as df:
                    model_path = df.read().strip()
                wf.write(model_path + "\n")
                if os.path.exists(log_path + "file_pointer.txt"):
                    with open(log_path + "model_back_path.txt") as df:
                        file_point = df.read().strip()
                    if os.path.exists(log_path + "file_pointer.txt"):
                        with open(log_path + "ckpt_path.txt") as df:
                            ckpt_path = df.read().strip()
                        if os.path.exists(log_path + "file_pointer.txt"):
                            with open(log_path + "epochs.txt") as df:
                                epochs = df.read().strip()
                        else:
                            wf.write("empty\n")
                    else:
                        for i in range(0, 2):
                            wf.write("empty\n")
                else:
                    for i in range(0, 3):
                        wf.write("empty\n")
            else:
                for i in range(0, 4):
                    wf.write("empty\n")
        else:
            for i in range(0, 5):
                wf.write("empty\n")
