import os
import json
import firebase_admin
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, storage, db as rtdb

app = Flask(__name__)

# --- Config ---
RTD_URL1 = "https://scales-ofm-default-rtdb.asia-southeast1.firebasedatabase.app/"
BUCKET_NAME = "scales-ofm.firebasestorage.app"

# --- Firebase Initialization ---
service_account_json = os.environ.get("FIREBASE_SERVICE_KEY")
if not service_account_json:
    # สำหรับ Cloud Run หากไม่เจอ Key จะแจ้ง Error ชัดเจนใน Logs
    print("❌ Error: FIREBASE_SERVICE_KEY environment variable is not set.")
    raise RuntimeError("Missing FIREBASE_SERVICE_KEY")

try:
    cred = credentials.Certificate(json.loads(service_account_json))
    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": BUCKET_NAME,
            "databaseURL": RTD_URL1
        }
    )
except Exception as e:
    print(f"❌ Firebase Init Error: {e}")

db = firestore.client()
rtdb_ref = rtdb.reference("/")
bucket = storage.bucket()

@app.route("/get_api_config", methods=["GET"])
def get_api_config():
    try:
        ofm = request.args.get("ofm")
        if not ofm:
            return jsonify({"error": "Missing 'ofm' parameter"}), 400

        doc = db.collection("ofm_servers").document(ofm).get()

        if doc.exists:
            data = doc.to_dict()
            return jsonify({
                "api_base": data.get("api_base", "")
            })

        return jsonify({
           #"api_base": "https://ofmserver-default.onrender.com"
           #"api_base": "https://<ชื่อแอปของคุณ>.a.run.app" 
           "api_base": "https://freshmarket.a.run.app" 
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run จะกำหนด PORT มาให้เอง ถ้าไม่มีให้ใช้ 8080 เป็นค่าเริ่มต้น
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
