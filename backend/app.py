from flask import Flask, request, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create dataset folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check if the file is a CSV
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==============================
# 📤 Upload Route
# ==============================
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return jsonify({"message": f"File '{filename}' uploaded successfully."}), 200
    else:
        return jsonify({"error": "Invalid file type. Only CSV files allowed."}), 400

# ==============================
# 🔮 Predict Route (Dummy for Now)
# ==============================
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    product = data.get("product")
    region = data.get("region")
    date = data.get("date")  # currently unused, but included for future logic

    # Load CSV
    try:
        df = pd.read_csv('dataset/kirana_sales_data.csv')
    except Exception as e:
        return jsonify({"error": f"Could not load dataset: {str(e)}"}), 500

    # Normalize column names (strip spaces, capitalize first letters)
    df.columns = [col.strip().capitalize() for col in df.columns]

    # Validate required columns
    expected_cols = {"Product", "Region", "Quantity"}
    if not expected_cols.issubset(set(df.columns)):
        return jsonify({"error": f"Missing columns in dataset. Required: {expected_cols}"}), 400

    # Filter data
    filtered = df[(df["Product"] == product) & (df["Region"] == region)]

    if filtered.empty:
        return jsonify({"forecast": f"No data found for product '{product}' in region '{region}'."}), 404

    # Basic prediction: average quantity
    avg_quantity = filtered["Quantity"].mean()
    forecast_msg = f"Estimated average sales for {product} in {region} is {avg_quantity:.2f} units."

    return jsonify({"forecast": forecast_msg})

# ==============================
# 🏠 Root route (optional)
# ==============================
@app.route('/')
def home():
    return "🎯 Backend is running. Try /upload or /predict using POST in Postman."


if __name__ == '__main__':
    app.run(debug=True)
