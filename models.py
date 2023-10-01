import csv
import datetime

from celery import shared_task
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from qux.models import CoreModel, default_null_blank
from qws.qses.mail import AWSEmail


class Mailroom(CoreModel):
    SLUG_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz"

    slug = models.CharField(max_length=16, unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = "mailroom"
        abstract = True


# TO DO
# Store every from, to, cc, and bcc as ManyToMany to a contact model


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
        return self.email

    def __repr__(self):
        return self.email


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
            return ",".join(
                [contact.email for contact in getattr(self, header).all() if contact]
            )
        else:
            return

    @classmethod
    def draft(cls, user, sender, to, cc, bcc, subject, message):
        obj = cls.objects.create(
            user=user
        )
        contact = Contact.objects.get_or_none(email=sender.lower())
        if contact is None:
            contact = Contact.objects.create(
                user=user,
                email=sender.lower()
            )
        obj.sender = contact

        if to:
            clist = []
            for e in to.split(","):
                c = Contact.objects.get_or_none(email=e.lower())
                if c is None:
                    c = Contact.objects.create(user=user, email=e.lower())
                if c not in clist:
                    clist.append(c)
            obj.to.set(clist)

        if cc:
            clist = []
            for e in cc.split(","):
                c = Contact.objects.get_or_none(email=e.lower())
                if c is None:
                    c = Contact.objects.create(user=user, email=e.lower())
                if c not in clist:
                    clist.append(c)
            obj.cc.set(clist)

        if bcc:
            clist = []
            for e in bcc.split(","):
                c = Contact.objects.get_or_none(email=e.lower())
                if c is None:
                    c = Contact.objects.create(user=user, email=e.lower())
                if c not in clist:
                    clist.append(c)
            obj.bcc.set(clist)

        obj.subject = subject
        obj.message = message

        return obj

    @classmethod
    def bulksend(cls):
        queryset = cls.objects.filter(is_sent=False)
        for message in queryset:
            message.send()

    def send(self):
        if isinstance(self.sent, datetime.datetime):
            return True

        service = AWSEmail()
        service.sender = self.sender.email
        service.to = self.emailstr("to")
        service.cc = self.emailstr("cc")
        service.bcc = self.emailstr("bcc")
        service.subject = self.subject
        service.message = self.message

        _, response = service.send()

        self.is_sent = response["ResponseMetadata"]["HTTPStatusCode"] == 200
        self.save()

        return self.is_sent


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
                if email:
                    contact = Contact.objects.get_or_none(email=email)
                    if contact is None:
                        contact = Contact.objects.create(
                            user=self.user,
                            email=email.lower(),
                        )
                        model_fields = ["firstname", "lastname"]
                        [setattr(contact, k, row[k]) for k in model_fields if k in row]
                        contact.save()
                if contact not in contacts:
                    contacts.append(contact)

        # Create messages
        for to in contacts:
            message = Message.draft(
                user=self.user,
                sender=sender_email,
                to=to.email,
                cc=self.cc,
                bcc=self.bcc,
                subject=self.subject,
                message=self.message.format(**to.__dict__),
            )

            message.ref_model = "mailroom.bulkmail"
            message.ref_slug = self.slug
            message.save()

        self.target_count = len(contacts)
        self.save()

        queryset = Message.objects.filter(
            ref_model="mailroom.bulkmail",
            ref_slug=self.slug,
        )
        [task_message_send.delay(message.slug) for message in queryset]

        self.sent = datetime.datetime.now()
        self.save()


@shared_task
def task_message_send(slug):
    message = Message.objects.get_or_none(slug=slug)
    if message:
        message.send()
