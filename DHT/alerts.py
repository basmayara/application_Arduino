import os
import time
from urllib.parse import quote

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
CALL_USER = os.environ.get("CALLMEBOT_USER", "")

TEMP_MIN = float(os.environ.get("ALERT_TEMP_MIN", 2))
TEMP_MAX = float(os.environ.get("ALERT_TEMP_MAX", 8))
HUM_MAX = float(os.environ.get("ALERT_HUM_MAX", 80))
COOLDOWN = int(os.environ.get("ALERT_COOLDOWN", 300))

_last_alert = 0


def check_alert(temperature, humidity):
    problems = []
    if temperature > TEMP_MAX:
        problems.append(f"temperature trop haute : {temperature} C (max {TEMP_MAX})")
    if temperature < TEMP_MIN:
        problems.append(f"temperature trop basse : {temperature} C (min {TEMP_MIN})")
    if humidity > HUM_MAX:
        problems.append(f"humidite trop elevee : {humidity} % (max {HUM_MAX})")
    return problems


def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        print("Telegram: TOKEN ou CHAT_ID manquant")
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text},
            timeout=5,
        )
        print("Telegram:", r.status_code, r.text)
    except requests.RequestException as e:
        print("Erreur Telegram :", e)


def send_telegram_call(text):
    if not CALL_USER:
        print("Appel: CALLMEBOT_USER manquant")
        return
    try:
        r = requests.get(
            f"http://api.callmebot.com/start.php?user={quote(CALL_USER)}"
            f"&text={quote(text)}&lang=fr-FR-Standard-A&rpt=2",
            timeout=10,
        )
        print("Appel:", r.status_code)
    except requests.RequestException as e:
        print("Erreur appel :", e)


def notify_if_alert(temperature, humidity):
    global _last_alert
    problems = check_alert(temperature, humidity)
    print("Verification alerte:", temperature, humidity, problems)
    if not problems:
        return
    if time.time() - _last_alert < COOLDOWN:
        return
    _last_alert = time.time()

    text = "ALERTE ColdChain : " + " ; ".join(problems)
    send_telegram_message("🚨 " + text)
    send_telegram_call(text)