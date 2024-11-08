from django.core.validators import RegexValidator


class PhoneNumberRussianFormatValidator(RegexValidator):
    code = "invalid_phone_number_format"
    message = "Неверный формат номера телефона"
    regex = (
        r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?"
        r"[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
    )
