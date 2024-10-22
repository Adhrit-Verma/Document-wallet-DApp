import secrets

def generate_secret_key(length=32):
    # Generate a secret key of specified length (default is 32 bytes)
    secret_key = secrets.token_hex(length)
    return secret_key

# Generate and print the secret key
if __name__ == "__main__":
    key = generate_secret_key()
    print(f"Generated Secret Key: {key}")
