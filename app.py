from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os
import xmltodict

app = Flask(__name__)

# Load secrets from environment variables
API_KEY = os.getenv("PROXY_API_KEY")
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")
BASE_API_URL = "https://s2s.thomsonreuters.com/api"

@app.route('/proxy/<path:subpath>', methods=['POST', 'GET'])
def proxy(subpath):
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    full_url = f"{BASE_API_URL}/{subpath}"
    print(f"Forwarding {request.method} to {full_url}")

    try:
        if request.method == 'POST':
            xml_payload = request.data.strip()
            print("Received XML payload:\n", xml_payload.decode(errors="replace"))

            response = requests.post(
                full_url,
                data=xml_payload,
                headers={
                    "Content-Type": "application/xml",
                    "Accept": "application/xml"
                },
                auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify=True
            )
        else:
            response = requests.get(
                full_url,
                headers={"Accept": "application/xml"},
                auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify=True
            )

        try:
            # Parse XML
            json_body = xmltodict.parse(response.content)

            # Try to extract the Uri field if it exists
            uri = None
            # Navigate known XML structure if matched
            root = next(iter(json_body.values()))
            if isinstance(root, dict):
                uri = root.get("Uri")

            return jsonify({
                "status_code": response.status_code,
                "url": full_url,
                "uri": uri,
                "response": json_body
            })
        except Exception as parse_error:
            print(f"Failed to parse XML: {parse_error}")
            return jsonify({
                "status_code": response.status_code,
                "url": full_url,
                "response_raw": response.text
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
