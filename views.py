import datetime

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic import TemplateView

from .forms import BulkMailForm
from .models import BulkMail


class BulkMailList(UserPassesTestMixin, ListView):
    template_name = "mailroom/bulkmail/bulkmail_list.html"
    model = BulkMail

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect("home")

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = BulkMail.objects.all()
        else:
            queryset = BulkMail.objects.filter(user=self.request.user)
        return queryset


class CreateBulkMail(UserPassesTestMixin, TemplateView):
    template_name = "mailroom/bulkmail/bulkmail_create.html"
    form = BulkMailForm
    extra_context = {
        "default_sender": "noreply",
    }

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect("home")

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user

            files = request.FILES
            if "target" in files:
                obj.target = files["target"]
            obj.save()

            obj.explode()

            return redirect("mailroom:bulkmail_list")

        if settings.DEBUG and form.errors:
            print(form.errors)

        return redirect("mailroom:bulkmail_create")
