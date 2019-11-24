from itsdangerous import URLSafeTimedSerializer


def get_token_serializer():
    from app import app
    ts = URLSafeTimedSerializer(app.config["EMAIL_CONFIRM_SECRET_KEY"])
    return ts
