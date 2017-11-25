class command_handler:
    def __init__(self, pod_state=0):
        self.pod_state = pod_state

    def start_pod(self):
        self.pod_state = 2
        print("Starting the pod")

    def brake_pod(self):
        self.pod_state = 2
        print("Braking the pod")

    def perform_system_check(self):
        self.pod_state = 3
        print("Performing system check")
