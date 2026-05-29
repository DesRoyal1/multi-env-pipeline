from flask import Flask, jsonify, request

app = Flask(__name__)

items = []

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({"items": items})

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify({"message": "item created", "item": data}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
