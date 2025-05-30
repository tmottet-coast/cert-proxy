from flask import Flask, request, Response, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

# Load secrets from environment variables
API_KEY = os.getenv("PROXY_API_KEY")
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")
BASE_API_URL = "https://s2s.thomsonreuters.com/api"

@app.route('/proxy/<path:subpath>', methods=['POST', 'GET'])
def proxy(subpath):
    # Validate API key
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    full_url = f"{BASE_API_URL}/{subpath}"
    print(f"Forwarding {request.method} to {full_url}")

    # Extract Accept and Content-Type headers
    accept_header = request.headers.get("Accept", "application/xml")
    content_type = request.headers.get("Content-Type", "application/xml")

    headers = {
        "Accept": accept_header,
        "Content-Type": content_type
    }

    try:
        if request.method == 'POST':
            xml_payload = request.data.strip()
            print("Received XML payload:\n", xml_payload.decode(errors="replace"))

            response = requests.post(
                full_url,
                data=xml_payload,
                headers=headers,
                auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify="/etc/secrets/ca.pem"
            )
        else:  # GET request
            response = requests.get(
                full_url,
                headers=headers,
                auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify="/etc/secrets/ca.pem"
            )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "application/octet-stream")
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Only used if running locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
