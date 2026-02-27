/* ============================================================
   AIRA Widget — Autonomous AI Research Assistant
   ============================================================ */

// Load marked.js for markdown rendering (if not already loaded)
(function() {
    if (typeof marked === 'undefined') {
        const s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/marked@9/marked.min.js';
        s.onload = () => {
            marked.setOptions({ breaks: true, gfm: true });
        };
        document.head.appendChild(s);
    }
})();

const aira = {
    conversationId: null,
    isOpen: false,
    isTyping: false,

    _QUICK_ACTIONS: [
        { label: '📊 Low Attendance',      prompt: 'Show students with attendance below 75%' },
        { label: '💰 Fee Defaulters',       prompt: 'Show fee defaulters' },
        { label: '🏫 Dept Summary',         prompt: 'Show department summary' },
        { label: '📈 CGPA Report',          prompt: 'Show student CGPA report' },
        { label: '🎯 Eligibility',          prompt: 'Show eligibility report' },
        { label: '🏷️ Categories',          prompt: 'Show category wise report' },
        { label: '🎓 Scholarships',         prompt: 'Show scholarship report' },
        { label: '📝 Marks Report',         prompt: 'Show marks report' },
        { label: '📅 Attendance Report',    prompt: 'Show attendance report' },
        { label: '🏆 Top Students',         prompt: 'Show top 10 students by CGPA' },
        { label: '💰 Fee Structure',        prompt: 'Show fee structure report' },
        { label: '🔬 Activities',           prompt: 'Show extracurricular activities report' },
    ],

    init() {
        this._inject();
        this._bindEvents();
        this._addWelcomeMessage();
    },

    _inject() {
        const quickBtns = this._QUICK_ACTIONS.map(a =>
            `<button class="aira-quick-btn" data-prompt="${a.prompt}">${a.label}</button>`
        ).join('');

        const widget = document.createElement('div');
        widget.className = 'aira-widget';
        widget.id = 'aira-widget';
        widget.innerHTML = `
      <div class="aira-panel" id="aira-panel">
        <div class="aira-panel-header">
          <div class="aira-avatar">🤖</div>
          <div class="aira-header-info">
            <h4>AIRA <span style="font-size:10px;opacity:0.75;font-weight:400">Autonomous Agent</span></h4>
            <span id="aira-status-line">AI Research Assistant • Database Connected</span>
          </div>
          <button class="aira-close-btn" id="aira-close">✕</button>
        </div>
        <div class="aira-quick-actions" id="aira-quick-actions">${quickBtns}</div>
        <div class="aira-messages" id="aira-messages"></div>
        <div class="aira-input-area">
          <textarea class="aira-input" id="aira-input" placeholder="Ask AIRA anything about students, staff, fees, marks..." rows="1"></textarea>
          <button class="aira-send-btn" id="aira-send" title="Send (Enter)">➤</button>
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

        document.getElementById('aira-quick-actions').addEventListener('click', (e) => {
            const btn = e.target.closest('.aira-quick-btn');
            if (btn) {
                document.getElementById('aira-input').value = btn.dataset.prompt;
                this._send();
            }
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
        const name = user ? (user.username || 'there') : 'there';
        this._appendMessage('aira', `## 👋 Hi ${name}! I'm AIRA

I'm an **autonomous AI agent** connected to your college database. I can:

- 📊 **Query & report** — students, staff, attendance, marks, fees
- 🔍 **Analyze data** — find top students, defaulters, low attendance
- 📋 **Generate tables** — formatted reports from live DB
- ✏️ **Write actions** — mark attendance (with confirmation)

> 💡 Use the quick buttons above or ask me anything in natural language!`);
    },

    _renderMarkdown(text) {
        try {
            if (typeof marked !== 'undefined') {
                return marked.parse(text);
            }
        } catch(e) {}
        // Fallback: basic formatting
        return text
            .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
            .replace(/\*(.+?)\*/g,'<em>$1</em>')
            .replace(/`(.+?)`/g,'<code>$1</code>')
            .replace(/\n/g,'<br>');
    },

    _appendMessage(role, content, opts = {}) {
        const container = document.getElementById('aira-messages');
        const isUser = role === 'user';
        const initials = isUser ? (auth.getUserInitials() || 'U') : '🤖';
        const div = document.createElement('div');
        div.className = `aira-msg ${role}`;

        const rendered = isUser
            ? `<span>${content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span>`
            : this._renderMarkdown(content);

        const copyBtn = (!isUser && content.length > 200)
            ? `<button class="aira-copy-btn" onclick="aira._copy(this)">📋 Copy</button>`
            : '';

        div.innerHTML = `
      <div class="aira-msg-avatar">${initials}</div>
      <div class="aira-msg-bubble">${rendered}${copyBtn}</div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        return div;
    },

    _copy(btn) {
        const bubble = btn.closest('.aira-msg-bubble');
        const text = bubble.innerText.replace('📋 Copy','').trim();
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = '✅ Copied!';
            setTimeout(() => { btn.textContent = '📋 Copy'; }, 2000);
        });
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

    _showToolStatus(toolName) {
        const container = document.getElementById('aira-messages');
        const div = document.createElement('div');
        div.className = 'aira-msg aira';
        div.id = 'aira-tool-status';
        const labels = {
            get_student_info: 'Looking up student info',
            get_attendance_summary: 'Fetching attendance data',
            get_marks: 'Loading marks records',
            get_fee_balance: 'Checking fee balance',
            get_department_summary: 'Fetching department stats',
            get_top_students: 'Finding top students',
            get_low_attendance: 'Scanning attendance records',
            get_fee_defaulters: 'Checking fee payments',
            get_staff_by_department: 'Loading staff list',
            generate_attendance_report: 'Generating attendance report',
            generate_marks_report: 'Generating marks report',
            generate_student_profile_report: 'Building student profiles',
            generate_fee_structure_report: 'Loading fee structures',
            generate_eligibility_report: 'Evaluating eligibility',
            generate_category_wise_report: 'Building category report',
            generate_scholarship_report: 'Fetching scholarship data',
            generate_extracurricular_report: 'Loading activity records',
        };
        const label = labels[toolName] || `Running: ${toolName}`;
        div.innerHTML = `
      <div class="aira-msg-avatar">🤖</div>
      <div style="display:flex;align-items:center;gap:0">
        <div class="aira-tool-status">
          <div class="tool-spinner"></div>
          🔧 ${label}…
        </div>
      </div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    },

    _hideToolStatus() {
        document.getElementById('aira-tool-status')?.remove();
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

        // Hide quick actions after first message
        document.getElementById('aira-quick-actions').style.display = 'none';

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

                // Show tool calls made (if any)
                const toolCalls = res.data.data?.tool_calls || [];
                toolCalls.forEach(tc => {
                    if (tc && tc.name) this._showToolStatus(tc.name);
                    setTimeout(() => this._hideToolStatus(), 1200);
                });

                if (res.data.data?.needs_confirmation) {
                    this._appendConfirmation(
                        res.data.data.preview || reply,
                        res.data.data.action_id
                    );
                } else {
                    this._appendMessage('aira', reply);
                }
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
    },

    _appendConfirmation(preview, actionId) {
        const container = document.getElementById('aira-messages');
        const div = document.createElement('div');
        div.className = 'aira-msg aira';
        div.innerHTML = `
      <div class="aira-msg-avatar">🤖</div>
      <div class="aira-msg-bubble">
        <div class="aira-confirm-card">
          <p><strong>⚠️ Confirm Action</strong></p>
          <p>${this._renderMarkdown(preview)}</p>
          <div class="aira-confirm-actions" id="confirm-${actionId}">
            <button class="btn btn-primary btn-sm aira-confirm-yes" onclick="aira._handleConfirm(${actionId})">✅ Confirm</button>
            <button class="btn btn-ghost btn-sm aira-confirm-no" onclick="aira._handleCancel(${actionId})">❌ Cancel</button>
          </div>
        </div>
      </div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    },

    async _handleConfirm(actionId) {
        const container = document.getElementById(`confirm-${actionId}`);
        if (container) container.innerHTML = '<em>Processing...</em>';
        try {
            const res = await api.post('/aira/confirm-action', { action_id: actionId });
            if (container) {
                container.innerHTML = res?.data?.message
                    ? `<span style="color:var(--success-color)">✅ ${res.data.message}</span>`
                    : '<span style="color:var(--success-color)">✅ Action completed!</span>';
            }
        } catch (err) {
            if (container) container.innerHTML = '<span style="color:var(--danger-color)">❌ Failed to execute action</span>';
        }
    },

    async _handleCancel(actionId) {
        const container = document.getElementById(`confirm-${actionId}`);
        if (container) container.innerHTML = '<em>Cancelling...</em>';
        try {
            await api.post('/aira/cancel-action', { action_id: actionId });
            if (container) container.innerHTML = '<span style="color:var(--text-muted)">🚫 Action cancelled</span>';
        } catch (err) {
            if (container) container.innerHTML = '<span style="color:var(--danger-color)">❌ Failed to cancel</span>';
        }
    }
};

// Auto-init when DOM is ready (only if logged in)
document.addEventListener('DOMContentLoaded', () => {
    if (auth.isLoggedIn()) aira.init();
});

window.aira = aira;
