# cli.py
import click
from .models import Library, Book

# Tek bir kütüphane nesnesi
library = Library()

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """E-Library Management CLI"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())  # Komut verilmezse ana menü/yardım göster

@cli.command()
@click.option('--title', prompt='Book title')
@click.option('--author', prompt='Author')
@click.option('--isbn', prompt='ISBN')
def add(title, author, isbn):
    """Yeni kitap ekler"""
    book = Book(title, author, isbn)
    library.add_book(book)

@cli.command(name="list-books")
def list_books():
    """Tüm kitapları listeler"""
    library.list_books()

@cli.command()
@click.option('--isbn', prompt='ISBN')
def remove(isbn):
    """ISBN ile kitap siler"""
    library.remove_book(isbn)

@cli.command()
@click.option('--query', prompt='Search by ISBN, title, or author')
def find(query):
    """ISBN, başlık veya yazar ile kitap arar"""
    results = []
    for b in library.books:
        if query.lower() in b.isbn.lower() or query.lower() in b.title.lower() or query.lower() in b.author.lower():
            results.append(b)

    if results:
        for book in results:
            print(book)
    else:
        # Yakın eşleşme kontrolü
        titles = [b.title for b in library.books]
        authors = [b.author for b in library.books]
        suggestions = get_close_matches(query, titles + authors, n=3, cutoff=0.5)
        if suggestions:
            print("Book not found. Did you mean?")
            for s in suggestions:
                print(f" - {s}")
        else:
            print("Book not found.")
