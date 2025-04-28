from fastapi import Request, HTTPException, status


async def get_token_from_cookie(request: Request):
    token = request.cookies.get('token')

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Cookie is missing',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return token