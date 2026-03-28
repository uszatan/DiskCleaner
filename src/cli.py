import argparse
import os
from .database_engine import DatabaseEngine
from .filesystem_scanner import scan_filesystem

def main():
    """
    Główna funkcja aplikacji, która obsługuje interfejs linii poleceń (CLI).
    Umożliwia użytkownikowi inicjalizację, resetowanie, skanowanie
    oraz wyszukiwanie duplikatów w bazie danych.
    """
    # Tworzenie głównego parsera argumentów.
    # description - tekst wyświetlany w pomocy, wyjaśniający, co robi program.
    parser = argparse.ArgumentParser(description="Narzędzie do czyszczenia dysku i wyszukiwania duplikatów.")

    # Definicja podparserów dla poszczególnych komend (np. 'scan', 'find-dups').
    # To pozwala na tworzenie sub-komend w stylu 'git commit' czy 'docker build'.
    subparsers = parser.add_subparsers(dest="command", help="Dostępne komendy", required=True)

    # --- Komenda 'init-db' ---
    # Tworzenie parsera dla komendy inicjalizującej bazę danych.
    parser_init_db = subparsers.add_parser("init-db", help="Inicjalizuje schemat bazy danych (jeśli nie istnieje).")
    # Argument określający ścieżkę do pliku bazy danych.
    parser_init_db.add_argument("--db", required=True, help="Ścieżka do pliku bazy danych SQLite.")

    # --- NOWA Komenda 'reset-db' ---
    # Tworzenie parsera dla komendy resetującej bazę danych.
    # Ta komenda jest przeznaczona do celów deweloperskich i testowych.
    parser_reset_db = subparsers.add_parser("reset-db", help="Całkowicie usuwa wszystkie dane i odtwarza schemat bazy danych.")
    # Argument określający ścieżkę do pliku bazy danych, która ma zostać zresetowana.
    parser_reset_db.add_argument("--db", required=True, help="Ścieżka do pliku bazy danych SQLite, która zostanie zresetowana.")
    # Dodatkowy argument potwierdzający, aby zapobiec przypadkowemu usunięciu danych.
    # Użycie 'action="store_true"' oznacza, że obecność flagi '--yes' ustawi wartość na True.
    parser_reset_db.add_argument("--yes", action="store_true", help="Potwierdzenie operacji resetowania bazy danych. Wymagane do wykonania.")


    # --- Komenda 'scan' ---
    # Tworzenie parsera dla komendy skanującej system plików.
    parser_scan = subparsers.add_parser("scan", help="Skanuje podany katalog i zapisuje metadane w bazie danych.")
    # Argument określający ścieżkę do katalogu do przeskanowania.
    parser_scan.add_argument("path", help="Ścieżka do katalogu, który ma zostać przeskanowany.")
    # Argument opcjonalny, określający ścieżkę do bazy danych.
    parser_scan.add_argument("--db", required=True, help="Ścieżka do pliku bazy danych SQLite.")

    # --- Komenda 'find-dups' ---
    # Tworzenie parsera dla komendy wyszukującej duplikaty.
    parser_find_dups = subparsers.add_parser("find-dups", help="Wyszukuje potencjalne duplikaty w bazie danych.")
    # Argument opcjonalny, określający ścieżkę do bazy danych.
    parser_find_dups.add_argument("--db", required=True, help="Ścieżka do pliku bazy danych SQLite.")

    # Parsowanie argumentów przekazanych w linii poleceń.
    args = parser.parse_args()

    # Inicjalizacja silnika bazy danych ze ścieżką podaną przez użytkownika.
    db_engine = DatabaseEngine(db_path=args.db)

    # --- Obsługa komend ---

    # Jeśli użytkownik wybrał komendę 'init-db'
    if args.command == "init-db":
        print(f"Inicjalizowanie schematu w bazie danych: {args.db}")
        # Wywołanie metody tworzącej schemat tabel (tylko jeśli nie istnieją).
        db_engine.create_schema()
        print("Schemat bazy danych został pomyślnie utworzony.")

    # Jeśli użytkownik wybrał komendę 'reset-db'
    elif args.command == "reset-db":
        # Sprawdzenie, czy użytkownik użył flagi '--yes' jako zabezpieczenia.
        if not args.yes:
            # Jeśli flaga nie została podana, wyświetl ostrzeżenie i zakończ.
            # To chroni przed przypadkowym i nieodwracalnym usunięciem danych.
            print("BŁĄD: Operacja resetowania bazy danych jest nieodwracalna i wymaga potwierdzenia.")
            print("Proszę dodać flagę '--yes' do polecenia, aby kontynuować.")
            return
        # Jeśli potwierdzenie zostało podane, wywołaj metodę resetującą bazę danych.
        db_engine.reset_database()

    # Jeśli użytkownik wybrał komendę 'scan'
    elif args.command == "scan":
        # Sprawdzenie, czy podana ścieżka jest katalogiem.
        if not os.path.isdir(args.path):
            print(f"Błąd: Podana ścieżka '{args.path}' nie jest prawidłowym katalogiem.")
            return

        print(f"Rozpoczynanie skanowania katalogu: {args.path}")
        # Uruchomienie generatora skanującego system plików.
        scanner_generator = scan_filesystem(args.path)
        # Przekazanie generatora do metody wstawiającej dane do bazy.
        db_engine.insert_scanner_objects(scanner_generator, source_path=args.path)
        print("Skanowanie zakończone. Dane zostały zapisane w bazie.")

    # Jeśli użytkownik wybrał komendę 'find-dups'
    elif args.command == "find-dups":
        print("Wyszukiwanie potencjalnych duplikatów...")
        # Wywołanie metody wyszukującej kandydatów na duplikaty.
        duplicates = db_engine.find_duplicate_candidates()
        # Jeśli lista duplikatów nie jest pusta.
        if duplicates:
            print(f"Znaleziono {len(duplicates)} grup potencjalnych duplikatów:")
            # Iteracja przez każdą grupę duplikatów.
            for name, size, timestamp, count in duplicates:
                # Formatowanie rozmiaru pliku do czytelnej formy (KB, MB, GB).
                size_str = f"{size / 1024 / 1024:.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
                # Wyświetlenie informacji o grupie duplikatów.
                print(f"  - Plik: '{name}', Rozmiar: {size_str}, Wystąpienia: {count}")
        else:
            # Jeśli nie znaleziono duplikatów.
            print("Nie znaleziono żadnych potencjalnych duplikatów.")

# Standardowy idiom w Pythonie: jeśli skrypt jest uruchamiany bezpośrednio,
# a nie importowany, wykonaj funkcję main().
if __name__ == "__main__":
    main()
