import csv
import datetime
import threading

from . import settings as app_settings
from celery.app import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from qux.models import QuxModel, default_null_blank


class Mailroom(QuxModel):
    SLUG_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz"

    slug = models.CharField(max_length=16, unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = "mailroom"
        abstract = True


class Contact(Mailroom):
    """
    email = username[64]@domain[255]
    """

    firstname = models.CharField(
        max_length=64, **default_null_blank, verbose_name="First Name"
    )
    lastname = models.CharField(
        max_length=64, **default_null_blank, verbose_name="Last Name"
    )
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=64)
    domain = models.CharField(max_length=255)

    class Meta:
        db_table = "mailroom_contact"

    def __str__(self):
        return str(self.email)

    def __repr__(self):
        return str(self.email)


@receiver(post_save, sender=Contact)
def set_calculated_fields(sender, instance, **kwargs):
    username, domain = instance.email.split("@")
    if instance.username != username or instance.domain != domain:
        instance.username = username
        instance.domain = domain
        instance.save()


class Message(Mailroom):
    sender = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="messages_from",
        **default_null_blank,
    )
    to = models.ManyToManyField(Contact, related_name="messages_to")
    cc = models.ManyToManyField(Contact, related_name="messages_cc")
    bcc = models.ManyToManyField(Contact, related_name="messages_bcc")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent = models.DateTimeField(**default_null_blank)
    ref_model = models.CharField(max_length=64, **default_null_blank)
    ref_slug = models.CharField(max_length=16, **default_null_blank)

    class Meta:
        db_table = "mailroom_message"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.emailstr('to')}"

    def emailstr(self, header=None):
        if header is None:
            return
        if header not in ["to", "cc", "bcc"]:
            return
        if getattr(self, header).exists():
            contact_list = [contact.email for contact in getattr(self, header).all()]
            return ",".join(contact_list)

        return

    def set_recipients(self, header, value):
        if header not in ["to", "cc", "bcc"]:
            return

        if value:
            contact_list = []
            for e in value.split(","):
                c = Contact.objects.get_or_none(email=e.lower())
                if c is None:
                    c = Contact.objects.create(user=self.user, email=e.lower())
                if c not in contact_list:
                    contact_list.append(c)
            getattr(self, header).set(contact_list)

    @classmethod
    def draft(cls, **kwargs):
        user = kwargs["user"]
        sender = kwargs["sender"].lower()

        obj = cls.objects.create(user=user)
        contact = Contact.objects.get_or_none(email=sender)
        if contact is None:
            contact = Contact.objects.create(user=user, email=sender)
        obj.sender = contact

        obj.set_recipients("to", kwargs["to"])
        obj.set_recipients("cc", kwargs["cc"])
        obj.set_recipients("bcc", kwargs["bcc"])

        obj.subject = kwargs["subject"]
        obj.message = kwargs["message"]

        return obj

    @classmethod
    def bulksend(cls):
        queryset = cls.objects.filter(is_sent=False)
        for message in queryset:
            message.send()

    def send(self):
        if isinstance(self.sent, datetime.datetime):
            return True

        packet = {
            "subject": self.subject,
            "body": self.message,
            "from_email": self.sender.email,
            "reply_to": [self.sender.email],
        }

        value = self.emailstr("to")
        if value:
            packet["to"] = [value]
        else:
            return

        value = self.emailstr("cc")
        value = [value] if value else []
        packet["cc"] = value + app_settings.MAILROOM_CC

        value = self.emailstr("bcc")
        value = [value] if value else []
        packet["bcc"] = value + app_settings.MAILROOM_BCC

        print(packet)

        # email_message = EmailMessage(**packet)
        # email_message.send(fail_silently=True)

        # This is an alternative to send email in a separate thread
        EmailThread(packet).start()


def mailroom_bulkmail_target_filepath(instance, filename):
    return f"mailroom/bulkmail/{instance.slug}/{filename}"


class BulkMail(Mailroom):
    sender = models.CharField("From", max_length=128)
    target = models.FileField(
        upload_to=mailroom_bulkmail_target_filepath,
        **default_null_blank,
        verbose_name="To",
    )
    target_count = models.IntegerField("Target Count", default=0)
    cc = models.TextField("Cc", **default_null_blank)
    bcc = models.TextField("Bcc", **default_null_blank)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent = models.DateTimeField(**default_null_blank)

    class Meta:
        db_table = "mailroom_bulkmail"

    def explode(self):
        if self.sent:
            return

        sender_email = "@".join([self.sender.lower(), "eninejobs.com"])

        contacts = []
        with open(self.target.path, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                # Get contact if email found else create
                # Do not overwrite existing contact
                email = row.get("email", None)
                contact = None

                if email:
                    contact = Contact.objects.get_or_none(email=email)
                    if contact is None:
                        contact = Contact.objects.create(
                            user=self.user,
                            email=email.lower(),
                        )

                        model_fields = ["firstname", "lastname"]
                        for k in model_fields:
                            if k in row:
                                setattr(contact, k, row[k])
                        contact.save()

                if contact and contact not in contacts:
                    contacts.append(contact)

        # Create messages
        for to in contacts:
            message_params = {
                "user": self.user,
                "sender": sender_email,
                "to": to.email,
                "cc": self.cc,
                "bcc": self.bcc,
                "subject": self.subject,
                "message": self.message.format(**to.__dict__),
            }
            message = Message.draft(**message_params)

            message.ref_model = "mailroom.bulkmail"
            message.ref_slug = self.slug
            message.save()

        self.target_count = len(contacts)
        self.save()

        queryset = Message.objects.filter(
            ref_model="mailroom.bulkmail",
            ref_slug=self.slug,
        )

        # Asynchronous (for queued)
        [task_message_send.delay(message.slug) for message in queryset]

        # Synchronous
        # [message.send() for message in queryset]

        self.sent = datetime.datetime.now()
        self.save()


class EmailThread(threading.Thread):
    def __init__(self, params):
        self.email_message = EmailMessage(**params)
        threading.Thread.__init__(self)

    def run(self):
        result = self.email_message.send()
        print(f"to:{self.email_message.to} | result:{result}")


@shared_task
def task_message_send(slug):
    message = Message.objects.get_or_none(slug=slug)
    if message:
        message.send()
        message.is_sent = True
        message.save()
