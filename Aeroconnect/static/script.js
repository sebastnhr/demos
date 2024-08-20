document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const autoBtn = document.getElementById('auto-btn');

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

    function addMessage(message, isUser, isError = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message', isError ? 'error' : 'message');
        messageElement.innerHTML = message;
        removeLoader();
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function cambiarEstadoBotones(estado) {
        ['send-btn', 'auto-btn'].forEach(id => document.getElementById(id).disabled = estado);
    }

    function sendMessage(question = false) {
        let message = question || userInput.value.trim();
        if (!message) return;
        cambiarEstadoBotones(true);

        if (!question) {
            addLoader();
            addMessage(message, true);
            userInput.value = '';
        }

        addLoader('left');
        fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: message })
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
            addMessage(data.question, true);
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

    sendBtn.addEventListener('click', sendMessage);
    autoBtn.addEventListener('click', sendAutoMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    welcome();
});
