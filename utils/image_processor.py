import logging
import pytesseract
import tempfile
from PIL import Image
import os

def extract_text_from_image(image_file):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_file: Flask file object containing the image
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
            temp_filename = temp.name
            image_file.save(temp_filename)
        
        # Open the image with PIL
        image = Image.open(temp_filename)
        
        # Use pytesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(image)
        
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        # Clean the extracted text
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            logging.warning("No text was extracted from the image")
            return None
        
        return extracted_text
    
    except Exception as e:
        logging.error(f"Error in extract_text_from_image: {str(e)}")
        # Clean up the temporary file if it exists
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise
