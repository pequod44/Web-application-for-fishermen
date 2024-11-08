USERNAME_LEN: int = 30
FIRST_NAME_LEN: int = 30
LAST_NAME_LEN: int = 30
PATRONYMIC_LEN: int = 30
EMAIL_LEN: int = 30
PHONE_NUMBER_LEN: int = 30
MEMBERSHIP_NUM_LEN: int = 10

MEMBERSHIP_STATUS: dict[str, str] = {
    "pending": "Отправлено на рассмотрение",
    "approved": "Данные подтверждены, требуется оплата",
    "paid": "Подтвержденный",
    "expired": "Действие членского билета истекло",
}
TICKET_VALIDITY_DURATION_DAY: int = 365
