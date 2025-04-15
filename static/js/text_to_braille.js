// Text to Braille Conversion JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('text-input');
    const recordButton = document.getElementById('record-button');
    const stopRecordButton = document.getElementById('stop-record-button');
    const brailleOutput = document.getElementById('braille-output');
    const detailedMapping = document.getElementById('detailed-mapping');
    const readAloudButton = document.getElementById('read-aloud-button');
    
    let recognition;
    let isRecording = false;
    
    // Initialize speech recognition if supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        // Use the appropriate constructor
        recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isRecording = true;
            recordButton.classList.add('d-none');
            stopRecordButton.classList.remove('d-none');
            showNotification('Recording Started', 'Speak now...');
        };
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            // Show interim results
            if (interimTranscript) {
                textInput.value = finalTranscript + interimTranscript;
            }
            
            // Process final results
            if (finalTranscript) {
                textInput.value = finalTranscript;
                convertTextToBraille(finalTranscript);
                
                // Show notification
                showNotification('Recording Stopped', 'Your speech has been transcribed');
                
                // Stop recording if we got final results
                if (!interimTranscript) {
                    stopRecording();
                }
            }
        };
        
        recognition.onend = function() {
            isRecording = false;
            recordButton.classList.remove('d-none');
            stopRecordButton.classList.add('d-none');
            
            // If no text was captured, show a notification
            if (!textInput.value.trim()) {
                showNotification('No Speech Detected', 'Please try speaking again');
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            stopRecording();
            
            let errorMessage = 'Speech recognition failed';
            
            // Provide more specific error messages
            switch(event.error) {
                case 'no-speech':
                    errorMessage = 'No speech was detected. Please try again.';
                    break;
                case 'aborted':
                    errorMessage = 'Speech input was aborted.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not available. Please check your microphone settings.';
                    break;
                case 'network':
                    errorMessage = 'Network error occurred. Please check your internet connection.';
                    break;
                case 'not-allowed':
                case 'service-not-allowed':
                    errorMessage = 'Microphone access denied. Please allow microphone access in your browser settings.';
                    break;
                default:
                    errorMessage = 'Speech recognition error: ' + event.error;
            }
            
            showNotification('Error', errorMessage);
        };
    } else {
        // Hide recording buttons if speech recognition is not supported
        recordButton.style.display = 'none';
        stopRecordButton.style.display = 'none';
        showNotification('Unsupported', 'Speech recognition is not supported in your browser');
    }
    
    // Event listener for text input
    textInput.addEventListener('input', function() {
        const text = textInput.value;
        if (text.trim()) {
            convertTextToBraille(text);
        } else {
            brailleOutput.textContent = '';
            detailedMapping.innerHTML = '';
        }
    });
    
    // Event listener for record button
    if (recordButton) {
        recordButton.addEventListener('click', startRecording);
    }
    
    // Event listener for stop record button
    if (stopRecordButton) {
        stopRecordButton.addEventListener('click', stopRecording);
    }
    
    // Event listener for read aloud button
    if (readAloudButton) {
        readAloudButton.addEventListener('click', function() {
            const text = textInput.value;
            if (text.trim()) {
                readAloud(text);
            } else {
                showNotification('Error', 'No text to read');
            }
        });
    }
    
    // Function to start recording
    function startRecording() {
        if (recognition && !isRecording) {
            try {
                // Clear previous input
                textInput.value = '';
                
                // Add visual indicator that recording is active
                recordButton.classList.add('recording');
                
                // Start recognition
                recognition.start();
            } catch (e) {
                console.error('Error starting recording:', e);
                showNotification('Error', 'Could not start recording: ' + e.message);
            }
        }
    }
    
    // Function to stop recording
    function stopRecording() {
        if (recognition && isRecording) {
            try {
                recognition.stop();
                recordButton.classList.remove('recording');
            } catch (e) {
                console.error('Error stopping recording:', e);
            }
        }
    }
    
    // Function to convert text to Braille
    function convertTextToBraille(text) {
        fetch('/api/text-to-braille', {
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
            
            brailleOutput.textContent = data.braille;
            
            // Display detailed mapping
            displayDetailedMapping(data.detailed_mapping);
        })
        .catch(error => {
            console.error('Error converting text to Braille:', error);
            showNotification('Error', 'Failed to convert text to Braille: ' + error.message);
        });
    }
    
    // Function to display detailed character mapping
    function displayDetailedMapping(mapping) {
        detailedMapping.innerHTML = '';
        
        if (!mapping || mapping.length === 0) {
            return;
        }
        
        // Create table header
        const table = document.createElement('table');
        table.className = 'table table-dark table-bordered';
        
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        const englishHeader = document.createElement('th');
        englishHeader.textContent = 'English';
        
        const brailleHeader = document.createElement('th');
        brailleHeader.textContent = 'Braille';
        
        headerRow.appendChild(englishHeader);
        headerRow.appendChild(brailleHeader);
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        mapping.forEach(item => {
            const row = document.createElement('tr');
            
            const englishCell = document.createElement('td');
            englishCell.textContent = item.original;
            
            const brailleCell = document.createElement('td');
            brailleCell.textContent = item.braille;
            brailleCell.style.fontSize = '24px';
            
            row.appendChild(englishCell);
            row.appendChild(brailleCell);
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        detailedMapping.appendChild(table);
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
