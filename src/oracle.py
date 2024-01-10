import re

def analyze_output(process):
    asan_error = re.search(r'ERROR: AddressSanitizer', process.stderr)
    return_code = process.returncode
    return {'asan_error': asan_error, 'return_code': return_code}