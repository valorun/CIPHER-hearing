import subprocess
import json
import errno
import os
from os.path import join

class WakeDetector():
    def __init__(self, raven_path, wakeword_model_path, threshold, samplerate=16000):
        self.raven_path = join(raven_path, 'bin', 'rhasspy-wake-raven')
        self.raven_args = ['--keyword', wakeword_model_path, '--probability-threshold', str(threshold)]
        self.start()

    def start(self):
        raven_command = [self.raven_path] + self.raven_args
        self.raven_proc = subprocess.Popen(
            raven_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        os.set_blocking(self.raven_proc.stdout.fileno(), False)

    def stop(self):
        self.raven_proc.terminate()
        self.raven_proc.wait()

    def detect(self, data):
        try:
            self.raven_proc.stdin.write(data)
            #self.raven_proc.stdin.flush()
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                raise

        if self.raven_proc.stdout is not None:
            try:
                result = self.raven_proc.stdout.readline()
                if result != b'':
                    print(result)
                    return json.loads(result)
            except Exception as e:
                raise
        return None
