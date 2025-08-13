import json
import os


class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"


class Library:
    def __init__(self, file_name="library.json"):
        self.file_name = file_name
        self.books = []
        self.load_books()

    def load_books(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.books = [Book(**book) for book in data]
                except json.JSONDecodeError:
                    self.books = []
        else:
            self.books = []

    def save_books(self):
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump([book.__dict__ for book in self.books], f, ensure_ascii=False, indent=4)

    def add_book(self, book: Book):
        if self.find_book(book.isbn):
            print("Bu ISBN numarasıyla kayıtlı bir kitap zaten var.")
            return
        self.books.append(book)
        self.save_books()
        print("Kitap başarıyla eklendi.")

    def remove_book(self, isbn: str):
        book = self.find_book(isbn)
        if book:
            self.books.remove(book)
            self.save_books()
            print("Kitap silindi.")
        else:
            print("Kitap bulunamadı.")

    def list_books(self):
        if not self.books:
            print("Kütüphane boş.")
            return
        for book in self.books:
            print(book)

    def find_book(self, isbn: str):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
