import  time

class FridayState:
    def __init__(self):
        self.active = False
        self.last_active = time.time()
        self.first_start = True
        self.standby = False
        self.TIMEOUT = 100
        self.auto_standby = True  # default ON hai

    def wake(self):
        self.active = True
        self.standby = False
        self.last_active = time.time()

    def touch(self):
        self.last_active = time.time()

    def is_timed_out(self):
        return time.time() - self.last_active > self.TIMEOUT

    def go_standby(self):
        self.active = False
        self.standby = True
