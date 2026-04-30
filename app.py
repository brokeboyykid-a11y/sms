from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

P1SMS_API_KEY = "C0okWjuQHfX7JLHB3WUUZFOGL7ymzAAP1mQodUZo5rmEZtocWOgNOlVJm1PD"

@app.route('/sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "no data"}), 400

    phone = data.get("phone", "")
    text = data.get("text", "Спасибо за обращение!")

    # Очистка номера
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10 and phone.startswith('9'):
        phone = '7' + phone
    elif len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    elif len(phone) == 11 and phone.startswith('7'):
        pass
    else:
        return jsonify({"status": "error", "message": "invalid phone format"}), 400

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
        response = requests.post(url, json=payload, timeout=10)
        print("P1sms response:", response.text)
        return jsonify({
            "status": "ok",
            "p1sms_response": response.json()
        })
    except Exception as e:
        print("Error sending SMS:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
