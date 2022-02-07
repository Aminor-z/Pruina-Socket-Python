class ConnectionReachMaxRetryTimesException(Exception):
    def __init__(self, retry_times):
        self.retry_times = retry_times

    def __str__(self):
        return f"Connection reach the max retry times[limit={self.retry_times}]"
