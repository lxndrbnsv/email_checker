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
            msg="post data is missing"
        )
    try:
        email = post_data["email"]
        if email is None:
            return jsonify(
                status="ERROR",
                msg="email is missing"
            )
        elif "@" not in email:
            return jsonify(
                status="ERROR",
                msg="invalid email address"
            )
    except KeyError:
        return jsonify(
            status="ERROR",
            msg="email key is missing"
        )
    try:
        username = post_data["username"]
        if username is None:
            return jsonify(
                status="ERROR",
                msg="username is missing"
            )
    except KeyError:
        return jsonify(
            status="ERROR",
            msg="username key is missing"
        )
    try:
        password = post_data["password"]
        if password is None:
            return jsonify(
                status="ERROR",
                msg="password is missing"
            )
    except KeyError:
        return jsonify(
            status="ERROR",
            msg="password key is missing"
        )
    try:
        proxy = post_data["proxy"]
        if proxy is None:
            return jsonify(
                status="ERROR",
                msg="proxy is missing"
            )
    except KeyError:
        return jsonify(
            status="ERROR",
            msg="proxy key is missing"
        )
    user_agent = request.headers.get("User-Agent")
    if user_agent is None:
        return jsonify(
            status="ERROR",
            msg="user-agent header is missing"
        )

    if user_agent != "Cron":
        return jsonify(
            status="ERROR",
            msg="access denied"
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
            email_exists=MailRu(
                email=email,
                proxy=proxy,
                user_agent=user_agent,
                username=username,
                password=password
            ).check
        )
    elif "@yahoo." in email:
        return jsonify(
            email_exists=Yahoo(
                email=email,
                proxy=proxy,
                user_agent=user_agent,
                username=username,
                password=password
            ).check
        )
    else:
        return jsonify(
            status="ERROR",
            msg="invalid email address"
        )
