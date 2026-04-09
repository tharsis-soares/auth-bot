from abc import ABC, abstractmethod
import json

class Response:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text

    def json(self):
        return json.loads(self.text)

class HttpClient(ABC):
    @abstractmethod
    def post(self, url: str, json: dict) -> Response:
        pass

    @abstractmethod
    def get(self, url: str) -> Response:
        pass

class Logger(ABC):
    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    @abstractmethod
    def success(self, message: str):
        pass