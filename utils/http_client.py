from utils.interfaces import HttpClient, Response
import httpx

class HttpxClient(HttpClient):
    def __init__(self, verify_ssl: bool = False, cert=None, follow_redirects=True):
        self.client = httpx.Client(verify=verify_ssl, cert=cert, follow_redirects=follow_redirects)

    def post(self, url: str, json: dict) -> Response:
        response = self.client.post(url, json=json)
        response.raise_for_status()
        return Response(response.status_code, response.text)

    def get(self, url: str) -> Response:
        response = self.client.get(url)
        response.raise_for_status()
        return Response(response.status_code, response.text)