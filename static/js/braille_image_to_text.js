// Braille Image to Text Conversion JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const brailleImageInput = document.getElementById('braille-image-input');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('preview-container');
    const detectedTextElement = document.getElementById('detected-text');
    const processedImageContainer = document.getElementById('processed-image-container');
    const uploadForm = document.getElementById('upload-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const readAloudButton = document.getElementById('read-aloud-button');
    
    // Event listener for image input change
    brailleImageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Display image preview
            const reader = new FileReader();
            
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                previewContainer.classList.remove('d-none');
            };
            
            reader.readAsDataURL(file);
        } else {
            previewContainer.classList.add('d-none');
        }
    });
    
    // Event listener for form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = brailleImageInput.files[0];
        
        if (!file) {
            showNotification('Error', 'Please select an image file');
            return;
        }
        
        // Show loading spinner
        loadingSpinner.classList.remove('d-none');
        
        // Create form data
        const formData = new FormData();
        formData.append('braille_image', file);
        
        // Send image to server for Braille recognition
        fetch('/api/braille-image-to-text', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
            
            if (data.error) {
                showNotification('Error', data.error);
                return;
            }
            
            // Display detected text
            detectedTextElement.textContent = data.text;
            
            // Display processed image
            if (data.processed_image) {
                const img = document.createElement('img');
                img.src = 'data:image/png;base64,' + data.processed_image;
                img.className = 'img-fluid rounded';
                img.alt = 'Processed image with detected Braille dots';
                
                processedImageContainer.innerHTML = '';
                processedImageContainer.appendChild(img);
            }
            
            // Show read aloud button
            if (readAloudButton) {
                readAloudButton.classList.remove('d-none');
            }
            
            showNotification('Success', 'Braille dots analyzed and converted to text');
        })
        .catch(error => {
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
            
            console.error('Error processing Braille image:', error);
            showNotification('Error', 'Failed to process Braille image: ' + error.message);
        });
    });
    
    // Event listener for read aloud button
    if (readAloudButton) {
        readAloudButton.addEventListener('click', function() {
            const text = detectedTextElement.textContent;
            
            if (!text || text.trim() === '') {
                showNotification('Error', 'No text to read');
                return;
            }
            
            readAloud(text);
        });
    }
    
    // Function to read text aloud
    function readAloud(text) {
        fetch('/api/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showNotification('Error', data.error);
                return;
            }
            
            // Play the audio
            const audio = new Audio('data:audio/mp3;base64,' + data.audio_data);
            audio.play();
            
            showNotification('Success', 'Reading text aloud');
        })
        .catch(error => {
            console.error('Error reading text aloud:', error);
            showNotification('Error', 'Failed to read text aloud: ' + error.message);
        });
    }
    
    // Function to show notification
    function showNotification(title, message) {
        const notification = document.getElementById('notification');
        const notificationTitle = document.getElementById('notification-title');
        const notificationMessage = document.getElementById('notification-message');
        
        if (notification && notificationTitle && notificationMessage) {
            notificationTitle.textContent = title;
            notificationMessage.textContent = message;
            
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        } else {
            console.log(`Notification: ${title} - ${message}`);
        }
    }
});