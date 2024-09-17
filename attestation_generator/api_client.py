import json
from collections import OrderedDict
from http.client import HTTPSConnection
from typing import Any, cast, List, Mapping
from urllib.parse import urlencode


class ApiClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        host = "agent.buildkite.com"
        self.conn = HTTPSConnection(host)
        self.headers = {"Host": host, "Authorization": "Token {}".format(access_token)}

    # Warning, this uses an internal undocumented endpoint and can break without any notice.
    # The long term goal is to use `buildkite artifact search` with `--format %T`
    # once this version has been released and is widely available: https://github.com/buildkite/agent/pull/2974
    def get_artifacts_list(
        self, query: str, build_id: str, job_id: str
    ) -> List[Mapping[str, Any]]:

        params = OrderedDict(
            query=query,
            scope=job_id,
        )

        path = "/v3/builds/{}/artifacts/search?{}".format(build_id, urlencode(params))

        self.conn.request("GET", path, headers=self.headers)
        response_body = self.conn.getresponse().read()
        return cast(List[Mapping[str, Any]], json.loads(response_body))
