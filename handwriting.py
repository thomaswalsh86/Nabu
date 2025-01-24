from pdf2image import convert_from_path
import cv2
import pytesseract
import re

pdf_path = 'place_holder'
regEx = re.search(r'.*\.pdf$', pdf_path, re.IGNORECASE)
if regEx is None:
    image = cv2.imread(pdf_path, cv2.IMREAD_GRAYSCALE)
    if image is not None:
        processed_image = cv2.GaussianBlur(image, (5, 5), 0)
        _, binary_image = cv2.threshold(processed_image, 127, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(binary_image, lang='eng', config='--psm 6')

        print("--- Text Extracted from Image ---")
        print(text)
else:   
    images = convert_from_path(pdf_path, dpi=300) 

    for i, page in enumerate(images):
        image_path=f'page_{i+1}.jpg'
        page.save(image_path, 'JPEG')

        image = cv2.imerad(image_path, cv2.IMREAD_GRAYSCALE)
        if image is not None: 
            processed_image = cv2.GaussianBlur(binary_image, (5, 5), 0)#reduces noise
            _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(binary_image, lang='eng', config='--psm 6')

            print(f"--- Text from Page {i+1} ---")
            print(text)
        else:
            print(f"Error: Unable to read image for page {i+1}.")