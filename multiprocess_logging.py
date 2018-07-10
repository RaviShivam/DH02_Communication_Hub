from multiprocessing import Queue
from logbook.queues import MultiProcessingHandler

queue = Queue(-1)
handler = MultiProcessingHandler(queue)