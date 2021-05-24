# pylint: disable=line-too-long
# pylint: disable=unused-argument
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from django.conf import settings


class CustomException(APIException):
    status_code = settings.HTTP_API_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = {field: force_text(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}
