from src.service import generate_slug


async def test_generate_short_url(session):
    res = await generate_slug(long_url="https://x.com", session=session)
    assert type(res) is str
    assert len(res) == 6