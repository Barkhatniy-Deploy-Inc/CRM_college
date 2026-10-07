"""Ошибки проверки токенов, не зависящие от фреймворка."""


class TokenError(Exception):
    """Базовое исключение при работе с токеном."""


class TokenExpiredError(TokenError):
    """Срок действия токена истёк."""


class TokenTypeError(TokenError):
    """Тип токена не соответствует ожидаемому."""
