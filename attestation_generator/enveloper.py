import base64
import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile


class Enveloper:
    def __init__(self, key_id: str, private_key_b64: str):
        self.key_id: str = key_id
        self.private_key: bytes = base64.b64decode(private_key_b64)

    def wrap(self, payload: str) -> str:
        payload_b64_bytes: bytes = base64.b64encode(
            bytearray(payload, encoding="utf-8")
        )

        signature = self.sign_payload(payload=payload_b64_bytes.decode("utf-8"))

        result = dict(
            payloadType="application/vnd.in-toto+json",
            payload=payload_b64_bytes.decode("utf-8"),
            signatures=[dict(keyid=self.key_id, sig=signature)],
        )
        return json.dumps(result)

    def sign_payload(self, payload: str) -> str:
        private_key_file = NamedTemporaryFile(delete=False)
        private_key_file.write(self.private_key)
        private_key_file.close()

        command = ["openssl", "dgst", "-sha256", "-sign", private_key_file.name]

        result = subprocess.run(
            command, capture_output=True, input=bytearray(payload, "utf-8")
        )

        Path(private_key_file.name).unlink()
        return base64.b64encode(result.stdout).decode("utf-8")
