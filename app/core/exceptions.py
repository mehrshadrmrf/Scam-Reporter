"""Exception های اختصاصی دامنه (Domain-level) برنامه."""


class ScamReportException(Exception):
    """کلاس پایه برای تمام خطاهای اختصاصی پروژه."""

    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ScamReportException):
    def __init__(self, entity: str, identifier: str | int):
        super().__init__(f"{entity} با شناسه {identifier} یافت نشد.", code="NOT_FOUND")


class PermissionDeniedError(ScamReportException):
    def __init__(self, message: str = "شما اجازه دسترسی به این عملیات را ندارید."):
        super().__init__(message, code="PERMISSION_DENIED")


class UserBannedError(ScamReportException):
    def __init__(self, message: str = "حساب کاربری شما مسدود شده است."):
        super().__init__(message, code="USER_BANNED")


class UserRestrictedError(ScamReportException):
    def __init__(self, message: str = "حساب کاربری شما محدود شده و امکان ثبت گزارش جدید ندارید."):
        super().__init__(message, code="USER_RESTRICTED")


class DuplicateReportError(ScamReportException):
    def __init__(self, existing_case_id: str):
        super().__init__(
            f"این گزارش با پرونده موجود ({existing_case_id}) شباهت بالایی دارد و ادغام شد.",
            code="DUPLICATE_REPORT",
        )
        self.existing_case_id = existing_case_id


class InvalidStateTransitionError(ScamReportException):
    def __init__(self, current: str, target: str):
        super().__init__(
            f"انتقال وضعیت از «{current}» به «{target}» مجاز نیست.",
            code="INVALID_STATE_TRANSITION",
        )


class ValidationError(ScamReportException):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")
