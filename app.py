from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

API_KEY = "your-api-key-here"  # Replace with secure method in production

@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST'])
def proxy(endpoint):
    # Verify API key
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # Build target URL
    target_url = f"https://s2s.thomsonreuters.com/api/{endpoint}"
    
    # Common headers to forward
    forward_headers = {
        "Accept": request.headers.get("Accept", "application/xml"),
        "Content-Type": request.headers.get("Content-Type", "application/xml"),
    }
    
    # Optional: forward Basic Auth header if present
    if "Authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["Authorization"]

    # Handle GET
    if request.method == 'GET':
        try:
            response = requests.get(
                target_url,
                headers=forward_headers,
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

    # Handle POST
    elif request.method == 'POST':
        try:
            response = requests.post(
                target_url,
                data=request.data,
                headers=forward_headers,
                cert=("/etc/secrets/client.crt", "/etc/secrets/client.key"),
                verify="/etc/secrets/ca.pem"
            )
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get("Content-Type", "application/xml")
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Unsupported method"}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
