from rest_framework import status
from rest_framework.response import Response

from core.application.errors import ApplicationError


def handle_application_error(exc: ApplicationError) -> Response:
    return Response(
        {
            'error': str(exc),
            'code': exc.code,
        },
        status=exc.http_status or status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
