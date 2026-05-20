class ApplicationError(Exception):
    code = 'APPLICATION_ERROR'
    http_status = 500


class ValidationError(ApplicationError):
    code = 'VALIDATION_ERROR'
    http_status = 400


class ConflictError(ApplicationError):
    code = 'CONFLICT'
    http_status = 409


class NotFoundError(ApplicationError):
    code = 'NOT_FOUND'
    http_status = 404


class ExternalServiceError(ApplicationError):
    code = 'EXTERNAL_SERVICE_ERROR'
    http_status = 502


class AdapterError(ApplicationError):
    code = 'ADAPTER_ERROR'
    http_status = 400


class PermissionDeniedError(ApplicationError):
    code = 'FORBIDDEN'
    http_status = 403
