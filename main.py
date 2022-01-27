import sys
import os
import contextlib
import time
import threading

import uvicorn

import asgi_api
import ccu3_connector


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

    ccu3_connector.load_config()

    print("starting...")
    uvi_config = uvicorn.Config(asgi_api.api, port=8000, host="0.0.0.0")
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
