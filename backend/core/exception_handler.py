from rest_framework.views import exception_handler

from core.responses import APIResponse


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is None:
        return APIResponse.error(
            message="Internal Server Error.",
            status_code=500,
        )

    return APIResponse.error(
        message=response.data.get("detail", "Something went wrong."),
        errors=response.data,
        status_code=response.status_code,
    )