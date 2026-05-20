class DomainError(Exception):
    code = 'DOMAIN_ERROR'


class DomainValidationError(DomainError):
    code = 'DOMAIN_VALIDATION'
