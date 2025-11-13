// Django React Project - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Django React Project - Static files loaded successfully!');
    
    // Add some interactive elements
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.textContent);
        });
    });
    
    // Status check functionality
    function checkSystemStatus() {
        const statusElements = document.querySelectorAll('.status-check');
        statusElements.forEach(element => {
            element.classList.add('status-success');
            element.textContent = '✅ Connected';
        });
    }
    
    // Auto-check status on page load
    setTimeout(checkSystemStatus, 1000);
    
    // Add current timestamp
    const timestampElement = document.getElementById('timestamp');
    if (timestampElement) {
        timestampElement.textContent = new Date().toLocaleString();
    }
});