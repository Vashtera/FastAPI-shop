from datetime import UTC, datetime, timedelta

import jwt 
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from ..core.config import settings


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password) 

"""
(для меня)
Принцип работы, мы копируем данные которые передали в функцию по созданию токена,
а также необязательное время жизни токена. 
Также проверяем если оно есть, то нынешнее время + время жизни токена, если же нет, то
нынешнее время + разница которой мы передали стандартное значение из конфига.
После словарь который мы скопировали мы обновляем и добавляем время жизни токена где ключ
"exp", и объявлем переменную с закодированным jwt и передалем туда 3 обязательных параметра для
кодировки, а именно данные, секретный ключ и алгоритм
"""

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes = settings.access_token_expires_minutes,
        )
    to_encode.update({"exp": expire}) # exp = expiration(время истечения токена)
    encoded_jwt = jwt.encode( 
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )
    return encoded_jwt


"""
(для меня)
Тут уже обратная работа прошлой функции, оно декодирует токен и сравнирвает данные что мы передали.
то есть, переменная payload(полезная нагрузка) и объявляем jwt.decode для декодирования
и передаем 2 нужные и 2 доп атрибута, а именно сам токен, секретный ключ, дальше уже алгоритм
для декодирования и очень важно для безопастности опции по которым мы проверяем нужные данные так
сказать. А именно время жизни токена и субъект(User id). Если же токен не действителен или еще что-то
то возвращаем None. Если же исключении не было, то возвращаем блок else где получаем sub(User id)
"""
def verify_access_token(token: str) -> str | None:
    """Подтверждение токена JWT и возвращение объекта(User id) если он существует"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError:
        return None
    else:
        return payload.get("sub") # sub = User id