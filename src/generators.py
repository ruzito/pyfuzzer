import random
import string

def random_bytes(length, byte_range):
    return bytearray(random.choices(range(byte_range[0], byte_range[1]), k=length))
