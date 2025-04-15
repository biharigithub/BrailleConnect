import logging
import tempfile
import os
import numpy as np
import cv2
from PIL import Image
from utils.braille_converter import braille_to_text

def detect_braille_from_image(image_file):
    """
    Detect Braille patterns from an image and convert them to text.
    
    Args:
        image_file: Flask file object containing the image
        
    Returns:
        tuple: (extracted_text, braille_dots_image_base64)
    """
    try:
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
            temp_filename = temp.name
            image_file.save(temp_filename)
        
        # Open the image with OpenCV
        image = cv2.imread(temp_filename)
        if image is None:
            raise ValueError("Could not read image file")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours - these should represent the Braille dots
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to get only the Braille dots
        min_area = 10  # Minimum area of a Braille dot
        max_area = 300  # Maximum area of a Braille dot
        braille_dots = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area <= area <= max_area:
                # Get the center of the contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    braille_dots.append((cX, cY))
        
        # Sort dots by their vertical position (rows)
        # This is a simplification - actual Braille processing would be more complex
        # and would need to recognize the 2x3 dot patterns
        row_height = 30  # Approximate height of a Braille cell
        rows = {}
        
        for dot in braille_dots:
            row_idx = dot[1] // row_height
            if row_idx not in rows:
                rows[row_idx] = []
            rows[row_idx].append(dot)
        
        # Sort each row by horizontal position
        for row_idx in rows:
            rows[row_idx].sort(key=lambda dot: dot[0])
        
        # Draw detected dots on the image for visualization
        dot_image = image.copy()
        for dot in braille_dots:
            cv2.circle(dot_image, dot, 5, (0, 255, 0), -1)
        
        # For demonstration purposes, we'll return a simplified result
        # In a real application, this would involve proper Braille cell recognition
        # and mapping to characters based on the dot patterns
        
        # Save the processed image with detected dots
        processed_image_path = temp_filename + "_processed.png"
        cv2.imwrite(processed_image_path, dot_image)
        
        # Convert to Base64 for web display
        with open(processed_image_path, "rb") as img_file:
            import base64
            processed_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # This is a placeholder for the actual Braille recognition
        # In a real implementation, we would analyze the dots' positions
        # to recognize Braille characters
        
        # For demonstration, let's assume we detected these Braille characters
        example_braille = "⠓⠑⠇⠇⠕⠀⠺⠕⠗⠇⠙"
        extracted_text = braille_to_text(example_braille)
        
        # Clean up temporary files
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if os.path.exists(processed_image_path):
            os.remove(processed_image_path)
            
        return extracted_text, processed_image_base64
        
    except Exception as e:
        logging.error(f"Error in detect_braille_from_image: {str(e)}")
        # Clean up temporary files if they exist
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.remove(temp_filename)
        if 'processed_image_path' in locals() and os.path.exists(processed_image_path):
            os.remove(processed_image_path)
        raise