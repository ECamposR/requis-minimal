import unicodedata


def normalize_catalog_token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.strip().upper()


DECIMAL_ITEM_NAMES = {
    "CONCENTRADO SHF",
    "LIQUIDO CONCENTRADO DESODORIZADOR",
}


def classify_catalog_item_type(nombre: str) -> str | None:
    first_word = normalize_catalog_token((nombre or "").strip().split(" ", 1)[0])
    if not first_word:
        return None

    retornable_prefixes = (
        "ALF",
        "ALFOMBRA",
        "BOTELLA",
        "CABEZAL",
        "CORAZON",
        "DISPENSER",
        "EQUIPO",
        "HERRAMIENTA",
        "MOPA",
        "SOPORTE",
    )
    consumible_prefixes = (
        "BASE",
        "BIDON",
        "CONCENTRADO",
        "CONTENEDOR",
        "CUERPO",
        "DISPENSADOR",
        "DOSIS",
        "FILTRO",
        "KIT",
        "LAMPARA",
        "LIQUIDO",
        "MECHA",
        "PILAS",
        "REPUESTO",
        "SERVICIO",
        "SPRAY",
        "TAPA",
    )

    if any(first_word.startswith(prefix) for prefix in retornable_prefixes):
        return "RETORNABLE"
    if any(first_word.startswith(prefix) for prefix in consumible_prefixes):
        return "CONSUMIBLE"
    return None


def catalog_item_allows_decimal(nombre: str) -> bool:
    return normalize_catalog_token(nombre) in DECIMAL_ITEM_NAMES
