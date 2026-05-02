from flask import Flask, request, jsonify
import logging
import requests

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

P1SMS_API_KEY = "C0okWjuQHfX7JLHB3WUUZFOGL7ymzAAP1mQodUZo5rmEZtocWOgNOlVJm1PD"

@app.route('/sms', methods=['GET', 'POST'])
def send_sms():
    # Логирование всех входящих данных
    app.logger.info("Входящий запрос от Zvonok:")
    app.logger.info("Метод: %s", request.method)
    app.logger.info("Заголовки: %s", dict(request.headers))
    app.logger.info("GET параметры: %s", request.args.to_dict())

    phone = None
    text = "Забери 25 литров! Наше приложение: http://likoilalian.vercel.app"

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        app.logger.info("JSON: %s", data)
        phone = data.get("phone") or data.get("ct_phone")
        text = data.get("text") or text
    else:
        phone = request.args.get('phone') or request.args.get('ct_phone')
        text = request.args.get('text', text)

    if not phone:
        # Ищем в любых полях
        for key, value in (request.args if request.method == 'GET' else (request.get_json(silent=True) or {})).items():
            if 'phone' in key.lower() and value:
                phone = value
                break

    if not phone:
        app.logger.error("Номер телефона не найден")
        return jsonify({"status": "error", "message": "no phone"}), 400

    # Очистка номера
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10 and phone.startswith('9'):
        phone = '7' + phone
    elif len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    elif len(phone) == 11 and phone.startswith('7'):
        pass
    else:
        app.logger.error("Неверный формат номера: %s", phone)
        return jsonify({"status": "error", "message": "invalid phone format"}), 400

    # Отправка через P1sms
    url = "https://admin.p1sms.ru/apiSms/create"
    payload = {
        "apiKey": P1SMS_API_KEY,
        "sms": [{
            "channel": "digit",
            "phone": phone,
            "text": text
        }]
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        app.logger.info("P1sms ответ: %s", resp.text)
        return jsonify({"status": "ok", "p1sms_response": resp.json()})
    except Exception as e:
        app.logger.error("Ошибка отправки SMS: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
