// Braille to Speech Conversion JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const brailleInput = document.getElementById('braille-input');
    const convertButton = document.getElementById('convert-button');
    const textOutput = document.getElementById('text-output');
    const readAloudButton = document.getElementById('read-aloud-button');
    const brailleButtons = document.querySelectorAll('.braille-btn');
    
    // Event listener for Braille input
    brailleInput.addEventListener('input', function() {
        const braille = brailleInput.value;
        if (!braille.trim()) {
            textOutput.textContent = '';
        }
    });
    
    // Event listener for convert button
    convertButton.addEventListener('click', function() {
        const braille = brailleInput.value;
        
        if (!braille.trim()) {
            showNotification('Error', 'Please enter Braille characters');
            return;
        }
        
        convertBrailleToText(braille);
    });
    
    // Event listener for read aloud button
    if (readAloudButton) {
        readAloudButton.addEventListener('click', function() {
            const text = textOutput.textContent;
            
            if (!text || text.trim() === '') {
                showNotification('Error', 'No text to read');
                return;
            }
            
            readAloud(text);
        });
    }
    
    // Event listeners for Braille buttons
    brailleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const brailleChar = this.getAttribute('data-braille');
            insertBrailleCharacter(brailleChar);
        });
    });
    
    // Function to insert Braille character at cursor position
    function insertBrailleCharacter(character) {
        const startPos = brailleInput.selectionStart;
        const endPos = brailleInput.selectionEnd;
        const text = brailleInput.value;
        
        brailleInput.value = text.substring(0, startPos) + character + text.substring(endPos);
        
        // Set cursor position after the inserted character
        brailleInput.selectionStart = startPos + character.length;
        brailleInput.selectionEnd = startPos + character.length;
        
        // Focus back on the input
        brailleInput.focus();
    }
    
    // Function to convert Braille to text
    function convertBrailleToText(braille) {
        fetch('/api/braille-to-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ braille: braille }),
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
            
            textOutput.textContent = data.text;
            
            if (data.text.trim()) {
                readAloudButton.classList.remove('d-none');
            } else {
                readAloudButton.classList.add('d-none');
            }
            
            showNotification('Success', 'Braille converted to text');
        })
        .catch(error => {
            console.error('Error converting Braille to text:', error);
            showNotification('Error', 'Failed to convert Braille to text: ' + error.message);
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
