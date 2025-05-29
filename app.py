from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "8923joijsdf789873k877"  # Replace with your secure API key
BASE_API_URL = "https://s2s.thomsonreuters.com/api"

@app.route('/proxy/<path:subpath>', methods=['POST'])
def proxy(subpath):
    # Validate API key
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        full_url = f"{BASE_API_URL}/{subpath}"

        response = requests.post(
            full_url,
            json=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
            verify=True  # Use system certs (or False for sandbox testing)
        )

        # Handle cases where response is not JSON
        try:
            json_data = response.json()
        except ValueError:
            json_data = {"raw": response.text}

        return jsonify({
            "status_code": response.status_code,
            "url": full_url,
            "response": json_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
