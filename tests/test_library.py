import os
import json
import pytest
from models import Book, Library

TEST_FILE = "test_library.json"

@pytest.fixture
def library():
    # Test öncesi temiz dosya
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    lib = Library(TEST_FILE)
    return lib

def test_add_book(library):
    book = Book("Test Book", "Test Author", "12345")
    library.add_book(book)
    assert library.find_book("12345") is not None

def test_remove_book(library):
    book = Book("Test Book", "Test Author", "12345")
    library.add_book(book)
    library.remove_book("12345")
    assert library.find_book("12345") is None

def test_find_book(library):
    book = Book("Test Book", "Test Author", "12345")
    library.add_book(book)
    found = library.find_book("12345")
    assert found.title == "Test Book"
