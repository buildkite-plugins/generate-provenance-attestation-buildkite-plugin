import base64
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from attestation_generator.enveloper import Enveloper
from attestation_generator.helpers import example_rsa_private_key, example_rsa_public_key


class EnveloperTests(unittest.TestCase):
    def test_sign_payload(self) -> None:
        enveloper = Enveloper(key_id="test", private_key_b64=example_rsa_private_key())
        payload = "TEST PAYLOAD"

        signature = enveloper.sign_payload(payload)

        self.assertSignatureIsValid(
            payload=payload, signature=signature, public_key=example_rsa_public_key()
        )

    def test_wrap(self) -> None:
        enveloper = Enveloper(
            key_id="example_key_id", private_key_b64=example_rsa_private_key()
        )
        payload = json.dumps(dict(name="John Doe", city="Melbourne"))
        result = json.loads(enveloper.wrap(payload))

        self.assertEqual(result["payloadType"], "application/vnd.in-toto+json")

        self.assertEqual(
            result["payload"],
            "eyJuYW1lIjogIkpvaG4gRG9lIiwgImNpdHkiOiAiTWVsYm91cm5lIn0=",
        )

        self.assertEqual(result["signatures"][0]["keyid"], "example_key_id")

        self.assertSignatureIsValid(
            payload=result["payload"],
            signature=result["signatures"][0]["sig"],
            public_key=example_rsa_public_key(),
        )

    def assertSignatureIsValid(
        self, payload: str, signature: str, public_key: str
    ) -> None:
        public_key_file = NamedTemporaryFile(delete=False)
        public_key_file.write(base64.b64decode(public_key))
        public_key_file.close()

        signature_file = NamedTemporaryFile(delete=False)
        signature_file.write(base64.b64decode(signature))
        signature_file.close()

        command = [
            "openssl",
            "dgst",
            "-sha256",
            "-verify",
            public_key_file.name,
            "-signature",
            signature_file.name,
        ]

        stdout_response = subprocess.run(
            command,
            capture_output=True,
            input=bytearray(payload, "utf-8"),
        )

        Path(public_key_file.name).unlink()
        Path(signature_file.name).unlink()

        self.assertEqual(stdout_response.stdout.decode("utf-8").strip(), "Verified OK")
