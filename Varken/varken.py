import schedule
import threading
import functools
from time import sleep

from Varken.iniparser import INIParser
from Varken.sonarr import SonarrAPI

def logging(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print('LOG: Running job "%s"' % function.__name__)
        result = function(*args, **kwargs)
        print('LOG: Job "%s" completed' % function.__name__)
        return result

    return wrapper

@logging
def threaded(job):
    thread = threading.Thread(target=job)
    thread.start()

if __name__ == "__main__":
    CONFIG = INIParser()

    if CONFIG.sonarr_enabled:
        SONARR = SonarrAPI(CONFIG.sonarr_servers, CONFIG.influx_server)
        for server in CONFIG.sonarr_servers:
            if server.queue:
                schedule.every().minute.do(threaded, SONARR.get_queue)

    while True:
        schedule.run_pending()
        sleep(1)

