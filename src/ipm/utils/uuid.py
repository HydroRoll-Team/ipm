import uuid


def generate_uuid() -> str:
    return uuid.uuid4().hex
