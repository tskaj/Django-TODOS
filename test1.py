from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import base64

def encode_uid(user_id):
    uid_bytes = force_bytes(user_id)
    encoded_uid = urlsafe_base64_encode(uid_bytes).rstrip(b'=')
    return encoded_uid.decode('utf-8')

def decode_uid(encoded_uid):
    # Add padding if necessary
    padding = '=' * (4 - (len(encoded_uid) % 4))
    encoded_uid_padded = encoded_uid + padding
    uid_bytes = urlsafe_base64_decode(encoded_uid_padded)
    return smart_str(uid_bytes)

# Test encoding and decoding
user_id = 4
encoded_uid = encode_uid(user_id)
decoded_uid = decode_uid(encoded_uid)

print(f"Original User ID: {user_id}")
print(f"Encoded UID: {encoded_uid}")
print(f"Decoded UID: {decoded_uid}")
