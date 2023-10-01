# Mailroom

Mailroom is a database and frontend to AWS SES. The first app from Mailroom allows sending bulk messages in multi-mode.

## Requirements

Packages
- django>=4.1.0
- redis
- celery

Submodules
- [Qux](https://github.com/quxdev/qux/)
- [QWS](https://github.com/quxdev/qws/)

## Quick Start

1. Add the following environment variables to your .env (or wherever you set them)

    ```shell
    AWS_SES_ACCESS_KEY_ID="1234567890ABCDEF1234"
    AWS_SES_SECRET_ACCESS_KEY="1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234"
    AWS_REGION="us-east-1"
    MAIL_SENDER="noreply@qux.dev"
    ```

    `AWS REGION` is set to the region where you have verified your domain on AWS SES

2. Add "mailroom" to INSTALLED_APPS in your settings file (`settings.py` usually)

    ```python
    INSTALLED_APPS = (
        ...
        'mailroom',
    )
    ```

3. Add/update reserved sender names in your settings file (`settings.py` usually)

    ```python
    MAILROOM_RESERVED_USERNAMES = ["root", "admin", "ceo",]
    MAILROOM_SENDER_DOMAIN_NAME = ["quxdev.com", "qux.dev"]
    # Mailroom uses for the qux_content block for rendering
    # Create a block with that name if you are using your own
    # template inheritance
    MAILROOM_BASE_TEMPLATE = "_blank.html"

    # QWS - Default values for from, cc, and bcc
    MAIL_FROM = os.getenv("MAIL_SENDER", None)
    MAIL_CC = None
    MAIL_BCC = None

    # REDIS
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB = os.getenv("REDIS_DB", 0)

    # Celery
    BROKER_URL = "redis://localhost:6379"
    CELERY_RESULT_BACKEND = "redis://localhost:6379"
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_CREATE_MISSING_QUEUES = True
    ```

4. Include the mailroom URLconf in your project urls.py like this:

    ```python
    url(r'mailroom/', include('mailroom.urls'), name='mailroom'),
    ```

5. Run `python manage.py migrate mailroom` to create the mailroom models.

6. Visit http://127.0.0.1/mailroom/ to start sending bulk messages

7. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a mailroom (you'll need the Admin app enabled).
