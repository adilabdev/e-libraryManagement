import httpx
from typing import Optional, Dict, List
from .exceptions import APIError

class OpenLibraryClient:
    BASE_URL = "https://openlibrary.org"

    async def _fetch_data(self, endpoint: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}{endpoint}", timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise APIError(f"API Hatası: {e}")

    async def fetch_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        return await self._fetch_data(f"/isbn/{isbn}.json")

    async def search_books(self, query: str, limit: int = 5) -> List[Dict]:
        data = await self._fetch_data(f"/search.json?q={query}&limit={limit}")
        return data.get("docs", [])