import errno
import json
import os
import subprocess
import tempfile
from os.path import join

import numpy as np
import soundfile as sf


class WakeDetector:
    def __init__(self, spotter_path, wakeword_model_path, threshold, samplerate=16000):
        self.spotter_path = spotter_path
        self.samplerate = samplerate
        self.tempfile_name = tempfile.NamedTemporaryFile(suffix=".wav").name
        self.spotter_args = [
            "test",
            "-e",
            "-g",
            "-m",
            "3",
            "-t",
            str(threshold),
            wakeword_model_path,
            self.tempfile_name,
        ]

    def _start_proc(self):
        spotter_command = [self.spotter_path] + self.spotter_args
        self.spotter_proc = subprocess.Popen(spotter_command, stdout=subprocess.PIPE)

    def stop(self):
        self.spotter_proc.terminate()
        self.spotter_proc.wait()

    def detect(self, data):
        # Save data as temporary file to be read by spotter
        # Todo, find an alternative to this to avoid read/write
        sf.write(
            self.tempfile_name,
            np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0,
            self.samplerate,
        )
        #print(self.tempfile_name)
        try:
            self._start_proc()
            # wait process to finish
            self.spotter_proc.wait()
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                raise

        if self.spotter_proc.stdout is not None:
            try:
                # Discard first lines
                self.spotter_proc.stdout.readline()
                self.spotter_proc.stdout.readline()
                # Keep only potentially relevant lines
                result = self.spotter_proc.stdout.readline()

                if result != b"":
                    result = result.decode("utf-8").split("score: ")[1].split(",")[0]
                    return float(result)
            except Exception as e:
                raise
        return None
