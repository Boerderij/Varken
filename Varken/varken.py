import schedule
import threading
from time import sleep

from Varken.iniparser import INIParser
from Varken.sonarr import SonarrAPI


def threaded(job, days=None):
    thread = threading.Thread(target=job, args=([days]))
    thread.start()


if __name__ == "__main__":
    CONFIG = INIParser()

    if CONFIG.sonarr_enabled:
        SONARR = SonarrAPI(CONFIG.sonarr_servers, CONFIG.influx_server)

        for server in CONFIG.sonarr_servers:
            if server.queue:
                schedule.every(server.queue_run_seconds).seconds.do(threaded, SONARR.get_queue)
            if server.missing_days > 0:
                schedule.every(server.missing_days_run_seconds).seconds.do(threaded, SONARR.get_missing,
                                                                           server.missing_days)
            if server.future_days > 0:
                schedule.every(server.future_days_run_seconds).seconds.do(threaded, SONARR.get_future,
                                                                          server.future_days)

    while True:
        schedule.run_pending()
        sleep(1)

