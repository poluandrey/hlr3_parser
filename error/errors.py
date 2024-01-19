class BaseError(Exception):
    pass


class GetFileError(BaseError):
    """
    Raised when could not get file for parsing
    """
    pass
