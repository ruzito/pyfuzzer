import subprocess
import random
import string


def generate_random_input(length):
    """Generates a random string of specified length."""
    return "".join(random.choices(string.printable, k=length))


def execute_application(input_str, command):
    """Executes the application with the given input."""
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(input=input_str.encode())
    return process.returncode, stdout, stderr


def minimize_input(input_str, command):
    """Tries to minimize the input that causes the application to fail."""
    for i in range(len(input_str)):
        test_input = input_str[:i] + input_str[i + 1 :]
        ret_code, _, _ = execute_application(test_input, command)
        if ret_code != 0:
            return minimize_input(test_input, command)
    return input_str


def fuzz_test(command, max_length=100, iterations=1000):
    """Fuzz tests an application."""
    for _ in range(iterations):
        input_str = generate_random_input(random.randint(1, max_length))
        ret_code, _, _ = execute_application(input_str, command)

        if ret_code != 0:
            print(f"Failure detected with input: {input_str}")
            minimized_input = minimize_input(input_str, command)
            print(f"Minimized failing input: {minimized_input}")
            break


if __name__ == "__main__":
    # Example: Python command-line application
    fuzz_test(["python", "target_app.py"])
