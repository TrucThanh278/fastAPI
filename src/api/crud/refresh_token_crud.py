from sqlmodel import select, Session, and_
from src.models.tokens import RefreshToken


def get_refresh_token(
    session: Session, user_id: str, refresh_token: str, is_revoked: bool = False
):
    if is_revoked:
        return None
    statement = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == is_revoked,
    )
    result = session.exec(statement).first()
    return result


def create_refresh_token(session: Session, user_id: str, token: str):
    refresh_token = RefreshToken(user_id=user_id, token=token)
    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)
    return refresh_token


def revoke_refresh_token(session: Session, refresh_token: str, user_id: str):
    statement = select(RefreshToken).where(
        and_(RefreshToken.token == refresh_token, RefreshToken.user_id == user_id)
    )
    try:
        result = session.exec(statement).first()
    except Exception as e:
        print("Error get refresh token !")
    result.is_revoked = True
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def get_refresh_token_active(session: Session, user_id: str, is_revoked: bool = False):
    statement = select(RefreshToken).where(
        and_(RefreshToken.user_id == user_id, RefreshToken.is_revoked == is_revoked)
    )
    result = session.exec(statement).first()
    return result
