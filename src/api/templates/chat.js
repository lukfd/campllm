const { createApp, ref, nextTick } = Vue

const setup = () => {
    const question = ref('')
    const model = ref('Loading model...')
    const messages = ref([])

        fetch('/api/model')
        .then(res => res.json())
        .then(data => {
            model.value = data.model;
        })
        .catch(err => {
            model.value = 'Error loading model';
            console.error('Error fetching model:', err);
        });

    async function askQuestion() {
        if (!question.value) return;

        const currentQuestion = question.value;
        messages.value.push({ sender: 'user', prefix: 'You:', text: currentQuestion });
        question.value = '';

        await nextTick();
        const chatHistory = document.getElementById('chat-history');
        chatHistory.scrollTop = chatHistory.scrollHeight;

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: currentQuestion }),
        });

        let botText = '';
        let botHtml = '';
        try {
            if (!response.ok) {
                // Try to extract useful error information from JSON or text
                let errText = '';
                try {
                    const errJson = await response.json();
                    errText = errJson.detail || errJson.message || JSON.stringify(errJson);
                } catch (e) {
                    errText = await response.text();
                }
                botText = `Error ${response.status}: ${errText || response.statusText}`;
                const raw = (typeof marked !== 'undefined') ? marked.parse(botText) : botText.replace(/\n/g, '<br>');
                botHtml = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
                messages.value.push({ sender: 'bot', prefix: 'Error:', text: botText, html: botHtml, type: 'error' });
                return;
            }

            const data = await response.json();
            botText = data.answer || '';
            if (data.sources && data.sources.length > 0) {
                botText += "\n\nSources:\n";
                data.sources.forEach(source => {
                    botText += `- ${source.park_name}: ${source.section_heading} (${source.section_url})\n`;
                });
            }

            // Convert Markdown to HTML and sanitize it before inserting
            const raw = (typeof marked !== 'undefined') ? marked.parse(botText) : botText.replace(/\n/g, '<br>');
            botHtml = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
            messages.value.push({ sender: 'bot', prefix: 'Bot:', text: botText, html: botHtml });

        } catch (err) {
            // Network or unexpected error
            botText = `Network error: ${err.message || String(err)}`;
            const raw = (typeof marked !== 'undefined') ? marked.parse(botText) : botText.replace(/\n/g, '<br>');
            botHtml = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
            messages.value.push({ sender: 'bot', prefix: 'Error:', text: botText, html: botHtml, type: 'error' });
        }

        await nextTick();
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    return {
        question,
        messages,
        model,
        askQuestion
    }
}

const vueApp = {
    delimiters: ['[[', ']]'],
    setup: setup
}

createApp(vueApp).mount('#app')
