from sqlmodel import Session, select, and_
from src.models.users import OTP
import time
import time
from src.configs.config import settings


def create_otp(email: str, otp: str, session: Session):
    statement = select(OTP).where(OTP.email == email)
    exist_otp = session.exec(statement=statement).first()

    if exist_otp:
        time_left = exist_otp.expires_at - int(time.time())
        # check time allow to create new OTP
        print(">>> time_left: ", time_left)
        print(
            ">>> settings.OTP_EXPIRE_MINUTES * 60 - settings.OTP_COOLDOWN_SECONDS: ",
            settings.OTP_EXPIRE_MINUTES * 60 - settings.OTP_COOLDOWN_SECONDS,
        )
        if time_left < (
            settings.OTP_EXPIRE_MINUTES * 60 - settings.OTP_COOLDOWN_SECONDS
        ):
            return None

    if exist_otp:
        session.delete(exist_otp)
        session.commit()

    expire_at = int((time.time() + settings.OTP_EXPIRE_MINUTES) * 60)
    otp_re = OTP(email=email, expires_at=expire_at, otp=otp)
    session.add(otp_re)
    session.commit()
    session.refresh(otp_re)
    return otp_re


def verify_otp(session: Session, email: str, otp: str) -> bool:
    statement = select(OTP).where(and_(OTP.email == email, OTP.otp == otp))
    otp_record = session.exec(statement).first()
    if otp_record and otp_record.expires_at > int(time.time()):
        session.delete(otp_record)
        session.commit()
        return True
    return False
