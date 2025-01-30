from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path
import cv2
import os
import easyocr

app = Flask(__name__)
CORS(app)

# Initialize EasyOCR with correct parameters
try:
    reader = easyocr.Reader(
        ['en'], 
        recog_network='english_g2',  # Verified working model
        gpu=False,
        model_storage_directory='model_storage',
        download_enabled=True
    )
    print("EasyOCR initialized successfully")
except Exception as e:
    print(f"Error initializing EasyOCR: {str(e)}")
    raise

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def preprocess_image(image_path):
    """Simplified preprocessing for reliability"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def extract_text(image_path):
    try:
        processed_img = preprocess_image(image_path)
        results = reader.readtext(
            processed_img,
            detail=0,
            paragraph=True,
            batch_size=5
        )
        return "\n".join(results)
    except Exception as e:
        return f"OCR Error: {str(e)}"

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    
    # Handle PDF files
    if file.filename.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
        full_text = ""
        for i, image in enumerate(images):
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"page_{i+1}.jpg")
            image.save(image_path, 'JPEG')
            full_text += extract_text(image_path) + "\n"
        extracted_text = full_text
    else:
        extracted_text = extract_text(file_path)

    return jsonify({"extracted_text": extracted_text})

if __name__ == "__main__":
    app.run(debug=True)
