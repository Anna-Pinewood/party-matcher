import os

from dotenv import load_dotenv
from sqlalchemy import BigInteger, ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
engine = create_async_engine(url=os.getenv("SQLALCHEMY_URL"))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    language: Mapped[str] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(25))
    gender: Mapped[int] = mapped_column()
    age: Mapped[int] = mapped_column()
    phone_number: Mapped[str] = mapped_column(String(25))
    vk_link: Mapped[str] = mapped_column(String(25), nullable=True)
    reddit_link: Mapped[str] = mapped_column(String(25), nullable=True)
    cv: Mapped[str] = mapped_column(String(25), nullable=True)
    text_desc: Mapped[str] = mapped_column(String(1500), nullable=True)


class Party(Base):
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(120))


class PartyUser(Base):
    __tablename__ = "party_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


async def async_main():
    # async with engine.begin() as conn:
    #     # Удаляем все таблицы, определенные в Base.metadata
    #     await conn.run_sync(Base.metadata.drop_all)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(Party.id)))
        party_count = result.scalar()

        if party_count == 0:
            initial_parties = [
                Party(name="Birthday Bash", description="Celebrating a birthday."),
                Party(name="New Year's Eve", description="Welcoming the new year."),
                Party(name="Office Party", description="Annual office gathering."),
            ]

            session.add_all(initial_parties)
            await session.commit()
