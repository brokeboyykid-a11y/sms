from flask import Flask, request, jsonify
import logging
import requests
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8694030302:AAG8WacA4b_3l5UlhuUMnrGODdEzLrb-6SI"
CHANNEL_ID = "-1003739197802"

def send_telegram_notification(phone, button):
    """Отправка сообщения в Telegram-канал"""
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        logging.warning("Нет токена или ID канала – уведомление не отправлено")
        return
    text = f"📞 Звонок на номер `{phone}`\n🔘 Нажата кнопка: {button}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        logging.info("Telegram response: %s", resp.text)
    except Exception as e:
        logging.error("Ошибка отправки в Telegram: %s", str(e))

@app.route('/sms', methods=['GET', 'POST'])
def sms_handler():
    app.logger.info("=== Входящий запрос ===")
    app.logger.info("Метод: %s", request.method)
    app.logger.info("Параметры URL: %s", request.args.to_dict())

    phone = request.args.get('phone')
    button = request.args.get('button', '0')

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        phone = phone or data.get('phone') or data.get('ct_phone')
        button = button or data.get('button') or data.get('ct_button_num', '0')

    # Игнорируем всё, кроме нажатия "1"
    if button != '1':
        app.logger.info("Кнопка не равна 1 (значение: %s), игнорируем.", button)
        return jsonify({"status": "ignored", "reason": "button not 1"}), 200

    if not phone:
        app.logger.error("Номер телефона отсутствует")
        return jsonify({"status": "error", "message": "no phone"}), 400

    # Очищаем номер (на случай, если нужно только логировать)
    phone_clean = ''.join(filter(str.isdigit, phone))
    # Можно не форматировать, но для красоты оставим
    if len(phone_clean) == 10 and phone_clean.startswith('9'):
        phone_clean = '7' + phone_clean
    elif len(phone_clean) == 11 and phone_clean.startswith('8'):
        phone_clean = '7' + phone_clean[1:]

    # Отправляем уведомление в Telegram
    send_telegram_notification(phone_clean, button)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
