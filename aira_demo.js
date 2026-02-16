// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
});

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
    }
}

// Sample Queries
const sampleQueries = [
    "Show me all CSE students with attendance below 75%",
    "Generate fee defaulters report for ECE department as PDF",
    "Calculate average marks for CS301 subject in 3rd semester",
    "What's the average GPA for Mechanical Engineering 2023 batch?"
];

const sampleResponses = [
    {
        text: "I found 12 students in CSE department with attendance below 75%.\n\nHere are the top 5 students with lowest attendance:\n• Rajesh Kumar (CSE-A, Roll: 2023001) - 68%\n• Priya Sharma (CSE-B, Roll: 2023045) - 70%\n• Amit Patel (CSE-A, Roll: 2023012) - 72%\n• Sneha Reddy (CSE-C, Roll: 2023089) - 73%\n• Vikram Singh (CSE-B, Roll: 2023056) - 74%\n\nWould you like me to:\n1. Export complete list as Excel\n2. Send attendance warnings to these students\n3. View detailed attendance breakdown",
        delay: 1500
    },
    {
        text: "I'm generating the fee defaulters report for ECE department...\n\n✅ Report generated successfully!\n\nSummary:\n• Total students: 180\n• Fee defaulters: 23 (12.8%)\n• Total pending amount: ₹8,45,000\n• Semester: Current (Odd 2024-25)\n\n📄 The PDF report \"ECE_Fee_Defaulters_Feb2026.pdf\" has been created and is ready for download.\n\nThe report includes:\n✓ Student details with contact info\n✓ Pending amount breakdown\n✓ Payment due dates\n✓ Guardian contact information",
        delay: 2000,
        showDownload: true
    },
    {
        text: "Calculating statistics for CS301 (Database Management Systems) in 3rd semester...\n\n📊 Results:\n\n• Average Marks: 72.4/100\n• Highest Score: 94 (Ananya Gupta, CSE-A)\n• Lowest Score: 42 (Rohit Mehta, CSE-C)\n• Pass Percentage: 89.2%\n• Students Appeared: 156\n• Absentees: 4\n\nGrade Distribution:\n🟢 O Grade (90-100): 18 students\n🟢 A+ Grade (80-89): 34 students\n🟡 A Grade (70-79): 42 students\n🟡 B+ Grade (60-69): 38 students\n🟠 B Grade (50-59): 21 students\n🔴 Failed (<50): 17 students",
        delay: 1800
    },
    {
        text: "Analyzing GPA data for Mechanical Engineering 2023 batch...\n\n📈 Analytics Summary:\n\n• Batch Size: 120 students\n• Average CGPA: 7.82/10\n• Highest CGPA: 9.45 (Karthik Iyer)\n• Lowest CGPA: 5.23 (Pending improvement)\n\nPerformance Distribution:\n🌟 Excellent (9.0-10.0): 15 students (12.5%)\n⭐ Very Good (8.0-8.9): 38 students (31.7%)\n✨ Good (7.0-7.9): 42 students (35%)\n📚 Average (6.0-6.9): 19 students (15.8%)\n📖 Below Average (<6.0): 6 students (5%)\n\nTrend: The batch shows consistent improvement with 8% increase in average CGPA from 1st year to current.",
        delay: 1700
    }
];

// Send Sample Query
function sendSampleQuery(index) {
    const input = document.getElementById('chatInput');
    input.value = sampleQueries[index];
    sendMessage();
}

// Handle Enter Key
function handleEnter(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send Message
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    input.value = '';
    
    // Find matching index
    const queryIndex = sampleQueries.findIndex(q => 
        q.toLowerCase().includes(message.toLowerCase().substring(0, 15)) || 
        message.toLowerCase().includes(q.toLowerCase().substring(0, 15))
    );
    
    // Show typing indicator
    showTypingIndicator();
    
    // Simulate AI response
    setTimeout(() => {
        removeTypingIndicator();
        if (queryIndex !== -1) {
            addMessage(sampleResponses[queryIndex].text, 'aira');
            if (sampleResponses[queryIndex].showDownload) {
                setTimeout(() => addDownloadButton(), 500);
            }
        } else {
            addMessage(
                "I understand you're asking about: \"" + message + "\"\n\n" +
                "This is a demo interface. In the full version, I would:\n" +
                "• Analyze your query using natural language processing\n" +
                "• Access the relevant database tables\n" +
                "• Process your request based on your role permissions\n" +
                "• Provide instant results with actionable insights\n\n" +
                "Try one of the Quick Action buttons for a full demo experience!",
                'aira'
            );
        }
    }, 1000 + Math.random() * 1000);
}

// Add Message
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const isAira = sender === 'aira';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isAira ? 'aira-message' : 'user-message'}`;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                ${isAira ? 
                    '<path d="M12 2 L12 22 M6 8 L12 2 L18 8 M6 16 L12 22 L18 16"/>' :
                    '<circle cx="12" cy="8" r="4"/><path d="M6 21v-2a6 6 0 0 1 12 0v2"/>'
                }
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">${text.replace(/\n/g, '<br>')}</div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Typing Indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message aira-message typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2 L12 22 M6 8 L12 2 L18 8 M6 16 L12 22 L18 16"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add CSS for typing animation if not exists
    if (!document.getElementById('typing-animation-style')) {
        const style = document.createElement('style');
        style.id = 'typing-animation-style';
        style.textContent = `
            .typing-dots {
                display: flex;
                gap: 4px;
                padding: 8px;
            }
            .typing-dots span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--accent-purple);
                animation: typing 1.4s infinite;
            }
            .typing-dots span:nth-child(2) {
                animation-delay: 0.2s;
            }
            .typing-dots span:nth-child(3) {
                animation-delay: 0.4s;
            }
            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.7;
                }
                30% {
                    transform: translateY(-10px);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function removeTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Add Download Button
function addDownloadButton() {
    const chatMessages = document.getElementById('chatMessages');
    const downloadDiv = document.createElement('div');
    downloadDiv.className = 'message aira-message';
    downloadDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2 L12 22 M6 8 L12 2 L18 8 M6 16 L12 22 L18 16"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">
                <button class="download-report-btn" onclick="downloadReport()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    <span>Download Report (PDF)</span>
                </button>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(downloadDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add download button CSS
    if (!document.getElementById('download-btn-style')) {
        const style = document.createElement('style');
        style.id = 'download-btn-style';
        style.textContent = `
            .download-report-btn {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.75rem 1.5rem;
                background: var(--primary-gradient);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 0.5rem;
            }
            .download-report-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            .download-report-btn svg {
                width: 18px;
                height: 18px;
            }
        `;
        document.head.appendChild(style);
    }
}

// Download Report (Demo)
function downloadReport() {
    addMessage("✅ Report download started! In the full version, the PDF would download automatically.", 'aira');
}

// Clear Chat
function clearChat() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="message aira-message">
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2 L12 22 M6 8 L12 2 L18 8 M6 16 L12 22 L18 16"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-text">Chat cleared! How can I help you today?</div>
                <div class="message-time">Just now</div>
            </div>
        </div>
    `;
}

// Scroll to Demo
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.boxShadow = 'var(--shadow-md)';
    } else {
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.feature-card, .capability-card, .stat-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Prevent page reload on button clicks
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!btn.hasAttribute('onclick')) {
            e.preventDefault();
        }
    });
});
