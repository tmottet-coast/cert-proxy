from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

API_KEY = "8923joijsdf789873k877"
BASE_API_URL = "https://s2s.thomsonreuters.com/api"

BASIC_AUTH_USER = "4481485"
BASIC_AUTH_PASS = "YMFMH5"

@app.route('/proxy/<path:subpath>', methods=['POST'])
def proxy(subpath):
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    xml_payload = request.data
    full_url = f"{BASE_API_URL}/{subpath}"

    try:
        response = requests.post(
            full_url,
            data=xml_payload,
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml"
            },
            auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
            cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
            verify=True  # Or False for testing only
        )

        return jsonify({
            "status_code": response.status_code,
            "url": full_url,
            "response": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
