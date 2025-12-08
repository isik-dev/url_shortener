from httpx import AsyncClient


async def test_generate_short_url(ac: AsyncClient):
    result = await ac.post(url="/short_url", json={"long_url": "https://google.com"})
    assert result.status_code == 200
