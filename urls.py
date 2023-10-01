from django.urls import path

from .views import *

app_name = "mailroom"

urlpatterns = [
    path("bulkmail/", BulkMailList.as_view(), name="bulkmail_list"),
    path("bulkmail/create/", CreateBulkMail.as_view(), name="bulkmail_create"),
]
