document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const autoBtn = document.getElementById('auto-btn');
    const imageUpload = document.getElementById('image-upload');
    let currentImageData = null;

    /*Input file*/
    const fileInput = document.getElementById('image-upload');
    const fileLabel = document.querySelector('.file-input label');
    const tooltip = document.querySelector('.tooltip');

    fileInput.addEventListener('change', function(e) {
        if(this.files && this.files.length > 0) {
            fileInput.classList.add('has-file');
            tooltip.textContent = this.files[0].name;
        } else {
            fileInput.classList.remove('has-file');
            tooltip.textContent = 'Ningún archivo seleccionado';
        }
    });

    /*Loader message*/
    function addLoader(align = 'right') {
        const loaderElement = document.createElement('span');
        loaderElement.classList.add('loader', align);
        chatMessages.appendChild(loaderElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeLoader() {
        const loaderElement = document.querySelector("#chat-messages .loader");
        if (loaderElement) loaderElement.remove();
    }

    function cambiarEstadoBotones(estado) {
        ['send-btn', 'auto-btn', 'image-upload'].forEach(id => document.getElementById(id).disabled = estado);
    }

    function addMessage(message, isUser, isError = false, imageData = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message', isError ? 'error' : 'message');
        
        const textElement = document.createElement('p');
        textElement.innerHTML = message;
        messageElement.appendChild(textElement);
        
        if (isUser && imageData) {
            const imageElement = document.createElement('img');
            imageElement.src = `data:image/jpeg;base64,${imageData}`;
            imageElement.alt = "Imagen subida por el usuario";
            imageElement.style.maxWidth = '100%';
            imageElement.style.maxHeight = '200px';
            messageElement.appendChild(imageElement);
        }
        
        removeLoader();
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function sendMessage(question = null) {
        let message = '';
        
        if (question !== null && typeof question === 'string') {
            message = question.trim();
        } else {
            message = userInput.value.trim();
        }
        
        if (!message && !currentImageData) return;
        
        cambiarEstadoBotones(true);
        addLoader();
        addMessage(message, true, false, currentImageData);
        userInput.value = '';
        
        addLoader('left');
        
        const requestBody = { question: message };
        if (currentImageData) {
            requestBody.image = currentImageData;
            currentImageData = null;
            imageUpload.value = '';
        }
        
        fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => addMessage(data.answer, false, data.answer.includes('Error')))
        .catch(error => {
            console.error('Error:', error);
            addMessage('Lo siento, ha ocurrido un error.', false, true);
        })
        .finally(() => cambiarEstadoBotones(false));
    }

    function sendAutoMessage() {
        cambiarEstadoBotones(true);
        addLoader();

        fetch('/auto', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            removeLoader();
            sendMessage(data.question);
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Lo siento, ha ocurrido un error.', false, true);
        })
        .finally(() => cambiarEstadoBotones(false));
    }

    function welcome() {
        cambiarEstadoBotones(true);
        addLoader('left');

        fetch('/welcome', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => addMessage(data.welcome, false, data.welcome.includes('Error')))
        .catch(error => {
            console.error('Error:', error);
            addMessage('Lo siento, ha ocurrido un error.', false, true);
        })
        .finally(() => cambiarEstadoBotones(false));
    }

    imageUpload.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                currentImageData = e.target.result.split(',')[1]; // Obtener solo la parte de datos base64
            };
            reader.readAsDataURL(file);
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    autoBtn.addEventListener('click', sendAutoMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    welcome();
});