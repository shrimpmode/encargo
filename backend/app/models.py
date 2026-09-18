import enum
import secrets
from datetime import UTC, datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class WaitlistState(enum.StrEnum):
    WAITING = "waiting"
    CALLED = "called"
    # Reserved for later lifecycle work (not read or written by this slice):
    SEATED = "seated"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


def _generate_status_token() -> str:
    return secrets.token_urlsafe(32)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    waitlist_entries: Mapped[list[WaitlistEntry]] = relationship(back_populates="restaurant")


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    name: Mapped[str]
    phone: Mapped[str]
    party_size: Mapped[int]
    state: Mapped[WaitlistState] = mapped_column(
        Enum(WaitlistState, native_enum=False, length=20),
        default=WaitlistState.WAITING,
    )
    status_token: Mapped[str] = mapped_column(
        unique=True, index=True, default=_generate_status_token
    )
    joined_at: Mapped[datetime] = mapped_column(default=_utcnow)
    called_at: Mapped[datetime | None] = mapped_column(default=None)

    restaurant: Mapped[Restaurant] = relationship(back_populates="waitlist_entries")
