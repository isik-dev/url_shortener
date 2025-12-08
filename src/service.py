from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError

from src.database.crud import add_slug_to_db, get_long_by_slug_from_db
from src.shortener import generate_random_slug

async def generate_slug(
        long_url: str,
        session: AsyncSession
) -> str:
    # TODO: validate url before doing anything

    async def _generate_slug_ad_add_to_db(session: AsyncSession) -> str:
        # 1. generate slug
        slug = generate_random_slug()
        # 2. add to db
        await add_slug_to_db(slug=slug, long_url=long_url, session=session)
        return slug

    for attempt in range(5):
        try:
            slug = await _generate_slug_ad_add_to_db(session=session)
            return slug
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex



    # 3. return to the client
    return slug

async def get_url_by_slug(slug: str, session: AsyncSession) -> str | None:
    long_url = await get_long_by_slug_from_db(slug=slug, session=session)
    if not long_url:
        raise NoLongUrlFoundError()
    return long_url