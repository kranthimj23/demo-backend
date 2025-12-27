from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

# Configuration from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'http://demo-database:8080')
APP_NAME = os.getenv('APP_NAME', 'Demo Backend')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

# In-memory data store (simulating database)
users_store = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "user"},
    {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "role": "user"}
]

items_store = [
    {"id": 1, "name": "Product A", "price": 29.99, "category": "electronics"},
    {"id": 2, "name": "Product B", "price": 49.99, "category": "clothing"},
    {"id": 3, "name": "Product C", "price": 19.99, "category": "books"}
]

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "demo-backend",
        "environment": ENVIRONMENT
    })

@app.route('/ready')
def ready():
    """Readiness check endpoint"""
    return jsonify({
        "status": "ready",
        "service": "demo-backend"
    })

@app.route('/db/status')
def db_status():
    """Check database connection status"""
    try:
        response = requests.get(f"{DATABASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "connected",
                "database_url": DATABASE_URL
            })
    except Exception as e:
        return jsonify({
            "status": "disconnected",
            "error": str(e)
        }), 503
    
    return jsonify({"status": "unknown"}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify({
        "users": users_store,
        "count": len(users_store),
        "source": "demo-backend"
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = next((u for u in users_store if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    new_id = max(u['id'] for u in users_store) + 1 if users_store else 1
    new_user = {
        "id": new_id,
        "name": data.get('name', 'Unknown'),
        "email": data.get('email', ''),
        "role": data.get('role', 'user')
    }
    users_store.append(new_user)
    return jsonify(new_user), 201

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items"""
    return jsonify({
        "items": items_store,
        "count": len(items_store),
        "source": "demo-backend"
    })

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item by ID"""
    item = next((i for i in items_store if i['id'] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items', methods=['POST'])
def create_item():
    """Create a new item"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    new_id = max(i['id'] for i in items_store) + 1 if items_store else 1
    new_item = {
        "id": new_id,
        "name": data.get('name', 'Unknown'),
        "price": data.get('price', 0.0),
        "category": data.get('category', 'general')
    }
    items_store.append(new_item)
    return jsonify(new_item), 201

@app.route('/api/db/query', methods=['POST'])
def db_query():
    """Proxy database queries to the database service"""
    try:
        data = request.get_json() or {}
        response = requests.post(
            f"{DATABASE_URL}/query",
            json=data,
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/write')
def write():
    """Legacy endpoint for compatibility"""
    return jsonify({"msg": "Data written to Demo-Backend"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
