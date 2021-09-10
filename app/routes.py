import datetime

from app.checker.check_email import MailRu, Yahoo

from app import app
from flask import jsonify, request


@app.route("/", methods=["POST"])
def if_email_exists():
    print(datetime.datetime.now(), request, flush=True)
    post_data = request.get_json()

    if post_data is None:
        return jsonify(
            status="ERROR",
            msg="POST data is missing"
        )
    email = post_data["email"]
    if email is None:
        return jsonify(
            status="ERROR",
            msg="Missing email key."
        )
    proxy = post_data["proxy"]
    if proxy is None:
        return jsonify(
            status="ERROR",
            msg="Missing proxy key."
        )
    user_agent = request.headers.get("User-Agent")
    if user_agent is None:
        return jsonify(
            status="ERROR",
            msg="Missing User-Agent header."
        )

    if user_agent != "Cron":
        return jsonify(
            status="ERROR",
            msg="Access denied."
        )
    mail_ru_domains = [
        "mail.ru",
        "list.ru",
        "inbox.ru",
        "bk.ru",
        "internet.ru"
    ]
    if email.split("@", 1)[1] in mail_ru_domains:
        return jsonify(
            email_exists=MailRu(email=email, proxy=proxy, user_agent=user_agent).check
        )
    elif "@yahoo." in email:
        return jsonify(
            email_exists=Yahoo(email=email, proxy=proxy, user_agent=user_agent).check
        )
    else:
        return jsonify(
            status="ERROR",
            msg="Invalid email address."
        )
