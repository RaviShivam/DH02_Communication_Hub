import time
from multiprocessing import Queue
from data_handlers import HANDLE_LOG
from messenger_ch import multi_mission_logger

queue = Queue(-1)
data = multi_mission_logger("test_logger", "test_log", queue, HANDLE_LOG)
data1 = multi_mission_logger("test_logger1", "test_log1", queue, HANDLE_LOG)
data2 = multi_mission_logger("test_logger2", "test_log2", queue, HANDLE_LOG)
data3 = multi_mission_logger("test_logger3", "test_log3", queue, HANDLE_LOG)


while True:
    data.queue.put(list(range(10)))
    data1.queue.put(list(range(10)))
    data2.queue.put(list(range(10)))
    data3.queue.put(list(range(10)))
    time.sleep(0.01)
