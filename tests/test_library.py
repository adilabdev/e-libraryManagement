import pytest
import os
from library_app.models import Book, Library

@pytest.fixture
def temp_library(tmp_path):
    db_file = tmp_path / "test_library.json"
    lib = Library(str(db_file))
    yield lib
    if os.path.exists(db_file):
        os.remove(db_file)

def test_add_book(temp_library):
    book = Book("Test Book", "Test Author", "123")
    assert temp_library.add_book(book)
    assert not temp_library.add_book(book)  # Duplicate

def test_remove_book(temp_library):
    book = Book("Test Book", "Test Author", "123")
    temp_library.add_book(book)
    assert temp_library.remove_book("123")
    assert not temp_library.remove_book("456")  # Non-existent

@pytest.mark.asyncio
async def test_fetch_book_from_api(temp_library):
    # Test with known valid ISBN
    book = await temp_library.fetch_book_from_api("9780061120084")
    assert book is not None
    assert "To Kill a Mockingbird" in book.title
    
    # Test with invalid ISBN
    assert await temp_library.fetch_book_from_api("0000000000") is None