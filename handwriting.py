from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create uploads folder if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def extract_text_from_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
    processed_image = cv2.GaussianBlur(image, (5, 5), 0)  # Reduce noise
    _, binary_image = cv2.threshold(processed_image, 127, 255, cv2.THRESH_BINARY)  # Binarize
    
    text = pytesseract.image_to_string(binary_image, lang='eng', config='--psm 6')  # OCR
    return text.strip()

# Function to process a PDF
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)  # Convert PDF to images
    extracted_text = ""

    for i, page in enumerate(images):
        image_path = os.path.join(UPLOAD_FOLDER, f"page_{i+1}.jpg")
        page.save(image_path, 'JPEG')

        text = extract_text_from_image(image_path)
        extracted_text += f"\n--- Page {i+1} ---\n{text}"

    return extracted_text.strip()

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)  # Save the uploaded file

    # Determine if file is PDF or image
    if file.filename.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    return jsonify({"extracted_text": extracted_text})

if __name__ == "__main__":
    app.run(debug=True)