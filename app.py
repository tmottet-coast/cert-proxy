from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "8923joijsdf789873k877"  # Replace with your secure API key

@app.route('/proxy', methods=['POST'])
def proxy():
    # Validate API key
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        response = requests.post(
            "https://s2s.thomsonreuters.com/api/",  # Replace with your target API
            json=data,
            cert=("/var/render/secrets/client.crt", "/var/render/secrets/client.key"),
            verify="/var/render/secrets/ca.pem"  # Or set to False for dev/testing only
        )
        return jsonify({
            "status_code": response.status_code,
            "response": response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
