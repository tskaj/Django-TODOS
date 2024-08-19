import base64

def test_base64_encoding(value):
    encoded = base64.urlsafe_b64encode(value.encode('utf-8'))
    print(f"Base64 Encoded: {encoded}")  # Print encoded bytes
    return encoded.decode('utf-8')

# Test encoding a simple string
encoded_value = test_base64_encoding("4")
print(f"Base64 Encoded Value for '4': {encoded_value}")
