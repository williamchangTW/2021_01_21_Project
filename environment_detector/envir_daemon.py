# Automation to check environment
# notice: signal api cannot founded in windows OS
import psutil as ps
import sys, os, time, signal
import ckpt_module as ckpt_module

class system_detect:
	# monitor pid
	# monitor resources: battery, memory, cpu
	# case 0: default setting
	# case 1: graceful killer start and save ckpt
	def __init__(self,
				 pid = None, 
				 limit_mem = 60,
				 limit_bat = 30):
		self.pid = pid
		self.limit_mem = limit_mem
		self.limit_bat = limit_bat

	def _behavior(self):
		# battery code block
		try:
			battery_status = ps.sensors_battery().percent
			power_plug = ps.sensors_battery().power_plugged
		except:
			power_plug = ps.sensors_battery().power_plugged
		# memory code block
		total_mem = ps.virtual_memory().total
		ava_mem = ps.virtual_memory().available
		usage_mem = (ava_mem / total_mem)*100
		# behavior settings
		# memory usage > bound
		if 100 - self.limit_mem >= int(usage_mem):
			print("Memory cae be allocate(%): " + str(usage_mem) + "\n")
			GracefulKiller(pid = self.pid, immed = True)
			return 2
		# with battery
		# battery <= bound 
		# unplug
		# memory close bound
		if 100 - (self.limit_mem - 10) >= int(usage_mem) or (battery_status <= self.limit_bat and power_plug == False):
			print("Memory cae be allocate(%): " + str(usage_mem) + "\n")
			GracefulKiller(pid = self.pid, immed = False)
			return 1
		else:
			return 0

class GracefulKiller:
	def __init__(self, pid = None, immed = False):
		self.pid = pid
		if immed == True:
			self._exit_immediately()
		else:
			self._exit_gracefully()
		# call ckpt to do something
	def _exit_gracefully(self):
		ckpt_module.make_ckpt()
		print("Checkpoint is called!\n")
		print("Resource usage is high!\n")
    
	def _exit_immediately(self):
		os.kill(self.pid, signal.SIGTERM)
		print('Signal handler called with signal')
		raise OSError("System Loading too high! terminated...\n")


if __name__ == "__main__":
	# daemon start
	while True:
		while os.path.exists("./tmp/train_pid.txt"):
			f = open("./tmp/train_pid.txt", "r")
			pid = f.read()
			pid = pid.strip()
			# records
			if ps.pid_exists(int(pid)) == False:
				print(str(time.asctime(time.localtime(time.time()))) + ": Waiting...")
				os.remove("./tmp/train_pid.txt")
				break
			# training
			elif ps.pid_exists(int(pid)) == True:
				print(str(time.asctime(time.localtime(time.time()))) + ": Daemon start monitoring!")
				# record
				with open("./tmp/aemon_log.txt", "w") as wf:
					wf.write(str(time.asctime(time.localtime(time.time()))) + ": monitoring...\n")
				if system_detect(int(pid))._behavior() == 2:
					print(str(time.asctime(time.localtime(time.time()))) + ": Unstable situation!\n")
					with open("./tmp/daemon_log.txt", "a") as wf:
						wf.write(str(time.asctime(time.localtime(time.time()))) + ": Unstable situation!\n")
					break
				elif system_detect(int(pid))._behavior() == 1:
					print(str(time.asctime(time.localtime(time.time()))) + ": System busy!\n")
					with open("./tmp/daemon_log.txt", "a") as wf:
						wf.write(str(time.asctime(time.localtime(time.time()))) + ": System busy!\n")
					break
				elif system_detect(int(pid))._behavior() == 0: 
					print(str(time.asctime(time.localtime(time.time()))) + ": Stable, training task is running...\n")
					with open("./tmp/daemon_log.txt", "a") as wf:
						wf.write(str(time.asctime(time.localtime(time.time()))) + ": Stable, training task is running...\n")
					break

		print(str(time.asctime(time.localtime(time.time()))) + ": monitoring...\n")
		with open("./tmp/daemon_log.txt", "a") as wf:
			wf.write(str(time.asctime(time.localtime(time.time()))) + ": monitoring...\n")
		time.sleep(10)
