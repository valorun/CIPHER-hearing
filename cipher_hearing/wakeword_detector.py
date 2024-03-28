import subprocess
import json
import errno
import os
from os.path import join

class WakeDetector():
    def __init__(self, spotter_path, wakeword_model_path, threshold, samplerate=16000):
        self.spotter_path = spotter_path
        self.spotter_args = [wakeword_model_path, '-e', '-t', str(threshold)]
        self.start()

    def start(self):
        spotter_command = [self.spotter_path] + self.spotter_args
        self.spotter_proc = subprocess.Popen(
            spotter_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        os.set_blocking(self.spotter_proc.stdout.fileno(), False)

    def stop(self):
        self.spotter_proc.terminate()
        self.spotter_proc.wait()

    def detect(self, data):
        try:
            self.spotter_proc.stdin.write(data)
            #self.spotter_proc.stdin.flush()
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                raise

        if self.spotter_proc.stdout is not None:
            try:
                result = self.spotter_proc.stdout.readline()
                if result != b'':
                    return json.loads(result)
            except Exception as e:
                raise
        return None
