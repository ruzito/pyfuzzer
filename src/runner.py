import subprocess
import os

def run_program(program_path, input_data, use_stdin=False, input_file=None):
    if use_stdin:
        process = subprocess.run([program_path], input=input_data, text=True, capture_output=True)
    else:
        with open(input_file, 'wb') as file:
            file.write(input_data)
        process = subprocess.run([program_path, input_file], capture_output=True, text=True)

    return process

import subprocess
import signal
import time

class Runner:
    def __init__(self, cmd, stdin, args, timeout):
        pass

# Function to handle Ctrl+C
def signal_handler(sig, frame):
    print('Stopping...')
    exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Loop to run the subprocess
while True:
    print("Running subprocess...")
    # Replace 'your_command' with the command you want to run
    subprocess.run(['your_command'])
    # Optional: add a delay between runs
    time.sleep(1)