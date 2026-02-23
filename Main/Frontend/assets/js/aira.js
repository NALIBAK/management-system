/* ============================================================
   AIRA Widget — Floating Chat Component
   ============================================================ */

const aira = {
    conversationId: null,
    isOpen: false,
    isTyping: false,

    init() {
        this._inject();
        this._bindEvents();
        this._addWelcomeMessage();
    },

    _inject() {
        const widget = document.createElement('div');
        widget.className = 'aira-widget';
        widget.id = 'aira-widget';
        widget.innerHTML = `
      <div class="aira-panel" id="aira-panel">
        <div class="aira-panel-header">
          <div class="aira-avatar">🤖</div>
          <div class="aira-header-info">
            <h4>AIRA</h4>
            <span>AI Research Assistant</span>
          </div>
          <button class="aira-close-btn" id="aira-close">✕</button>
        </div>
        <div class="aira-quick-actions" id="aira-quick-actions">
          <button class="aira-quick-btn" data-prompt="Show students with attendance below 75%">📊 Low Attendance</button>
          <button class="aira-quick-btn" data-prompt="Show fee defaulters">💰 Fee Defaulters</button>
          <button class="aira-quick-btn" data-prompt="Show department summary">🏫 Dept Summary</button>
          <button class="aira-quick-btn" data-prompt="Show student CGPA report">📊 CGPA Report</button>
          <button class="aira-quick-btn" data-prompt="Show eligibility report">🎯 Eligibility</button>
          <button class="aira-quick-btn" data-prompt="Show category wise report">🏷️ Categories</button>
          <button class="aira-quick-btn" data-prompt="Show scholarship report">🎓 Scholarships</button>
        </div>
        <div class="aira-messages" id="aira-messages"></div>
        <div class="aira-input-area">
          <textarea class="aira-input" id="aira-input" placeholder="Ask AIRA anything..." rows="1"></textarea>
          <button class="aira-send-btn" id="aira-send">➤</button>
        </div>
      </div>
      <div class="aira-bubble" id="aira-bubble">
        <div class="aira-pulse"></div>
        <span class="aira-icon">🤖</span>
      </div>`;
        document.body.appendChild(widget);
    },

    _bindEvents() {
        document.getElementById('aira-bubble').onclick = () => this.toggle();
        document.getElementById('aira-close').onclick = () => this.close();
        document.getElementById('aira-send').onclick = () => this._send();

        const input = document.getElementById('aira-input');
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this._send(); }
        });
        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        });

        document.querySelectorAll('.aira-quick-btn').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('aira-input').value = btn.dataset.prompt;
                this._send();
            };
        });
    },

    toggle() { this.isOpen ? this.close() : this.open(); },

    open() {
        this.isOpen = true;
        document.getElementById('aira-panel').classList.add('open');
        document.getElementById('aira-input').focus();
    },

    close() {
        this.isOpen = false;
        document.getElementById('aira-panel').classList.remove('open');
    },

    _addWelcomeMessage() {
        const user = auth.getUser();
        const name = user ? user.username : 'there';
        this._appendMessage('aira', `👋 Hi ${name}! I'm AIRA, your AI assistant. I can help you query student data, attendance, marks, fees, and more. What would you like to know?`);
    },

    _appendMessage(role, content) {
        const container = document.getElementById('aira-messages');
        const isUser = role === 'user';
        const initials = isUser ? (auth.getUserInitials() || 'U') : '🤖';
        const div = document.createElement('div');
        div.className = `aira-msg ${role}`;
        div.innerHTML = `
      <div class="aira-msg-avatar">${initials}</div>
      <div class="aira-msg-bubble">${content.replace(/\n/g, '<br>')}</div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    },

    _showTyping() {
        const container = document.getElementById('aira-messages');
        const div = document.createElement('div');
        div.className = 'aira-msg aira';
        div.id = 'aira-typing-indicator';
        div.innerHTML = `
      <div class="aira-msg-avatar">🤖</div>
      <div class="aira-typing"><span></span><span></span><span></span></div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    },

    _hideTyping() {
        document.getElementById('aira-typing-indicator')?.remove();
    },

    async _send() {
        const input = document.getElementById('aira-input');
        const message = input.value.trim();
        if (!message || this.isTyping) return;

        input.value = '';
        input.style.height = 'auto';
        this._appendMessage('user', message);
        this._showTyping();
        this.isTyping = true;
        document.getElementById('aira-send').disabled = true;

        try {
            const pageContext = window.location.pathname;
            const res = await api.post('/aira/chat', {
                message,
                conversation_id: this.conversationId,
                page_context: pageContext
            });

            this._hideTyping();
            if (res && res.data) {
                this.conversationId = res.data.data?.conversation_id || this.conversationId;
                const reply = res.data.data?.response || res.data.message || 'Sorry, I could not process that.';
                this._appendMessage('aira', reply);
            } else {
                this._appendMessage('aira', '⚠️ Could not connect to AIRA. Please check if the backend is running.');
            }
        } catch (err) {
            this._hideTyping();
            this._appendMessage('aira', '⚠️ An error occurred. Please try again.');
        } finally {
            this.isTyping = false;
            document.getElementById('aira-send').disabled = false;
        }
    }
};

// Auto-init when DOM is ready (only if logged in)
document.addEventListener('DOMContentLoaded', () => {
    if (auth.isLoggedIn()) aira.init();
});

window.aira = aira;
