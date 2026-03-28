import os
import sqlite3
from typing import List, Generator, Tuple
import time

# Import definicji sScannerObject, aby zapewnić spójność typów danych.
from .definitions import sScannerObject

class DatabaseEngine:
    """
    Główna klasa do zarządzania bazą danych SQLite.
    Odpowiada za tworzenie schematu, importowanie danych ze skanera
    oraz dostarczanie zapytań do analizy danych (np. wyszukiwanie duplikatów).
    Klasa została zaprojektowana tak, aby hermetyzować wszystkie operacje na bazie danych.
    """

    def __init__(self, db_path: str):
        """
        Inicjalizuje silnik bazy danych.

        Args:
            db_path (str): Ścieżka do pliku bazy danych SQLite.
        """
        # Przechowuje ścieżkę do pliku bazy danych.
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        Zwraca obiekt połączenia z bazą danych.
        Prywatna metoda pomocnicza używana przez inne metody tej klasy.
        """
        # Nawiązuje połączenie z plikiem bazy danych określonym w konstruktorze.
        return sqlite3.connect(self.db_path)

    def create_schema(self):
        """
        Tworzy schemat bazy danych, jeśli nie istnieje.
        Schemat obejmuje tabelę 'scanned_objects' do przechowywania metadanych plików
        i katalogów oraz tabelę 'import_log' do śledzenia historii importów.
        """
        # Użycie 'with' gwarantuje, że połączenie zostanie automatycznie zamknięte,
        # nawet jeśli wystąpi błąd. To najlepsza praktyka w Pythonie.
        with self._get_connection() as conn:
            # Tworzenie obiektu kursora, który pozwala na wykonywanie poleceń SQL.
            cursor = conn.cursor()
            # Polecenie SQL do utworzenia tabeli 'scanned_objects'.
            # Używamy 'IF NOT EXISTS', aby uniknąć błędów przy ponownym uruchomieniu.
            # Typy danych zostały zoptymalizowane:
            # - INTEGER dla ID, flag, rozmiaru i timestampu (wydajniejsze niż TEXT).
            # - TEXT dla nazw, które są ciągami znaków.
            # - NOT NULL zapewnia integralność danych.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scanned_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    objName TEXT NOT NULL,
                    objPathId INTEGER NOT NULL,
                    objId INTEGER NOT NULL,
                    objIsDir INTEGER NOT NULL,
                    objSize INTEGER NOT NULL,
                    objTimestamp INTEGER NOT NULL,
                    objOtherAttributes TEXT,
                    importId INTEGER NOT NULL
                )
            """)
            # Polecenie SQL do utworzenia tabeli 'import_log'.
            # Ta tabela będzie przechowywać informacje o każdym imporcie (sesji skanowania).
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS import_log (
                    importId INTEGER PRIMARY KEY,
                    importTimestamp INTEGER NOT NULL,
                    sourcePath TEXT NOT NULL
                )
            """)
            # Zatwierdzenie transakcji, co zapisuje zmiany w bazie danych.
            conn.commit()

    def reset_database(self):
        """
        Całkowicie resetuje bazę danych.
        Usuwa istniejące tabele ('scanned_objects', 'import_log') i tworzy je od nowa.
        Funkcja ta jest przeznaczona do użytku deweloperskiego, aby umożliwić
        szybkie "czyszczenie" bazy danych przed ponownym testowaniem.
        """
        # Użycie 'with' zapewnia bezpieczne zarządzanie połączeniem.
        with self._get_connection() as conn:
            # Utworzenie kursora do wykonywania operacji SQL.
            cursor = conn.cursor()
            # Informacja dla użytkownika o rozpoczęciu procesu resetowania.
            print("Rozpoczynanie resetowania bazy danych...")
            # Polecenie SQL do usunięcia tabeli 'scanned_objects', jeśli istnieje.
            # 'DROP TABLE' trwale usuwa tabelę i wszystkie jej dane.
            cursor.execute("DROP TABLE IF EXISTS scanned_objects")
            print("- Tabela 'scanned_objects' została usunięta.")
            # Polecenie SQL do usunięcia tabeli 'import_log', jeśli istnieje.
            cursor.execute("DROP TABLE IF EXISTS import_log")
            print("- Tabela 'import_log' została usunięta.")
            # Zatwierdzenie operacji usunięcia tabel.
            conn.commit()
            # Po usunięciu starych tabel, wywołujemy metodę create_schema(),
            # aby odtworzyć strukturę bazy danych od zera.
            print("Odtwarzanie schematu bazy danych...")
            self.create_schema()
            print("Resetowanie bazy danych zakończone pomyślnie.")


    def get_new_import_id(self, cursor: sqlite3.Cursor, source_path: str) -> int:
        """
        Generuje nowy, unikalny identyfikator dla sesji importu i zapisuje go w logu.

        Args:
            cursor (sqlite3.Cursor): Kursor bazy danych do wykonania operacji.
            source_path (str): Ścieżka źródłowa skanowania, która będzie zapisana w logu.

        Returns:
            int: Nowy, unikalny identyfikator importu.
        """
        # Pobranie aktualnego czasu jako uniksowy timestamp.
        import_timestamp = int(time.time())
        # Wstawienie nowego rekordu do tabeli logów.
        # Używamy NULL dla importId, ponieważ jest to klucz główny, który automatycznie się inkrementuje.
        cursor.execute("INSERT INTO import_log (importTimestamp, sourcePath) VALUES (?, ?)", (import_timestamp, source_path))
        # Pobranie ostatnio wstawionego ID, które jest naszym nowym ID importu.
        return cursor.lastrowid

    def insert_scanner_objects(self, scanner_objects: Generator[sScannerObject, None, None], source_path: str):
        """
        Wstawia obiekty ze skanera do bazy danych w ramach jednej transakcji.

        Args:
            scanner_objects (Generator[sScannerObject, None, None]): Generator obiektów sScannerObject.
            source_path (str): Ścieżka źródłowa skanowania.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Pobranie nowego ID dla bieżącej sesji importu.
            import_id = self.get_new_import_id(cursor, source_path)
            # Definicja zapytania SQL do wstawiania danych.
            # Używamy znaków zapytania (?) jako placeholderów, co chroni przed atakami SQL Injection.
            insert_query = """
                INSERT INTO scanned_objects (objName, objPathId, objId, objIsDir, objSize, objTimestamp, objOtherAttributes, importId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Przygotowanie generatora danych do wstawienia.
            # Każdy obiekt sScannerObject jest przekształcany w krotkę pasującą do zapytania SQL.
            data_generator = (
                (
                    obj.objName, obj.objPathId, obj.objId, obj.objIsDir,
                    obj.objSize, obj.objTimestamp, obj.objOtherAttributes, import_id
                )
                for obj in scanner_objects
            )
            # Użycie executemany() do masowego wstawiania danych.
            # Jest to znacznie wydajniejsze niż wykonywanie zapytań w pętli,
            # ponieważ minimalizuje liczbę operacji I/O na bazie danych.
            cursor.executemany(insert_query, data_generator)
            # Zatwierdzenie transakcji.
            conn.commit()

    def find_duplicate_candidates(self) -> List[Tuple[str, int, int, int]]:
        """
        Znajduje potencjalne duplikaty plików na podstawie nazwy, rozmiaru i znacznika czasu.

        Returns:
            List[Tuple[str, int, int, int]]: Lista krotek, gdzie każda krotka zawiera:
                                             - nazwę pliku (objName)
                                             - rozmiar pliku (objSize)
                                             - znacznik czasu (objTimestamp)
                                             - liczbę wystąpień (count)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Zapytanie SQL do wyszukiwania kandydatów na duplikaty.
            # - Filtrujemy tylko pliki (objIsDir = 0).
            # - Grupujemy je według nazwy, rozmiaru i znacznika czasu.
            # - Używamy klauzuli HAVING, aby zwrócić tylko te grupy, które mają więcej niż jednego członka (potencjalne duplikaty).
            query = """
                SELECT objName, objSize, objTimestamp, COUNT(*)
                FROM scanned_objects
                WHERE objIsDir = 0
                GROUP BY objName, objSize, objTimestamp
                HAVING COUNT(*) > 1
            """
            cursor.execute(query)
            # Zwraca wszystkie pasujące wiersze jako listę krotek.
            return cursor.fetchall()

    def get_full_path(self, obj_id: int, import_id: int) -> str:
        """
        Odtwarza pełną ścieżkę dla danego obiektu (pliku lub katalogu) na podstawie jego ID i ID importu.

        Args:
            obj_id (int): ID obiektu (pliku lub katalogu).
            import_id (int): ID importu, w ramach którego obiekt został zeskanowany.

        Returns:
            str: Zrekonstruowana, pełna ścieżka do obiektu.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Rekurencyjne zapytanie SQL (Common Table Expression - CTE) do odtworzenia ścieżki.
            # - Zaczynamy od obiektu o zadanym obj_id i import_id.
            # - Następnie rekurencyjnie dołączamy jego rodziców (katalogi nadrzędne),
            #   aż dojdziemy do korzenia (gdzie objPathId = 0).
            # - Dodajemy kolumnę 'level', aby móc posortować części ścieżki od korzenia do pliku.
            query = """
                WITH RECURSIVE path_parts(id, name, parent_id, level) AS (
                    SELECT objId, objName, objPathId, 0
                    FROM scanned_objects
                    WHERE objId = ? AND importId = ?
                    UNION ALL
                    SELECT o.objId, o.objName, o.objPathId, pp.level + 1
                    FROM scanned_objects o
                    JOIN path_parts pp ON o.objId = pp.parent_id AND o.importId = ?
                )
                SELECT name FROM path_parts ORDER BY level DESC;
            """
            # Wykonanie zapytania z podanymi parametrami.
            cursor.execute(query, (obj_id, import_id, import_id))
            # Pobranie wszystkich części ścieżki.
            parts = [row[0] for row in cursor.fetchall()]

            # Pobranie ścieżki źródłowej dla danego importu, aby uzyskać ścieżkę bezwzględną.
            cursor.execute("SELECT sourcePath FROM import_log WHERE importId = ?", (import_id,))
            source_path_row = cursor.fetchone()
            
            if source_path_row:
                return os.path.join(source_path_row[0], *parts)
            return os.path.join(*parts)
