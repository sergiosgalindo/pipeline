const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const conversation = document.querySelector('#conversation');
const sendButton = document.querySelector('#send');
const welcome = document.querySelector('#welcome');
const history = [];

function addMessage(role, text, sources = [], extraClass = '') {
  const row = document.createElement('div');
  row.className = `message ${role} ${extraClass}`;
  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'T' : 'B';
  const body = document.createElement('div');
  body.className = 'message-content';
  body.textContent = text;
  row.append(avatar, body);
  if (sources.length) {
    const sourceLine = document.createElement('div');
    sourceLine.className = 'sources';
    sourceLine.textContent = `Fuente: ${sources.join(' · ')}`;
    body.append(sourceLine);
  }
  conversation.append(row);
  conversation.classList.add('has-messages');
  conversation.scrollTop = conversation.scrollHeight;
  return row;
}

async function ask(question) {
  if (!question || sendButton.disabled) return;
  welcome.hidden = true;
  addMessage('user', question);
  const priorHistory = history.slice();
  history.push({ role: 'user', content: question });
  const pending = addMessage('assistant', 'Buscando en las políticas…', [], 'typing');
  sendButton.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question, history: priorHistory }),
    });
    const data = await response.json();
    pending.remove();
    if (!response.ok) throw new Error(data.detail || data.error || 'No se pudo obtener una respuesta.');
    addMessage('assistant', data.answer, data.sources || []);
    history.push({ role: 'assistant', content: data.answer });
  } catch (error) {
    pending.remove();
    addMessage('assistant', error.message, [], 'error');
    history.pop();
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  input.value = '';
  input.style.height = 'auto';
  ask(question);
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll('[data-question]').forEach((button) => {
  button.addEventListener('click', () => ask(button.dataset.question));
});

function resetConversation() {
  history.length = 0;
  conversation.querySelectorAll('.message').forEach((message) => message.remove());
  welcome.hidden = false;
  conversation.classList.remove('has-messages');
  input.focus();
}

document.querySelector('#new-chat').addEventListener('click', resetConversation);
document.querySelector('#new-chat-mobile').addEventListener('click', resetConversation);
