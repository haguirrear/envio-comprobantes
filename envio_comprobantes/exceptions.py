class BaseException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class FailAuthToken(BaseException):
    pass


class FailSendReceipt(BaseException):
    pass


class FailObteinTicket(BaseException):
    pass


class FailZipFile(BaseException):
    pass


class FailHashFile(BaseException):
    pass


class FailParseTicket(BaseException):
    pass
