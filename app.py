from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

P1SMS_API_KEY = "C0okWjuQHfX7JLHB3WUUZFOGL7ymzAAP1mQodUZo5rmEZtocWOgNOlVJm1PD"

@app.route('/sms', methods=['POST'])
def send_sms():
    # Логируем входящие данные для отладки (потом можно убрать)
    data = request.get_json(silent=True) or {}
    print("Входящий запрос от Zvonok:", data)

    # Пытаемся получить номер телефона – Zvonok обычно шлёт "phone"
    phone = data.get("phone", "")
    # Если номера нет в JSON, возможно, он в form-параметрах
    if not phone:
        phone = request.form.get("phone", "")

    # Текст сообщения: берём из запроса, если нет – стандартный
    text = data.get("text") or request.form.get("text") or "Забери 25 литров!\nНаше приложение: http://likoilalian.vercel.app"

    if not phone:
        return jsonify({"status": "error", "message": "no phone"}), 400

    # Очистка номера – оставляем только цифры
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10 and phone.startswith('9'):
        phone = '7' + phone
    elif len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    elif len(phone) == 11 and phone.startswith('7'):
        pass
    else:
        return jsonify({"status": "error", "message": "invalid phone format"}), 400

    # Отправка через P1sms
    url = "https://admin.p1sms.ru/apiSms/create"
    payload = {
        "apiKey": P1SMS_API_KEY,
        "sms": [
            {
                "channel": "digit",
                "phone": phone,
                "text": text
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        print("P1sms ответ:", resp.text)
        return jsonify({
            "status": "ok",
            "p1sms_response": resp.json()
        })
    except Exception as e:
        print("Ошибка отправки SMS:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
