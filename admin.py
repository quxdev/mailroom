from django.contrib import admin

from .models import Contact, Message, BulkMail


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "slug",
        "user",
        "email",
        "firstname",
        "lastname",
        "username",
        "domain",
    )
    readonly_fields = (
        "id",
        "user",
        "slug",
        "username",
        "domain",
    )
    list_display = fields


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "slug",
        "user",
        "sender",
        "_to",
        "_cc",
        "_bcc",
        "subject",
        "sent",
    )
    list_editable = ()
    ordering = ("id",)

    def get_fields(self, request, obj=None):
        if obj:
            return [
                "id",
                "slug",
                "user",
                "sender",
                "_to",
                "_cc",
                "_bcc",
                "subject",
                "message",
                "sent",
            ]

        return [
            "id",
            "slug",
            "user",
            "sender",
            "to",
            "cc",
            "bcc",
            "subject",
            "message",
            "sent",
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.get_fields(request, obj)

        return ["id", "slug", "user", "sent"]

    @staticmethod
    def _to(obj):
        return obj.emailstr("to")

    @staticmethod
    def _cc(obj):
        return obj.emailstr("cc")

    @staticmethod
    def _bcc(obj):
        return obj.emailstr("bcc")


@admin.register(BulkMail)
class BulkMailAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "slug",
        "user",
        "sender",
        "target",
        "cc",
        "bcc",
        "subject",
        "sent",
    )
    list_display = (
        "id",
        "slug",
        "user",
        "sender",
        "target_count",
        "subject",
        "sent",
    )
    list_editable = ()
    ordering = ("-id",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.fields

        return ["id", "slug", "user", "sent"]
