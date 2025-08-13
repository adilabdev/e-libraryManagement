from models import Book, Library

def main():
    library = Library()

    while True:
        print("\n--- Kütüphane Yönetim Sistemi ---")
        print("1. Kitap Ekle")
        print("2. Kitap Sil")
        print("3. Kitapları Listele")
        print("4. Kitap Ara")
        print("5. Çıkış")

        choice = input("Seçiminiz: ")

        if choice == "1":
            title = input("Kitap adı: ")
            author = input("Yazar: ")
            isbn = input("ISBN: ")
            book = Book(title, author, isbn)
            library.add_book(book)

        elif choice == "2":
            isbn = input("Silmek istediğiniz kitabın ISBN'i: ")
            library.remove_book(isbn)

        elif choice == "3":
            library.list_books()

        elif choice == "4":
            isbn = input("Aradığınız kitabın ISBN'i: ")
            book = library.find_book(isbn)
            if book:
                print(book)
            else:
                print("Kitap bulunamadı.")

        elif choice == "5":
            print("Programdan çıkılıyor...")
            break
        else:
            print("Geçersiz seçim. Tekrar deneyin.")

if __name__ == "__main__":
    main()
