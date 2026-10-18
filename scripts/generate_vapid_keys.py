#!/usr/bin/env python
"""
Generate one VAPID keypair for Web Push.

Run ONCE, ever. The public key is baked into every browser subscription the
app has issued, so replacing the private key does not re-key them — it
invalidates all of them, and every installed reader stops receiving
notifications with no error visible anywhere. Treat it like a signing key.

    ./venv/bin/python scripts/generate_vapid_keys.py

The private key goes in .env locally and in the Render dashboard in
production — render.yaml declares it with `sync: false`, so it is never in
this repository. Do not paste it into a commit, an issue, or a chat.

VAPID_SUBJECT must be a mailto: or https: URL identifying the sender. Push
services use it to reach whoever is sending; a wrong value is grounds for
them to drop the message.
"""
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def _b64(raw: bytes) -> str:
    """URL-safe base64, unpadded — the encoding the Web Push spec uses."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def main() -> None:
    key = ec.generate_private_key(ec.SECP256R1())

    # The raw 32-byte scalar, which is what py_vapid reads from an env var.
    private_raw = key.private_numbers().private_value.to_bytes(32, "big")

    # Uncompressed point: 0x04 || X || Y, 65 bytes. This is the
    # applicationServerKey the browser is handed.
    public_raw = key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )

    print("Add these to .env locally, and to the Render dashboard in production.")
    print("Generate ONCE: a new private key silently invalidates every existing")
    print("subscription, with no error for the reader.\n")
    print(f"VAPID_PUBLIC_KEY={_b64(public_raw)}")
    print(f"VAPID_PRIVATE_KEY={_b64(private_raw)}")
    print("VAPID_SUBJECT=mailto:you@example.com   # <- your real address")


if __name__ == "__main__":
    main()
