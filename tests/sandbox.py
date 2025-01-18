import hashlib
from datetime import datetime

def generate_id(title):
    hash_object = hashlib.sha1(title.encode())
    short_hash = hash_object.hexdigest()[:6]  # Take the first 6 characters
    return short_hash

print(generate_id("Shopping list" + str(datetime.now().timestamp())))