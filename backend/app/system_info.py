import psutil


class SystemInfo:
    def __init__(self):
        pass

    def get_disk_usage(self):
        disk = psutil.disk_usage("/")
        return {"total": disk.total / (2**30), "used": disk.used / (2**30), "free": disk.free / (2**30)}
