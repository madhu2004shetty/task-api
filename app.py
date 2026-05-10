# app.py - Main Flask Application
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)

# ─── JWT Configuration ───────────────────────────────────────────────
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

# ─── In-Memory "Database" ────────────────────────────────────────────

USERS = {
    "admin": "password123"   # username: password
}

tasks = []          # List to store tasks
task_id_counter = 1 # Auto-increment ID for tasks


# ─── ENDPOINT 1: GET / ─────────────────────────────────────────────
# Root endpoint - shows API info
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Task Management API",
        "version": "1.0",
        "endpoints": {
            "POST /login": "Get JWT token",
            "GET /tasks": "List tasks (requires token)",
            "POST /tasks": "Create task (requires token)",
            "DELETE /tasks/<id>": "Delete task (requires token)"
        }
    }), 200


# ─── ENDPOINT 2: POST /login ─────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()  # Read JSON body from request

    username = data.get("username")
    password = data.get("password")

    # Check if user exists and password matches
    if username not in USERS or USERS[username] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create a JWT token with the username as identity
    token = create_access_token(identity=username)
    return jsonify({"access_token": token}), 200


# ─── ENDPOINT 2: GET /tasks ──────────────────────────────────────────
# Protected route 
# Header format: Authorization: Bearer <token>
@app.route("/tasks", methods=["GET"])
@jwt_required()  # This decorator blocks requests without a valid token
def get_tasks():
    current_user = get_jwt_identity()  # Extract username from token
    return jsonify({"user": current_user, "tasks": tasks}), 200


# ─── ENDPOINT 3: POST /tasks ─────────────────────────────────────────
# Protected route - add a new task
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    global task_id_counter
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    task = {
        "id": task_id_counter,
        "title": data["title"],
        "done": False
    }
    tasks.append(task)
    task_id_counter += 1

    return jsonify(task), 201  # 201 = Created


# ─── ENDPOINT 4: DELETE /tasks/<id> ──────────────────────────────────
# Protected route - delete a task by ID
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    global tasks
    original_count = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]

    if len(tasks) == original_count:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": f"Task {task_id} deleted"}), 200


# ─── Run the app ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
