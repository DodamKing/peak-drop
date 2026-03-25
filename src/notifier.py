import requests


def send_discord(webhook_url: str, message: str) -> bool:
    """디스코드 웹훅으로 텍스트 메시지를 전송한다."""
    payload = {"content": message}
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()
    return True


def send_discord_embed(webhook_url: str, embed: dict) -> bool:
    """디스코드 웹훅으로 Embed 메시지를 전송한다."""
    payload = {"embeds": [embed]}
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()
    return True
