from django.contrib import admin

from .models import Contact, Message, BulkMail


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


admin.site.register(Contact, ContactAdmin)


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
        else:
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
        else:
            return ["id", "slug", "user", "sent"]

    def _to(self, obj):
        return obj.emailstr("to")

    def _cc(self, obj):
        return obj.emailstr("cc")

    def _bcc(self, obj):
        return obj.emailstr("bcc")


admin.site.register(Message, MessageAdmin)


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
        else:
            return ["id", "slug", "user", "sent"]



admin.site.register(BulkMail, BulkMailAdmin)
