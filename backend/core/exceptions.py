from rest_framework.exceptions import APIException
from rest_framework import status


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad Request."


class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized."


class ForbiddenException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Forbidden."


class NotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not Found."