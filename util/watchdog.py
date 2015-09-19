# Basic watchdog timer that just sets a flag that should be checked
from threading import Timer,Event


class WatchDog(object):

    @staticmethod
    def Callback(event):
        import logging
        logging.info("callback")
        event.set()

    def __init__(self):
        self.watchdog_timeout_seconds = 60.0 * 10 # 10 minutes
        self._event = Event()
        self._event.clear()
        self.timer = None

    def IsExpired(self):
        return self._event.is_set()

    def Start(self):
        self.timer = Timer(self.watchdog_timeout_seconds, WatchDog.Callback, [self._event])
        self.timer.start()

    def Stop(self):
        self._event.clear()
        if self.timer:
            self.timer.cancel()
        self.timer = None

    def Reset(self):
        self.Stop()
        self.Start()
