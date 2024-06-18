from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


def generate_keys(private_key_path="private_key.pem", public_key_path="public_key.pem"):
    # Generate private key
    private_key = Ed25519PrivateKey.generate()

    # Obtain the public key
    public_key = private_key.public_key()

    # Serialize the private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Print the keys
    print("Private Key:\n", private_pem.decode('utf-8'))
    print("Public Key:\n", public_pem.decode('utf-8'))

    # Save the private key to a file
    with open(private_key_path, "wb") as f:
        f.write(private_pem)

    # Save the public key to a file
    with open(public_key_path, "wb") as f:
        f.write(public_pem)


if __name__ == '__main__':
    generate_keys()