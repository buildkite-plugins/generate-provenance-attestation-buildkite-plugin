import base64
import uuid
import zlib
from pathlib import Path
from typing import Dict, List, Mapping

from attestation_generator.api_client import ApiClient
from attestation_generator.path_sha import PathSha


def fake_env() -> Dict[str, str]:
    return {
        "BUILDKITE_BRANCH": "main",
        "BUILDKITE_BUILD_ID": generate_uuid(),
        "BUILDKITE_BUILD_NUMBER": "49387",
        "BUILDKITE_COMMAND": "gem build awesome-logger.gemspec",
        "BUILDKITE_COMMIT": "2b4ba8fe79386d40ce27dc5f6cc4161a0f598cc2",
        "BUILDKITE_JOB_ID": generate_uuid(),
        "BUILDKITE_ORGANIZATION_ID": generate_uuid(),
        "BUILDKITE_ORGANIZATION_SLUG": "acme-corp",
        "BUILDKITE_PIPELINE_ID": generate_uuid(),
        "BUILDKITE_PIPELINE_SLUG": "awesome-logger",
        "BUILDKITE_REPO": "https://github.com/acme-corp/awesome-logger.git",
        "BUILDKITE_STEP_ID": generate_uuid(),
        "BUILDKITE_STEP_KEY": "build-gem",
        "BUILDKITE_TAG": "v1.6.0",
    }


def fake_files() -> List[PathSha]:
    return [
        dict(path="file_1.ext", sha256sum="fake_sha_1"),
        dict(path="file_2.ext", sha256sum="fake_sha_2"),
    ]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_files_and_shas(
    query: str, build_id: str, job_id: str, access_token: str
) -> List[PathSha]:
    client = ApiClient(access_token)

    subqueries = map(lambda s: s.strip(), query.split(";"))

    result = []
    for subquery in subqueries:
        artifacts = client.get_artifacts_list(subquery, build_id, job_id)
        result += list(
            map(
                artifact_to_path_sha,
                artifacts,
            )
        )
    return result


def strip_dirs(path: str) -> str:
    p = Path(path)
    return p.name


def artifact_to_path_sha(artifact: Mapping[str, str]) -> PathSha:
    return dict(
        path=strip_dirs(str(artifact["path"])),
        sha256sum=str(artifact["sha256sum"]),
    )


def example_rsa_private_key() -> str:
    # THIS IS INSECURE AND INTENDED SOLELY TO DEMONSTRATE
    # SIGNING MECHANISMS.
    #
    # `key` value is the result of:
    #
    # `openssl genrsa -out private_key.pem 2048` → zlib.compress → b64encode
    # e.g. b64encode(zlib.compress(`private_key.pem`)).decode("utf-8")
    #
    # So we reverse the process here
    key = "eNplVbeutOgSzHmKzdEvGNwcgg3w3nsy7Icb7GCffs/uDW8HFbRa6lKVSvXnz++wgqSYf9muEjK+8JcmJP8u/0CGoggHo7AMz5gs6JembyX6RFnGEUSG8ThWS04AvJYBAsNMv3cO7ws0/GK+i5XkNQMV4fE4yp5ZZo/YGezNScmwYX3dFjzJcxzyAlvliENRBwMLXILUFA4qRH7zBwDhdvHQ67vCRQBfB28zl5ZtUtJVaJiSPOYKyNepVv6Idywffe1B4/TRgHTErxszwjFdPPVGoTxY7vBOBxcN93Iij292rLiIpBRwADe0VYTpN/sFejVTU0q4727DE27ZSlk3x8jXVeiLfYQWJWqmsNMcR9NhratdT905pKO4ewVRXRWSqEbk+h7NMlQOx3CSUoFjvSVB4D4QZg/XiNAwdT5ZELbhc7x1Nkay0Qp92Xd/MT+GfqgcSk5/Rpo1daZMVGv7FmPVwckJ6adloUszMMBgGUbgwK/aUTCrxYR1SKWQpVbVfYp/UDEYxbSPNUAuaL0624w0dv6BIRDq8E/pdJZPC6nhkUrYYBqIg7E26Fn1eCMcUBLvzt7ZkfubiZWPWpyBwBnra87HSiDHKlHlCXQ4kqJt0ku7pyaB9ytYcAdDxDVN2WaD3GYPs/oMhjd5TAnVf9ot5I0fi8igB/CSpB9wThPdzvByuAfvjOf3HyKgtbkFd0TL+elR+YFl8ps4M47SVVF16r1ywrxFIJHI9kbP8MemNtxAzByzXffbDXznlJ8X1jW53qNos66lIM5np4MvIeZf/7Q7WAesj0D6ZvdyltveDdRtxUwjTncXmfpJfQqMc/D2pTIanO/aqbHA4bf1/cHOg7Vwqo8bd/WhfRHKIXb3kmRPGE5HEN+PtXanoHlCn3H9u2nqtnoPP87G75Hn0YCI4sXWpUmn0vjdQZ9OaOrToBBGPYbB2g/evaSPN4mxl3A1J4rinVza3sK7O6LzKmM+LrU6MjC3a1m9SUGsRRhF8Kh5hlsOmXCIcuHjJDmf/1HufV+Y0Ef2lPndWe4WIDUtjlfj3NxFo8pEQ219wASWVShRUglzO1a43NgsdJJfE98tcH++FKh8a/+Q76boxULHH7g9lFDGC669Sg8aPCptt88udG+z79RkyjiHQAj1bSpodvK1ZzNoJolxjZslHWEwITmvVtcAMZr9JY02dJ23lxcfCvmXMoeyc8Cnje5lr4tE0JPJycMY9V5b7YyoImFfwnySpenXlum5ca5koOGOu3mpoxdD5xah7eAx2eOnmm1r+fHBUvZRkutfxwPU6UQ/L8WR2zTqsoAvsSdsiwSSm99Af7wy119qYIn5CkvShmULJqQIWvCbdDHShImeSHM4Hw4Ep8QV4NovM0mMg/ItJEvUMiqZFtEieu5NwhtsZ7+6pP/AVZalsE/E6XafqrR/0DZH3n3dirx5VPC9G3ZPx1BVzlTlmgslrQvXAl0ROkrDdb3o5twYqeedmhbcqddZ9FdNUmYkiVexFBoSTo6ZZwWE8+baJoHCBzYL5i+/VB+TTY6THVCaHsV20UH7ulEOJOyaDPSs0IhMbSxKatGSb2QAkULnH+0Umw1p9JfNdTMXVFRBBn3lm2TqpJ/kPgJ0wsbCAuizyv5ji6yf7yosjv2iQOT2ULk9WqmexL8CElP/PvWJAsQ0KI28eg0/LwUXHVawmGIlf6LtDWbh95uu0qPhDhAhv4L1TbYbV5vgJ5I+yvrqwN9/Q//1jmDy/99F/wD7JCs8"
    compressed: bytes = base64.b64decode(bytearray(key, "utf-8"))
    plaintext: bytes = zlib.decompress(compressed)

    # Return base64 encoded plaintext
    return base64.b64encode(plaintext).decode("utf-8")


def example_rsa_public_key() -> str:
    # This value is the result of
    # `openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem` → plaintext → b64encode
    # e.g. b64encode(`public_key.pem`).decode("utf-8")
    return "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUEweFBmdFFMYWptRzN3SEZiODBDTAptampaUHoydmtxV0hRQVZYOGNqdnFCNlYxUXhBWG0vME91cndQaEFtUDMrdDRIdngrdzc0SUZiTVE5YmEvbkZQCnNid3p3TVNtckJtSTN0RldlUTlrUlA3VUhxdzcxN3RtNTB5czlGMmN5b0JyMTljdGpGWjJha2ljdEcxS3NsY20KWlVkRmJuYU9iN1dyNjl4ZjJlb0VJQXBZbmx0aThnYllDM3FlcUdlRWU0N04yQXFySFJ5eloxa3l5YmRwaEl0TwpId0hEMlc5OUdaYTMzcmkyVWFWZlZsNDlWRm4zbkJoU1Z1YSs1elhWU0wwREVHSFNQbHk0dVlGRWM5ajVjWi8vCmZ1c00ybEZZbGM3K3l3Vi8ycHpsVXgwMFRsVTI3NVpKWGtPaDJmSi9RVFN3SFdDVHJMWEozby9tTUM4RGp0S28KWlFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
