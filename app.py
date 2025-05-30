from flask import Flask, request, jsonify, Response
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

API_KEY = os.getenv("PROXY_API_KEY")
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")
BASE_API_URL = "https://s2s.thomsonreuters.com/api"

@app.route('/proxy/<path:subpath>', methods=['POST', 'GET'])
def proxy(subpath):
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    query_string = request.query_string.decode()
    full_url = f"{BASE_API_URL}/{subpath}"
    if query_string:
        full_url += f"?{query_string}"

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
            return jsonify({
                "status_code": response.status_code,
                "url": full_url,
                "response": response.text
            })

        else:  # GET request
            accept_header = "application/pdf" if "reportType=pdf" in query_string else "application/xml"
            response = requests.get(
                full_url,
                headers={"Accept": accept_header},
                auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS),
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify=True
            )

            if "reportType=pdf" in query_string:
                return Response(
                    response.content,
                    status=response.status_code,
                    content_type="application/pdf"
                )
            else:
                return jsonify({
                    "status_code": response.status_code,
                    "url": full_url,
                    "response": response.text
                })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
