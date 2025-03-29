from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

import logging

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error_code": getattr(exc, "default_code", "error"),
            "error_message": str(exc.detail),
            "status_code": response.status_code,
        }

    return response

class CustomAPIException(APIException):
    status_code = 400
    default_detail = "예기치 않은 오류가 발생했습니다."
    default_code = "error"

    logger = logging.getLogger(__name__)

    def __init__(self, detail=None, status_code=None, code=None):
        super().__init__(detail=detail)
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.default_code = code

        # 예외 발생 시 로깅
        self.logger.error(f"CustomAPIException: {self.default_code} - {self.detail}")

class NotFoundException(CustomAPIException):
    status_code = 404
    default_detail = "리소스를 찾을 수 없습니다."
    default_code = "not_found"

class UnauthorizedException(CustomAPIException):
    status_code = 401
    default_detail = "인증이 필요합니다."
    default_code = "unauthorized"

class ForbiddenException(CustomAPIException):
    status_code = 403
    default_detail = "이 작업을 수행할 권한이 없습니다."
    default_code = "forbidden"

class ServiceUnavailableException(CustomAPIException):
    status_code = 503
    default_detail = "현재 서비스를 사용할 수 없습니다. 잠시 후 다시 시도해주세요."
    default_code = "service_unavailable"

class SubscriptionConflictException(CustomAPIException):
    status_code = 400
    default_detail = "이미 구독된 항목입니다."
    default_code = "subscription_conflict"
