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
        // scroll to bottom by bringing the last child into view
        chatHistory.lastElementChild?.scrollIntoView({ behavior: 'auto', block: 'end' });

        // show loading placeholder which we will replace with the real response
        const loadingIndex = messages.value.push({ sender: 'bot', prefix: 'Bot:', text: '...', html: null, type: 'loading' }) - 1;

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
                // replace the loading placeholder with an error message
                messages.value[loadingIndex] = { sender: 'bot', prefix: 'Error:', text: botText, html: botHtml, type: 'error' };
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
            // replace the loading placeholder with the bot response
            messages.value[loadingIndex] = { sender: 'bot', prefix: 'Bot:', text: botText, html: botHtml };

        } catch (err) {
            // Network or unexpected error
            botText = `Network error: ${err.message || String(err)}`;
            const raw = (typeof marked !== 'undefined') ? marked.parse(botText) : botText.replace(/\n/g, '<br>');
            botHtml = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
            // replace the loading placeholder with an error message
            messages.value[loadingIndex] = { sender: 'bot', prefix: 'Error:', text: botText, html: botHtml, type: 'error' };
        }

        await nextTick();
        // ensure the latest message is visible
        chatHistory.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
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
