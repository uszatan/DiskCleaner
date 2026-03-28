import os
from typing import Generator, Dict, Tuple

# Import definicji obiektu sScannerObject z lokalnego modułu.
# To zapewnia, że wszystkie części aplikacji używają tej samej struktury danych.
from .definitions import sScannerObject

def scan_filesystem(path: str) -> Generator[sScannerObject, None, None]:
    """
    Skanuje podaną ścieżkę systemu plików i zwraca generator obiektów sScannerObject.

    Funkcja ta przechodzi przez drzewo katalogów, generując obiekty dla każdego napotkanego
    pliku i katalogu. Została zaprojektowana jako generator, aby zminimalizować zużycie pamięci
    poprzez przetwarzanie obiektów strumieniowo, zamiast ładować wszystkich do pamięci naraz.

    Args:
        path (str): Absolutna ścieżka do katalogu, który ma zostać przeskanowany.

    Yields:
        Generator[sScannerObject, None, None]: Generator zwracający obiekty sScannerObject
                                                dla każdego pliku i katalogu w skanowanej ścieżce.
    """
    # Słownik przechowujący mapowanie pełnych ścieżek katalogów na ich unikalne identyfikatory (ID).
    # Jest to kluczowe do późniejszego odtworzenia hierarchii katalogów w bazie danych.
    # Kluczem jest ścieżka (np. "/home/user/docs"), a wartością jest ID (np. 1).
    dir_map: Dict[str, int] = {path: 0}

    # Inicjalizacja liczników ID dla katalogów i plików.
    # Zaczynamy od 1, ponieważ ID 0 jest zarezerwowane dla korzenia skanowania.
    dir_id_counter = 1
    file_id_counter = 1

    # os.walk() rekurencyjnie przechodzi przez drzewo katalogów.
    # Dla każdej iteracji dostarcza:
    # - dirpath: ścieżkę do aktualnie przetwarzanego katalogu.
    # - dirnames: listę nazw podkatalogów w dirpath.
    # - filenames: listę nazw plików w dirpath.
    for dirpath, dirnames, filenames in os.walk(path):
        # Pobranie ID katalogu nadrzędnego z mapy.
        # Jest to niezbędne do powiązania plików i podkatalogów z ich "rodzicem".
        parent_dir_id = dir_map[dirpath]

        # Przetwarzanie podkatalogów znalezionych w bieżącym katalogu.
        for dirname in dirnames:
            # Tworzenie pełnej ścieżki do podkatalogu.
            full_path = os.path.join(dirpath, dirname)
            # Przypisanie nowego, unikalnego ID do tego podkatalogu.
            dir_map[full_path] = dir_id_counter
            # Zwrócenie (yield) obiektu reprezentującego ten katalog.
            # - objName: nazwa katalogu
            # - objPathId: ID katalogu nadrzędnego
            # - objId: unikalne ID tego katalogu
            # - objIsDir: 1 (prawda), bo to jest katalog
            # - objSize: 0, katalogi nie mają rozmiaru w tym kontekście
            # - objTimestamp: 0, nie przechowujemy czasu modyfikacji dla katalogów
            # - objOtherAttributes: None, nieużywane
            yield sScannerObject(dirname, parent_dir_id, dir_id_counter, 1, 0, 0, None)
            # Inkrementacja licznika ID katalogów, aby następny był unikalny.
            dir_id_counter += 1

        # Przetwarzanie plików znalezionych w bieżącym katalogu.
        for filename in filenames:
            # Tworzenie pełnej ścieżki do pliku.
            full_path = os.path.join(dirpath, filename)
            try:
                # Pobieranie metadanych pliku za pomocą os.stat().
                # Używamy bloku try-except, aby obsłużyć ewentualne błędy,
                # np. gdy plik zostanie usunięty w trakcie skanowania.
                file_stat = os.stat(full_path)
                # Pobranie czasu ostatniej modyfikacji pliku.
                # Używamy getmtime, ponieważ jest to najbardziej wiarygodny wskaźnik zmiany zawartości pliku.
                # Czas jest konwertowany na liczbę całkowitą (timestamp), co jest wydajniejsze do przechowywania i porównywania.
                mtime = int(os.path.getmtime(full_path))
            except FileNotFoundError:
                # Jeśli plik nie zostanie znaleziony (np. usunięty w trakcie), pomijamy go.
                continue

            # Zwrócenie (yield) obiektu reprezentującego ten plik.
            # - objName: nazwa pliku
            # - objPathId: ID katalogu nadrzędnego
            # - objId: unikalne ID tego pliku
            # - objIsDir: 0 (fałsz), bo to jest plik
            # - objSize: rozmiar pliku w bajtach, pobrany z file_stat
            # - objTimestamp: czas ostatniej modyfikacji jako Unix timestamp
            # - objOtherAttributes: None, nieużywane
            yield sScannerObject(filename, parent_dir_id, file_id_counter, 0, file_stat.st_size, mtime, None)
            # Inkrementacja licznika ID plików.
            file_id_counter += 1
