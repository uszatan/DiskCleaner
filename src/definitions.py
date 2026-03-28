import collections

# Definicja nazwanej krotki (named tuple) przechowującej metadane zeskanowanego obiektu (pliku lub katalogu).
# Użycie namedtuple zamiast zwykłej krotki czy słownika poprawia czytelność kodu,
# ponieważ dostęp do pól odbywa się przez nazwy (np. obiekt.objName), a nie przez indeksy (np. obiekt[0]).
# Jest to również bardziej pamięciooszczędne niż słownik.
sScannerObject = collections.namedtuple(
    "sScannerObject",
    [
        "objName",              # Nazwa obiektu (pliku lub katalogu), typ: str
        "objPathId",            # Identyfikator ścieżki nadrzędnej (katalogu, w którym się znajduje), typ: int
        "objId",                # Unikalny identyfikator obiektu w ramach jednego skanowania, typ: int
        "objIsDir",             # Flaga określająca, czy obiekt jest katalogiem (1) czy plikiem (0), typ: int
        "objSize",              # Rozmiar pliku w bajtach. Dla katalogów wartość ta jest zazwyczaj 0, typ: int
        "objTimestamp",         # Czas ostatniej modyfikacji pliku jako uniksowy znacznik czasu (Unix timestamp), typ: int
        "objOtherAttributes"    # Zarezerwowane na przyszłe atrybuty (np. hash pliku, uprawnienia), obecnie nieużywane, typ: any
    ]
)
