POINT_NAME_LEN: int = 30
DESCRIPTION_LEN: int = 128
BASE_COORDINATES: tuple[float, float] = (46.347141, 48.026459)
POINT_TYPES: dict[str, str] = {
    "fishing": "Рыбная",
    "hunting": "Охотничья",
    "camping": "Туристическая база",
}
POINT_TYPE_LEN: int = 20
CUTOFF_DATE: int = 90
FORBIDDEN_ZONE_NAME_LEN: int = 30
MONTHS_UNTIL_ARCHIVE: int = 3

REPORT_TYPES: dict[str, str] = {
    "spam": "Спам",
    "illegal": "Незаконная деятельность",
    "disinformation": "Некорректная информация",
    "damage": "Ущерб окружающей среде",
    "hazard": "Опасность для безопасности",
    "poaching": "Браконьерство",
    "other": "Другое",
}

RATING: dict[int, str] = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
}
