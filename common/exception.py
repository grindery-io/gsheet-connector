from rest_framework.exceptions import PermissionDenied
from rest_framework import status


class CustomException(PermissionDenied):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32600,
            "message": "Invalid Request"
        },
        "id": 1
    }

    def __init__(self, code, message, status_code=None):
        self.detail = {
            "result": False,
            "errorCode": code,
            "errorMsg": message
        }
        if status_code is not None:
            self.status_code = status_code
