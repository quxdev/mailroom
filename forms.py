from django.forms import ModelForm

from .models import BulkMail


class BulkMailForm(ModelForm):
    class Meta:
        model = BulkMail
        fields = (
            "sender",
            "target",
            "cc",
            "bcc",
            "subject",
            "message",
        )
