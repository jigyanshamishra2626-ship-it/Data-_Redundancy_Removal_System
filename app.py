from flask import Flask, jsonify, request, render_template_string
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# Aapka MongoDB Atlas connection link
MONGO_URI = "mongodb+srv://jigyanshamishra2626_db_user:<PASSWORD>@cluster0.d07suzi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Connection timeout ko thoda flexible rakha hai
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client["Cloud_Data_Management"]  
    verified_collection = db["unique_records"]
    print("✅ MongoDB Connected! Data Redundancy Removal System Active.")
except ConnectionFailure:
    print("❌ MongoDB connection failed.")
    db = None

# ---- HTML UI Frontend ----
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Data Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; }
        .container { max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        input[type="text"], input[type="email"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #2980b9; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }
        button:hover { background-color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Cloud Data Redundancy Removal System</h2>
        <p>Identify, validate, and prevent duplicate entries in the cloud database.</p>
        <hr>
        <form action="/submit-data" method="POST">
            <label>Full Name:</label>
            <input type="text" name="name" placeholder="Enter full name..." required>
            
            <label>Email Address (Unique Key):</label>
            <input type="email" name="email" placeholder="Enter email address..." required>
            
            <label>Data Payload / Content:</label>
            <input type="text" name="payload" placeholder="Enter data content to store..." required>
            
            <button type="submit">Validate & Append to Cloud</button>
        </form>
        <br>
        <a href="/view-database"><button style="background-color: #27ae60;">View Verified Cloud Database</button></a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit-data', methods=['POST'])
def submit_data():
    if db is None:
        return jsonify({"status": "Error", "message": "Database Connection Offline"}), 500
        
    name = request.form.get('name').strip()
    email = request.form.get('email').strip().lower()
    payload = request.form.get('payload').strip()
    
    if not name or not email or not payload:
        return "<h3>❌ Validation Failed: Empty fields are not allowed.</h3><a href='/'>Go Back</a>"
        
    existing_record = verified_collection.find_one({"email": email})
    
    if existing_record:
        return f"<h3>❌ Redundancy Alert: Duplicate entry blocked! The email '{email}' already exists.</h3><a href='/'>Go Back</a>"
    
    new_record = {
        "name": name,
        "email": email,
        "data_content": payload,
        "status": "Verified & Unique"
    }
    
    verified_collection.insert_one(new_record)
    return "<h3>✅ Success: Data is unique! Successfully verified and saved to Cloud Database.</h3><a href='/'>Go Back</a>"

@app.route('/view-database')
def view_database():
    if db is None:
        return jsonify({"status": "Error", "message": "Database Offline"}), 500
        
    records = list(verified_collection.find({}, {"_id": 0}))
    return jsonify({
        "system_status": "Database is accurate and efficient (Zero Redundancy)",
        "total_unique_records": len(records),
        "verified_data": records
    })

if __name__ == '__main__':
    # Windows reload error se bachne ke liye use_reloader=False kiya hai
    app.run(debug=True, use_reloader=False, port=5000)
