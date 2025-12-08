from src.database.models import ShortURL
from src.exceptions import SlugAlreadyExistsError

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def add_slug_to_db(
        slug: str, 
        long_url: str, 
        session: AsyncSession
):
    new_slug = ShortURL(
        slug=slug,
        long_url=long_url
    )
    try:
        session.add(new_slug)
    except IntegrityError:
        raise SlugAlreadyExistsError
        
    await session.commit()


async def get_long_by_slug_from_db(slug: str, session: AsyncSession) -> str | None:
    query = select(ShortURL).filter_by(slug=slug)
    result = await session.execute(query)
    res = result.scalar_one_or_none()
    return res.long_url if res.long_url else None
