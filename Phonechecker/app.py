from flask import Flask, render_template, request
import phonenumbers
from phonenumbers import geocoder, carrier
import requests

app = Flask(__name__)

API_KEY = "46261815a5087dfdb0ec54abec7bae78"  # ✅ Replace with your actual API key

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        result = {"name": name, "phone": phone}

        # Offline lookup with phonenumbers
        try:
            number = phonenumbers.parse(phone)
            result["offline"] = {
                "location": geocoder.description_for_number(number, "en"),
                "carrier": carrier.name_for_number(number, "en"),
                "valid": phonenumbers.is_valid_number(number)
            }
        except Exception as e:
            result["offline_error"] = f"Offline lookup failed: {e}"

        # Online lookup with NumVerify API
        try:
            url = "http://apilayer.net/api/validate"
            params = {
                "access_key": API_KEY,
                "number": phone,
                "country_code": "",
                "format": 1
            }
            response = requests.get(url, params=params)
            data = response.json()
            if data.get("valid"):
                result["online"] = {
                    "country": data.get("country_name"),
                    "location": data.get("location"),
                    "carrier": data.get("carrier"),
                    "line_type": data.get("line_type")
                }
            else:
                result["online_error"] = "Invalid number (via API)"
        except Exception as e:
            result["online_error"] = f"API error: {e}"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
