from __future__ import annotations

import re
from datetime import date

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

_NAME_PATTERN = re.compile(r"^[\w\s.'\-áéíóúÁÉÍÓÚñÑüÜ]{2,80}$", re.UNICODE)


class AppointmentForm(FlaskForm):
    client_name = StringField(
        "Client name", validators=[DataRequired(), Length(min=2, max=80)]
    )
    service_id = IntegerField(
        "Service", validators=[DataRequired(), NumberRange(min=1)]
    )
    appointment_date = StringField(
        "Date", validators=[DataRequired(), Length(min=10, max=10)]
    )

    def validate_client_name(self, field: StringField) -> None:
        if not _NAME_PATTERN.match(field.data.strip()):
            raise ValidationError("Name contains invalid characters")

    def validate_appointment_date(self, field: StringField) -> None:
        try:
            parsed = date.fromisoformat(field.data)
        except ValueError as exc:
            raise ValidationError("Date must be in YYYY-MM-DD format") from exc
        if parsed < date.today():
            raise ValidationError("Date cannot be in the past")
