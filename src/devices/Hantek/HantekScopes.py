from devices.Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope

from threading import Thread, RLock
from queue import Queue
import sys
import numpy as np
import time

data = []
data_lock = RLock()
queue:Queue = Queue()
num_worker_threads = 6

class Hantek6022Scope(object):

    def __init__(self):
        
        #define params for hantek oscilloscope

        self.voltage_range = 1       # 1 (5V), 2 (2.6V), 5 or 10
        self.sample_rate_index = 8         # sample rate in MHz or in 10khz
        self.sample_rate = self.sample_rate_index * 1000 * 10
        self.numchannels = 1
        self.numseconds = 0          # number of seconds to sample (use 0 for infinity)
        self.blocksize = 100*6*1024      # should be divisible by 6*1024
        self.alternative = 1         # choose ISO 3072 bytes per 125 us


        self.scope = Oscilloscope()
        self.scope.setup()
        self.scope.open_handle()
        if (not self.scope.is_device_firmware_present):
             self.scope.flash_firmware()
        else:
            self.scope.supports_single_channel = True
       
        #scope.set_interface(alternative)
        #print("ISO" if scope.is_iso else "BULK", "packet size:", scope.packetsize)
        self.scope.set_num_channels(self.numchannels)
        # set voltage range
        self.scope.set_ch1_voltage_range(self.voltage_range)
        # set sample rate
        self.scope.set_sample_rate(self.sample_rate_index)

        self.scope.setup()
        if not self.scope.open_handle():
            sys.exit( -1 )

    def readCapturedData(self):
        start_time = time.time()
        print("Clearing FIFO and starting data transfer...")
        self.scope.start_capture()
        shutdown_event = self.scope.read_async(self.recv_callback, self.blocksize, outstanding_transfers=10)
        real_duration = 0
        while True:
            real_duration = time.time() - start_time
            print("real_duration:",real_duration)
            if self.numseconds > 0 and real_duration >= self.numseconds:
                break
            self.scope.poll()
 
    def recv_callback(self, ch1_data, _):
	# Note: This function has to be kept as simple and fast as possible
	#       to prevent loss of measurements. Only copy data here. All other
	#       processing is done in worker threads afterwards.
	#print("ch1_data:", ch1_data)
	#print("min:{} max:{}".format(min(ch1_data), max(ch1_data)))
        print("queue.put():",len(data))
        data_lock.acquire()
        try:
            queue.put(len(self.data))
            data.append({'raw':ch1_data})
        finally:
            data_lock.release()
    
    def startCapture(self):
        t = Thread(target=self.readCapturedData)
        #t.setDaemon(True)
        t.start()



class DataWorkerThread(Thread):
    
    def __init__(self, myScopeObj: Hantek6022Scope):
        super().__init__()
        self.scope = myScopeObj
        for i in range(num_worker_threads):
            self.worker = Thread(target=self.process_data, args=(i, queue,))
            self.worker.setDaemon(True)
            self.worker.start()

    def process_data(self, worker_id, queue: Queue):
        while True:
            i = queue.get()

            data_lock.acquire()
            try:
                print("i:",i," data len:",len(data))
                if i >= len(data):
                    continue
                block = data[i]
            finally:
                data_lock.release()

            # Min, max is much faster with numpy array than with python list
            block['raw_np'] = np.array(block['raw'])
            block_min = block['raw_np'].min()
            block_max = block['raw_np'].max()
            [block_min, block_max] = self.scope.scale_read_data([block_min, block_max], self.scope.voltage_range) # map raw to voltage
            block['min'] = block_min
            block['max'] = block_max
            print("process_data() worker#{} block#{} min:{} max:{}".format(worker_id, i, block_min, block_max))
            queue.task_done()


