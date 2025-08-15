import pytest
from library_app.api_client import OpenLibraryClient

@pytest.mark.asyncio
async def test_fetch_book_success():
    client = OpenLibraryClient()
    data = await client.fetch_book_by_isbn("9780061120084")  # Küçük Prens
    assert data is not None
    assert "title" in data
    assert "authors" in data

@pytest.mark.asyncio
async def test_search_books():
    client = OpenLibraryClient()
    results = await client.search_books("Dune")
    assert len(results) > 0
    assert all("isbn" in doc for doc in results[:3])