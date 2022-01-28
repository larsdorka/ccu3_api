import sys
import os
import contextlib
import time
import threading
import json

import uvicorn

import asgi_api
import ccu3_connector

config_data = {}


class BackgroundServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        pass
        return

    @contextlib.contextmanager
    def run_in_thread(self) -> None:
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
        return


if __name__ == '__main__':
    logpath = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logfilepath = os.path.join(logpath, "stdout.log")
    file_stdout = open(logfilepath, "a")
    print("")
    print("application started")
    print("redirecting output to {}".format(logfilepath))
    sys.stdout = file_stdout
    sys.stderr = file_stdout

    try:
        with open("config/config.json") as file:
            config_data = json.load(file)
    except Exception as ex:
        print("error on reading config file: " + str(ex))
        file_stdout.close()
        sys.exit()

    ccu3_connector.initialize(config_data['ccu3_config'])

    print("starting...")
    uvi_config = uvicorn.Config(asgi_api.api, port=config_data['server_config']['port'], host=config_data['server_config']['host'], forwarded_allow_ips="*")
    uvi_server = BackgroundServer(config=uvi_config)
    with uvi_server.run_in_thread():
        time.sleep(1)
        print("started")
        try:
            x = input("press any key")
        except KeyboardInterrupt:
            pass
        print("stopping...")
    print("stopped")

    file_stdout.close()
