from fastapi import HTTPException, status


def get_current_user():
    """Pengganti auth()->check() di Laravel.

    TODO: ganti dengan implementasi asli (JWT / session / OAuth2).
    Sementara dibiarkan lolos supaya endpoint bisa dites.
    """
    user = {"id": "dev"}
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthenticated")
    return user
