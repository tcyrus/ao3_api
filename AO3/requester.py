import threading
import time
from typing import Optional

import requests


class Requester:
    """Requester object"""
    
    def __init__(
        self,
        rqtw: Optional[int] = -1,
        timew: Optional[int] = 60
    ):
        """Limits the request rate to prevent HTTP 429 (rate limiting) responses.
        12 request per minute seems to be the limit.

        Args:
            rqtw: Maximum requests per time window (-1 -> no limit). Defaults to -1.
            timew: Time window (seconds). Defaults to 60.
        """
        
        if rqtw is None:
            rqtw = -1

        if timew is None:
            timew = 60

        self._requests = []
        self._rqtw = rqtw
        self._timew = timew
        self._lock = threading.Lock()
        self.total = 0

    @property
    def rqtw(self) -> int:
        return self._rqtw

    @rqtw.setter
    def rqtw(self, value: int) -> None:
        self._rqtw = value

    def setRQTW(self, value: int) -> None:
        self.rqtw = value

    @property
    def timew(self) -> int:
        return self._timew

    @rqtw.setter
    def timew(self, value: int) -> None:
        self._timew = value

    def setTimeW(self, value: int) -> None:
        self.timew = value

    def request(self, *args, **kwargs):
        """Requests a web page once enough time has passed since the last request
        
        Args:
            session(requests.Session, optional): Session object to request with

        Returns:
            requests.Response: Response object
        """

        # We've made a bunch of requests, time to rate limit?
        if self._rqtw != -1:
            with self._lock:
                if len(self._requests) >= self._rqtw:
                    t = time.time()
                    # Reduce list to only requests made within the current time window
                    while len(self._requests):
                        if t-self._requests[0] >= self._timew:
                            self._requests.pop(0) # Older than window, forget about it
                        else:
                            break # Inside window, the rest of them must be too
                    # Have we used up all available requests within our window?
                    if len(self._requests) >= self._rqtw: # Yes
                        # Wait until the oldest request exits the window, giving us a slot for the new one
                        time.sleep(self._requests[0] + self._timew - t)
                        # Now outside window, drop it
                        self._requests.pop(0)
                        
                if self._rqtw != -1:
                    self._requests.append(time.time())
                self.total += 1

        if "session" in kwargs:
            sess = kwargs["session"]
            del kwargs["session"]
            req = sess.request(*args, **kwargs)
        else:
            req = requests.request(*args, **kwargs)

        return req

requester = Requester()
