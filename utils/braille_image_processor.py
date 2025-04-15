import logging
import tempfile
import os
import numpy as np
import cv2
import base64
from PIL import Image
from utils.braille_converter import braille_to_text

# Standard Braille pattern (2x3 grid)
# Each position is numbered:
# 1 4
# 2 5
# 3 6

def detect_braille_from_image(image_file):
    """
    Detect Braille patterns from an image and convert them to text.
    
    Args:
        image_file: Flask file object containing the image
        
    Returns:
        tuple: (extracted_text, braille_dots_image_base64)
    """
    temp_filename = None
    processed_image_path = None
    
    try:
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
            temp_filename = temp.name
            image_file.save(temp_filename)
        
        # Open the image with OpenCV
        image = cv2.imread(temp_filename)
        if image is None:
            raise ValueError("Could not read image file")
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Resize if the image is too large
        max_dimension = 1200
        if height > max_dimension or width > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, None, fx=scale, fy=scale)
            height, width = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding to get binary image
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours - these should represent the Braille dots
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape to get only the Braille dots
        min_area = 5  # Minimum area of a Braille dot
        max_area = 500  # Maximum area of a Braille dot
        circularity_threshold = 0.7  # Threshold for circularity (1 is perfect circle)
        braille_dots = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area <= area <= max_area:
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity >= circularity_threshold:
                        # Get the center of the contour
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            braille_dots.append((cX, cY))
        
        # Draw detected dots on the image for visualization
        dot_image = image.copy()
        for dot in braille_dots:
            cv2.circle(dot_image, dot, 5, (0, 255, 0), -1)
        
        # Group dots into Braille cells
        # First, estimate the average distance between dots
        if len(braille_dots) < 2:
            raise ValueError("Not enough Braille dots detected")
        
        # Calculate the distances between each pair of dots
        distances = []
        for i in range(len(braille_dots)):
            for j in range(i+1, len(braille_dots)):
                dist = np.sqrt((braille_dots[i][0] - braille_dots[j][0])**2 + 
                              (braille_dots[i][1] - braille_dots[j][1])**2)
                distances.append(dist)
        
        # Estimate the distance between adjacent dots in a Braille cell
        distances.sort()
        cell_height = 0
        cell_width = 0
        
        # Take the smallest 25% of distances to estimate dot spacing within a cell
        n = max(1, len(distances) // 4)
        dot_spacing = sum(distances[:n]) / n
        
        # Vertical and horizontal spacing between cells
        cell_height = dot_spacing * 3  # 3 positions high
        cell_width = dot_spacing * 2   # 2 positions wide
        
        # Group dots into rows
        rows = {}
        row_tolerance = dot_spacing / 2
        
        for dot in braille_dots:
            assigned = False
            for row_y in list(rows.keys()):
                if abs(dot[1] - row_y) < row_tolerance:
                    rows[row_y].append(dot)
                    assigned = True
                    break
            
            if not assigned:
                rows[dot[1]] = [dot]
        
        # Sort rows by y-coordinate
        sorted_rows = sorted(rows.items(), key=lambda x: x[0])
        
        # Define a function to determine if a dot is present at a specific position in a cell
        def is_dot_at_position(dots, cell_x, cell_y, position):
            # Calculate expected coordinates based on position
            x_offset = 0 if position in [1, 2, 3] else dot_spacing
            y_offset = 0 if position in [1, 4] else (dot_spacing if position in [2, 5] else 2*dot_spacing)
            
            expected_x = cell_x + x_offset
            expected_y = cell_y + y_offset
            
            # Check if any dot is close to the expected position
            for dot in dots:
                if (abs(dot[0] - expected_x) < dot_spacing/2 and 
                    abs(dot[1] - expected_y) < dot_spacing/2):
                    return True
            return False
        
        # Group dots into cells and convert to Braille
        braille_chars = []
        
        # Process each row
        for row_y, row_dots in sorted_rows:
            # Sort dots in row by x-coordinate
            row_dots.sort(key=lambda dot: dot[0])
            
            # Group dots into cells (adjacent groups)
            cells = []
            cell_start_x = row_dots[0][0]
            current_cell = []
            
            for dot in row_dots:
                if not current_cell or dot[0] - current_cell[-1][0] < cell_width:
                    current_cell.append(dot)
                else:
                    cells.append(current_cell)
                    current_cell = [dot]
            
            if current_cell:
                cells.append(current_cell)
            
            # Convert each cell to a Braille character
            for cell_dots in cells:
                # Find the top-left corner of the cell
                cell_x = min(dot[0] for dot in cell_dots)
                cell_y = min(dot[1] for dot in cell_dots)
                
                # Determine which positions have dots
                dot_pattern = 0
                if is_dot_at_position(cell_dots, cell_x, cell_y, 1): dot_pattern |= 0x01
                if is_dot_at_position(cell_dots, cell_x, cell_y, 2): dot_pattern |= 0x02
                if is_dot_at_position(cell_dots, cell_x, cell_y, 3): dot_pattern |= 0x04
                if is_dot_at_position(cell_dots, cell_x, cell_y, 4): dot_pattern |= 0x08
                if is_dot_at_position(cell_dots, cell_x, cell_y, 5): dot_pattern |= 0x10
                if is_dot_at_position(cell_dots, cell_x, cell_y, 6): dot_pattern |= 0x20
                
                # Convert dot pattern to Unicode Braille character
                braille_char = chr(0x2800 + dot_pattern)
                braille_chars.append(braille_char)
            
            # Add a space between rows
            braille_chars.append(" ")
        
        # Convert the Braille characters to text
        braille_text = "".join(braille_chars)
        detected_text = braille_to_text(braille_text)
        
        # Draw cell boundaries on the image
        cell_image = dot_image.copy()
        
        # Save the processed image with detected dots
        processed_image_path = temp_filename + "_processed.png"
        cv2.imwrite(processed_image_path, dot_image)
        
        # Convert to Base64 for web display
        with open(processed_image_path, "rb") as img_file:
            processed_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Clean up temporary files
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if os.path.exists(processed_image_path):
            os.remove(processed_image_path)
            
        return detected_text, processed_image_base64
        
    except Exception as e:
        logging.error(f"Error in detect_braille_from_image: {str(e)}")
        # Clean up temporary files if they exist
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)
        if processed_image_path and os.path.exists(processed_image_path):
            os.remove(processed_image_path)
        
        # Return a helpful error message and empty image
        error_message = f"Could not process Braille image: {str(e)}"
        return error_message, ""