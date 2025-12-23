/**
 * AI Chatbot Widget
 * Provides floating chat interface for Python tutoring
 */

class ChatbotWidget {
    constructor() {
        this.conversationId = null;
        this.contextType = 'general';
        this.contextId = null;
        this.isOpen = false;
        this.isExpanded = false;
        this.isLoading = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    async init() {
        // Detect context from page
        this.detectContext();
        
        // Create widget HTML
        this.createWidget();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Load conversation if exists (wait for it to complete)
        // This will also update the context badge
        await this.loadConversation();
    }
    
    detectContext() {
        // Check if we're on a lesson or exercise page
        const path = window.location.pathname;
        
        // Reset context
        this.contextType = 'general';
        this.contextId = null;
        
        if (path.includes('/lesson/')) {
            const match = path.match(/\/lesson\/(\d+)/);
            if (match) {
                this.contextType = 'lesson';
                this.contextId = parseInt(match[1]);
                console.log('Context detected: lesson', this.contextId);
            }
        } else if (path.includes('/exercise/')) {
            const match = path.match(/\/exercise\/(\d+)/);
            if (match) {
                this.contextType = 'exercise';
                this.contextId = parseInt(match[1]);
                console.log('Context detected: exercise', this.contextId);
            }
        }
    }
    
    createWidget() {
        const widgetHTML = `
            <!-- Chatbot Toggle Button -->
            <button id="chatbot-toggle" class="chatbot-toggle" title="AI Python Tutor">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span class="chatbot-badge" id="chatbot-badge" style="display: none;">1</span>
            </button>
            
            <!-- Chatbot Window -->
            <div id="chatbot-window" class="chatbot-window" style="display: none;">
                <!-- History Sidebar -->
                <div id="chatbot-history-sidebar" class="chatbot-history-sidebar">
                    <div class="history-header">
                        <h3>Chat History</h3>
                        <button id="history-close" class="chatbot-icon-btn">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    <div class="history-list" id="history-list">
                        <div class="history-loading">Loading conversations...</div>
                    </div>
                </div>
                
                <div class="chatbot-header">
                    <div class="chatbot-header-left">
                        <div class="chatbot-avatar">🤖</div>
                        <div class="chatbot-header-info">
                            <div class="chatbot-title">AI Python Tutor</div>
                            <div class="chatbot-status" id="chatbot-status">Online</div>
                        </div>
                    </div>
                    <div class="chatbot-header-actions">
                        <button id="chatbot-history" class="chatbot-icon-btn" title="Chat history">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                        </button>
                        <button id="chatbot-new" class="chatbot-icon-btn" title="New conversation">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                        <button id="chatbot-expand" class="chatbot-icon-btn" title="Expand">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <polyline points="9 21 3 21 3 15"></polyline>
                                <line x1="21" y1="3" x2="14" y2="10"></line>
                                <line x1="3" y1="21" x2="10" y2="14"></line>
                            </svg>
                        </button>
                        <button id="chatbot-close" class="chatbot-icon-btn" title="Close">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="chatbot-context" id="chatbot-context" style="display: none;">
                    <div class="context-info">
                        <span class="context-icon">📚</span>
                        <span class="context-text" id="context-text">Context: General</span>
                    </div>
                    <a href="#" id="context-link" class="context-link" style="display: none;">Go to Page →</a>
                </div>
                
                <div class="chatbot-messages" id="chatbot-messages">
                    <div class="chatbot-welcome">
                        <div class="welcome-icon">👋</div>
                        <h3>Hi! I'm your AI Python Tutor</h3>
                        <p>Ask me anything about Python programming, and I'll help you learn!</p>
                        <div class="welcome-suggestions">
                            <button class="suggestion-btn" data-message="Explain what variables are in Python">What are variables?</button>
                            <button class="suggestion-btn" data-message="How do I use loops in Python?">How do loops work?</button>
                            <button class="suggestion-btn" data-message="What's the difference between lists and tuples?">Lists vs Tuples?</button>
                        </div>
                    </div>
                </div>
                
                <div class="chatbot-typing" id="chatbot-typing" style="display: none;">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="typing-text">AI is thinking...</span>
                </div>
                
                <div class="chatbot-input-container">
                    <textarea 
                        id="chatbot-input" 
                        class="chatbot-input" 
                        placeholder="Ask me anything about Python..."
                        rows="1"
                    ></textarea>
                    <button id="chatbot-send" class="chatbot-send-btn" title="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        // Add to body
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        
        // Add styles
        this.addStyles();
    }
    
    addStyles() {
        const styles = `
            <style>
                .chatbot-toggle {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    width: 56px;
                    height: 56px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    color: white;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                    z-index: 9998;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .chatbot-toggle:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                }
                
                .chatbot-badge {
                    position: absolute;
                    top: -4px;
                    right: -4px;
                    background: #ef4444;
                    color: white;
                    border-radius: 10px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-weight: 600;
                }
                
                .chatbot-window {
                    position: fixed;
                    bottom: 90px;
                    right: 24px;
                    width: 400px;
                    height: 600px;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideUp 0.3s ease;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .chatbot-window.chatbot-expanded {
                    width: 700px;
                    height: 80vh;
                    bottom: 20px;
                    right: 20px;
                }
                
                .chatbot-history-sidebar {
                    position: absolute;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    width: 280px;
                    background: #f9fafb;
                    border-right: 1px solid #e5e7eb;
                    z-index: 10;
                    transform: translateX(-100%);
                    transition: transform 0.3s ease;
                    display: flex;
                    flex-direction: column;
                }
                
                .chatbot-history-sidebar.show {
                    transform: translateX(0);
                }
                
                .history-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.75rem;
                    border-bottom: 1px solid #e5e7eb;
                    background: white;
                    min-height: 48px;
                    gap: 0.5rem;
                }
                
                .history-header h3 {
                    margin: 0;
                    font-size: 0.95rem;
                    color: #1f2937;
                    flex: 1;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .history-header button {
                    flex-shrink: 0;
                }
                
                .history-list {
                    flex: 1;
                    overflow-y: auto;
                    padding: 0.5rem;
                }
                
                .history-item {
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    transition: all 0.2s;
                    display: flex;
                    align-items: flex-start;
                    gap: 0.5rem;
                    min-width: 0;
                    overflow: hidden;
                }
                
                .history-item:hover {
                    border-color: #667eea;
                    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
                }
                
                .history-item-content {
                    flex: 1;
                    cursor: pointer;
                    min-width: 0;
                    overflow: hidden;
                }
                
                .history-delete-btn {
                    padding: 0.5rem;
                    background: transparent;
                    border: none;
                    color: #ef4444;
                    cursor: pointer;
                    border-radius: 4px;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                
                .history-delete-btn:hover {
                    background: #fee2e2;
                }
                
                .history-item.active {
                    border-color: #667eea;
                    background: #f0f4ff;
                }
                
                .history-item-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.25rem;
                    gap: 0.5rem;
                    min-width: 0;
                }
                
                .history-item-context {
                    font-size: 0.75rem;
                    font-weight: 600;
                    color: #667eea;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    flex-shrink: 1;
                    min-width: 0;
                }
                
                .history-item-date {
                    font-size: 0.7rem;
                    color: #6b7280;
                    white-space: nowrap;
                    flex-shrink: 0;
                }
                
                .history-item-preview {
                    font-size: 0.8rem;
                    color: #4b5563;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    word-break: break-word;
                }
                
                .history-loading {
                    text-align: center;
                    padding: 2rem;
                    color: #6b7280;
                }
                
                .history-empty {
                    text-align: center;
                    padding: 2rem;
                    color: #9ca3af;
                }
                
                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .chatbot-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .chatbot-header-left {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .chatbot-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                }
                
                .chatbot-title {
                    font-weight: 600;
                    font-size: 16px;
                }
                
                .chatbot-status {
                    font-size: 12px;
                    opacity: 0.9;
                }
                
                .chatbot-header-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .chatbot-icon-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }
                
                .chatbot-icon-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                /* History header buttons - styled for visibility on white background */
                .history-header .chatbot-icon-btn {
                    background: rgba(239, 68, 68, 0.15) !important;
                    color: #ef4444 !important;
                    width: 28px !important;
                    height: 28px !important;
                    border: 1px solid rgba(239, 68, 68, 0.3) !important;
                }
                
                .history-header .chatbot-icon-btn:hover {
                    background: #ef4444 !important;
                    color: white !important;
                    border-color: #ef4444 !important;
                    transform: scale(1.05) !important;
                }
                
                .chatbot-context {
                    background: #fef3c7;
                    color: #92400e;
                    padding: 8px 16px;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 1px solid #fde68a;
                }
                
                .context-info {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .context-link {
                    color: #92400e;
                    text-decoration: none;
                    font-size: 12px;
                    padding: 4px 8px;
                    background: rgba(146, 64, 14, 0.1);
                    border-radius: 4px;
                    transition: all 0.2s;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    font-weight: 600;
                }
                
                .context-link:hover {
                    background: rgba(146, 64, 14, 0.2);
                }
                
                .chatbot-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                    background: #f9fafb;
                }
                
                .chatbot-messages::-webkit-scrollbar {
                    width: 6px;
                }
                
                .chatbot-messages::-webkit-scrollbar-thumb {
                    background: #d1d5db;
                    border-radius: 3px;
                }
                
                .chatbot-welcome {
                    text-align: center;
                    padding: 32px 16px;
                }
                
                .welcome-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                }
                
                .chatbot-welcome h3 {
                    color: #1f2937;
                    margin-bottom: 8px;
                    font-size: 18px;
                }
                
                .chatbot-welcome p {
                    color: #6b7280;
                    margin-bottom: 20px;
                    font-size: 14px;
                }
                
                .welcome-suggestions {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                
                .suggestion-btn {
                    background: white;
                    border: 1px solid #e5e7eb;
                    padding: 10px 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 13px;
                    color: #4b5563;
                    transition: all 0.2s;
                    text-align: left;
                }
                
                .suggestion-btn:hover {
                    border-color: #667eea;
                    color: #667eea;
                    background: #f5f7ff;
                }
                
                .chat-message {
                    margin-bottom: 16px;
                    animation: fadeIn 0.3s ease;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .message-user {
                    display: flex;
                    justify-content: flex-end;
                }
                
                .message-assistant {
                    display: flex;
                    justify-content: flex-start;
                }
                
                .message-bubble {
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 14px;
                    line-height: 1.5;
                }
                
                .message-user .message-bubble {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-bottom-right-radius: 4px;
                }
                
                .message-assistant .message-bubble {
                    background: white;
                    color: #1f2937;
                    border: 1px solid #e5e7eb;
                    border-bottom-left-radius: 4px;
                }
                
                .message-assistant .message-bubble pre {
                    background: #f3f4f6;
                    padding: 8px;
                    border-radius: 6px;
                    overflow-x: auto;
                    margin: 8px 0;
                }
                
                .message-assistant .message-bubble code {
                    background: #f3f4f6;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Fira Code', monospace;
                    font-size: 13px;
                }
                
                .message-timestamp {
                    font-size: 11px;
                    color: #9ca3af;
                    margin-top: 4px;
                }
                
                .chatbot-typing {
                    padding: 8px 16px;
                    background: white;
                    border-top: 1px solid #e5e7eb;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .typing-indicator {
                    display: flex;
                    gap: 4px;
                }
                
                .typing-indicator span {
                    width: 6px;
                    height: 6px;
                    background: #667eea;
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }
                
                .typing-indicator span:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .typing-indicator span:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                @keyframes typing {
                    0%, 60%, 100% { transform: translateY(0); }
                    30% { transform: translateY(-8px); }
                }
                
                .typing-text {
                    font-size: 13px;
                    color: #6b7280;
                }
                
                .chatbot-input-container {
                    background: white;
                    border-top: 1px solid #e5e7eb;
                    padding: 12px;
                    display: flex;
                    gap: 8px;
                    align-items: flex-end;
                }
                
                .chatbot-input {
                    flex: 1;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 10px 12px;
                    font-size: 14px;
                    resize: none;
                    max-height: 100px;
                    font-family: inherit;
                }
                
                .chatbot-input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                
                .chatbot-send-btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.2s;
                }
                
                .chatbot-send-btn:hover:not(:disabled) {
                    transform: scale(1.05);
                }
                
                .chatbot-send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                /* Mobile and Touch Optimizations */
                @media (max-width: 768px) {
                    .chatbot-window {
                        width: calc(100vw - 48px);
                        height: calc(100vh - 120px);
                        bottom: 80px;
                        right: 24px;
                        left: 24px;
                        max-width: none;
                    }
                    
                    .chatbot-window.chatbot-expanded {
                        width: calc(100vw - 48px);
                        height: calc(100vh - 100px);
                        bottom: 20px;
                        right: 24px;
                        left: 24px;
                    }
                    
                    .chatbot-history-sidebar {
                        width: 100%;
                        max-width: 320px;
                    }
                    
                    .chatbot-toggle {
                        width: 56px;
                        height: 56px;
                        bottom: 20px;
                        right: 20px;
                    }
                    
                    .chatbot-header {
                        padding: 0.75rem;
                    }
                    
                    .chatbot-input-container {
                        padding: 0.75rem;
                    }
                    
                    .chatbot-input {
                        font-size: 16px; /* Prevents zoom on iOS */
                        min-height: 44px; /* Touch target size */
                    }
                    
                    .chatbot-send-btn {
                        width: 44px;
                        height: 44px;
                        min-width: 44px;
                    }
                    
                    .chatbot-icon-btn {
                        width: 40px;
                        height: 40px;
                        min-width: 40px;
                    }
                    
                    .suggestion-btn {
                        padding: 0.75rem 1rem;
                        font-size: 0.875rem;
                        min-height: 44px;
                    }
                }
                
                @media (max-width: 480px) {
                    .chatbot-window {
                        width: calc(100vw - 32px);
                        left: 16px;
                        right: 16px;
                        bottom: 70px;
                    }
                    
                    .chatbot-window.chatbot-expanded {
                        width: calc(100vw - 32px);
                        left: 16px;
                        right: 16px;
                        height: calc(100vh - 80px);
                    }
                    
                    .chatbot-toggle {
                        width: 52px;
                        height: 52px;
                        bottom: 16px;
                        right: 16px;
                    }
                    
                    .chatbot-header {
                        padding: 0.625rem;
                    }
                    
                    .chatbot-title {
                        font-size: 0.875rem;
                    }
                    
                    .chatbot-status {
                        font-size: 0.75rem;
                    }
                    
                    .chatbot-messages {
                        padding: 0.75rem;
                    }
                    
                    .message {
                        padding: 0.75rem;
                        font-size: 0.875rem;
                    }
                    
                    .chatbot-input-container {
                        padding: 0.625rem;
                    }
                }
                
                /* Touch device optimizations */
                @media (hover: none) and (pointer: coarse) {
                    .chatbot-toggle:hover {
                        transform: none;
                    }
                    
                    .chatbot-toggle:active {
                        transform: scale(0.95);
                    }
                    
                    .chatbot-icon-btn:hover {
                        background: transparent;
                    }
                    
                    .chatbot-icon-btn:active {
                        background: rgba(0, 0, 0, 0.1);
                        transform: scale(0.95);
                    }
                    
                    .suggestion-btn:hover {
                        transform: none;
                    }
                    
                    .suggestion-btn:active {
                        transform: scale(0.98);
                    }
                    
                    /* Prevent double-tap zoom */
                    .chatbot-toggle,
                    .chatbot-icon-btn,
                    .chatbot-send-btn,
                    .suggestion-btn {
                        touch-action: manipulation;
                    }
                }
                
                @media (max-width: 768px) {
                    .chatbot-window {
                        width: calc(100vw - 32px);
                        height: calc(100vh - 120px);
                        right: 16px;
                        bottom: 80px;
                    }
                    
                    .chatbot-window.chatbot-expanded {
                        width: calc(100vw - 16px);
                        height: calc(100vh - 100px);
                        right: 8px;
                        bottom: 70px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    attachEventListeners() {
        // Toggle button
        document.getElementById('chatbot-toggle').addEventListener('click', () => {
            this.toggleWindow();
        });
        
        // Close button
        document.getElementById('chatbot-close').addEventListener('click', () => {
            this.closeWindow();
        });
        
        // History button
        document.getElementById('chatbot-history').addEventListener('click', () => {
            this.toggleHistory();
        });
        
        // History close button
        document.getElementById('history-close').addEventListener('click', () => {
            this.toggleHistory();
        });
        
        // Expand/Collapse button
        document.getElementById('chatbot-expand').addEventListener('click', () => {
            this.toggleExpand();
        });
        
        // New conversation button
        document.getElementById('chatbot-new').addEventListener('click', () => {
            this.newConversation();
        });
        
        // Send button
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Input enter key
        document.getElementById('chatbot-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        document.getElementById('chatbot-input').addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        });
        
        // Suggestion buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const message = e.target.dataset.message;
                document.getElementById('chatbot-input').value = message;
                this.sendMessage();
            }
        });
    }
    
    toggleWindow() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbot-window');
        window.style.display = this.isOpen ? 'flex' : 'none';
        
        if (this.isOpen) {
            document.getElementById('chatbot-input').focus();
        }
    }
    
    closeWindow() {
        this.isOpen = false;
        document.getElementById('chatbot-window').style.display = 'none';
    }
    
    toggleExpand() {
        this.isExpanded = !this.isExpanded;
        const window = document.getElementById('chatbot-window');
        const expandBtn = document.getElementById('chatbot-expand');
        
        if (this.isExpanded) {
            window.classList.add('chatbot-expanded');
            expandBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="4 14 10 14 10 20"></polyline>
                    <polyline points="20 10 14 10 14 4"></polyline>
                    <line x1="14" y1="10" x2="21" y2="3"></line>
                    <line x1="3" y1="21" x2="10" y2="14"></line>
                </svg>
            `;
            expandBtn.title = 'Collapse';
        } else {
            window.classList.remove('chatbot-expanded');
            expandBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <polyline points="9 21 3 21 3 15"></polyline>
                    <line x1="21" y1="3" x2="14" y2="10"></line>
                    <line x1="3" y1="21" x2="10" y2="14"></line>
                </svg>
            `;
            expandBtn.title = 'Expand';
        }
    }
    
    toggleHistory() {
        const sidebar = document.getElementById('chatbot-history-sidebar');
        console.log('Toggle history - sidebar:', sidebar);
        
        if (!sidebar) {
            console.error('History sidebar not found!');
            return;
        }
        
        const isShowing = sidebar.classList.contains('show');
        console.log('Is showing:', isShowing);
        
        if (isShowing) {
            sidebar.classList.remove('show');
        } else {
            sidebar.classList.add('show');
            this.loadHistory();
        }
    }
    
    async loadHistory() {
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '<div class="history-loading">Loading conversations...</div>';
        
        try {
            const response = await fetch('/api/chatbot/history/');
            const data = await response.json();
            
            if (data.success && data.conversations.length > 0) {
                // Filter out conversations without messages
                const conversationsWithMessages = data.conversations.filter(conv => conv.last_message);
                
                if (conversationsWithMessages.length === 0) {
                    historyList.innerHTML = '<div class="history-empty">No conversations yet</div>';
                    return;
                }
                
                historyList.innerHTML = conversationsWithMessages.map(conv => {
                    const contextLabel = this.getContextLabel(conv.context_type, conv.context_id);
                    const date = new Date(conv.updated_at).toLocaleDateString('tr-TR', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    const preview = conv.last_message;
                    const isActive = conv.id === this.conversationId;
                    
                    return `
                        <div class="history-item ${isActive ? 'active' : ''}" data-conversation-id="${conv.id}" data-context-type="${conv.context_type || ''}" data-context-id="${conv.context_id || ''}">
                            <div class="history-item-content">
                                <div class="history-item-header">
                                    <span class="history-item-context">${contextLabel}</span>
                                    <span class="history-item-date">${date}</span>
                                </div>
                                <div class="history-item-preview">${preview}</div>
                            </div>
                            <button class="history-delete-btn" data-conversation-id="${conv.id}" title="Delete conversation">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                            </button>
                        </div>
                    `;
                }).join('');
                
                // Attach click handlers
                document.querySelectorAll('.history-item').forEach(item => {
                    // Click on item content to load conversation
                    const content = item.querySelector('.history-item-content');
                    content.addEventListener('click', () => {
                        const convId = parseInt(item.dataset.conversationId);
                        const contextType = item.dataset.contextType || null;
                        const contextId = item.dataset.contextId ? parseInt(item.dataset.contextId) : null;
                        this.loadConversationById(convId, contextType, contextId);
                    });
                });
                
                // Attach delete handlers
                document.querySelectorAll('.history-delete-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const convId = parseInt(btn.dataset.conversationId);
                        this.deleteConversation(convId);
                    });
                });
            } else {
                historyList.innerHTML = '<div class="history-empty">No conversations yet</div>';
            }
        } catch (error) {
            console.error('Error loading history:', error);
            historyList.innerHTML = '<div class="history-empty">Failed to load history</div>';
        }
    }
    
    getContextLabel(contextType, contextId) {
        if (!contextType || contextType === 'general') {
            return '💬 General';
        } else if (contextType === 'lesson') {
            return `📚 Lesson ${contextId}`;
        } else if (contextType === 'exercise') {
            return `💻 Exercise ${contextId}`;
        }
        return '💬 Chat';
    }
    
    async loadConversationById(conversationId, contextType, contextId) {
        console.log('[Chatbot] Loading conversation:', { conversationId, contextType, contextId });
        
        this.conversationId = conversationId;
        this.contextType = contextType || 'general';
        this.contextId = contextId;
        
        // Update active state in history
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('active');
        
        // Load messages directly by conversation ID
        try {
            const response = await fetch(`/api/chatbot/history/${conversationId}/`);
            const data = await response.json();
            
            if (data.success) {
                // Update context from conversation data
                this.contextType = data.conversation.context_type || 'general';
                this.contextId = data.conversation.context_id || null;
                
                // Display messages
                this.displayMessages(data.messages);
                this.updateContextBadge();
            } else {
                console.error('Failed to load conversation:', data.error);
                alert('Failed to load conversation: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
            alert('Network error. Please try again.');
        }
        
        // Close history sidebar
        this.toggleHistory();
    }
    
    async deleteConversation(conversationId) {
        if (!confirm('Are you sure you want to delete this conversation?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/chatbot/delete/${conversationId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Remove from UI
                const item = document.querySelector(`[data-conversation-id="${conversationId}"]`);
                if (item) {
                    item.remove();
                }
                
                // If deleted current conversation, start new one
                if (this.conversationId === conversationId) {
                    this.conversationId = null;
                    const container = document.getElementById('chatbot-messages');
                    container.innerHTML = `
                        <div class="chatbot-welcome">
                            <div class="welcome-icon">👋</div>
                            <h3>New Conversation Started</h3>
                            <p>Ask me anything about Python programming!</p>
                        </div>
                    `;
                }
                
                // Check if history is empty
                const historyList = document.getElementById('history-list');
                if (historyList.children.length === 0) {
                    historyList.innerHTML = '<div class="history-empty">No conversations yet</div>';
                }
            } else {
                alert('Failed to delete conversation: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            alert('Network error. Please try again.');
        }
    }
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    async loadConversation() {
        // If we have a conversation ID, load it directly
        if (this.conversationId) {
            try {
                const response = await fetch(`/api/chatbot/history/${this.conversationId}/`);
                const data = await response.json();
                
                if (data.success) {
                    this.conversationId = data.conversation.id;
                    this.contextType = data.conversation.context_type || 'general';
                    this.contextId = data.conversation.context_id || null;
                    this.displayMessages(data.messages);
                    this.updateContextBadge();
                } else {
                    this.updateContextBadge();
                }
            } catch (error) {
                console.error('Error loading conversation:', error);
                this.updateContextBadge();
            }
        } 
        // If we have context but no conversation ID, try to get/create context conversation
        else if (this.contextType !== 'general' && this.contextId) {
            try {
                const response = await fetch(`/api/chatbot/context/${this.contextType}/${this.contextId}/`);
                const data = await response.json();
                
                if (data.success) {
                    this.conversationId = data.conversation.id;
                    this.displayMessages(data.messages);
                    this.updateContextBadge();
                } else {
                    // Even if no conversation exists, update the badge to show context
                    this.updateContextBadge();
                }
            } catch (error) {
                console.error('Error loading conversation:', error);
                // Even on error, update the badge to show context
                this.updateContextBadge();
            }
        } else {
            // No context, hide badge
            this.updateContextBadge();
        }
    }
    
    updateContextBadge() {
        const contextDiv = document.getElementById('chatbot-context');
        const contextText = document.getElementById('context-text');
        const contextLink = document.getElementById('context-link');
        
        if (this.contextType !== 'general' && this.contextId) {
            contextDiv.style.display = 'flex';
            const icon = this.contextType === 'lesson' ? '📚' : '💻';
            contextText.innerHTML = `<span style="margin-right: 4px;">${icon}</span>Context: ${this.contextType.charAt(0).toUpperCase() + this.contextType.slice(1)} ${this.contextId}`;
            
            // Check if we're already on the context page
            const currentPath = window.location.pathname;
            const contextPath = this.contextType === 'lesson' ? `/lesson/${this.contextId}/` : `/exercise/${this.contextId}/`;
            const isOnContextPage = currentPath === contextPath;
            
            // Only show link if we're NOT on the context page
            if (!isOnContextPage) {
                contextLink.href = contextPath;
                contextLink.style.display = 'inline-flex';
            } else {
                contextLink.style.display = 'none';
            }
        } else {
            contextDiv.style.display = 'none';
            contextLink.style.display = 'none';
        }
    }
    
    displayMessages(messages) {
        const container = document.getElementById('chatbot-messages');
        
        // Clear welcome message if there are messages
        if (messages.length > 0) {
            container.innerHTML = '';
        }
        
        messages.forEach(msg => {
            this.addMessageToUI(msg.role, msg.content, msg.timestamp);
        });
        
        this.scrollToBottom();
    }
    
    addMessageToUI(role, content, timestamp = null) {
        const container = document.getElementById('chatbot-messages');
        
        // Remove welcome message if exists
        const welcome = container.querySelector('.chatbot-welcome');
        if (welcome) {
            welcome.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message message-${role}`;
        
        // Parse markdown-style code blocks
        const formattedContent = this.formatMessage(content);
        
        const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-bubble">
                ${formattedContent}
                <div class="message-timestamp">${timeStr}</div>
            </div>
        `;
        
        container.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Simple markdown formatting
        // Convert ```python code blocks
        content = content.replace(/```python\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        content = content.replace(/```\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Convert inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert bold
        content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isLoading) return;
        
        // Add user message to UI
        this.addMessageToUI('user', message);
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Show typing indicator
        this.showTyping();
        
        // Send to API
        try {
            const requestData = {
                message: message,
                context_type: this.contextType,
                context_id: this.contextId,
                conversation_id: this.conversationId
            };
            
            // Debug: Log context info
            console.log('[Chatbot] Sending message with context:', {
                context_type: this.contextType,
                context_id: this.contextId,
                message: message.substring(0, 50) + '...'
            });
            
            const response = await fetch('/api/chatbot/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.conversationId = data.conversation_id;
                this.addMessageToUI('assistant', data.message);
                // Update context badge after sending message (in case context was set)
                this.updateContextBadge();
                
                // Reload history to show new conversation if it's new
                if (document.getElementById('chatbot-history-sidebar')?.classList.contains('show')) {
                    this.loadHistory();
                }
            } else {
                this.addMessageToUI('assistant', '❌ ' + (data.error || 'An error occurred'));
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToUI('assistant', '❌ Network error. Please try again.');
        } finally {
            this.hideTyping();
        }
    }
    
    showTyping() {
        this.isLoading = true;
        document.getElementById('chatbot-typing').style.display = 'flex';
        document.getElementById('chatbot-send').disabled = true;
    }
    
    hideTyping() {
        this.isLoading = false;
        document.getElementById('chatbot-typing').style.display = 'none';
        document.getElementById('chatbot-send').disabled = false;
    }
    
    scrollToBottom() {
        const container = document.getElementById('chatbot-messages');
        container.scrollTop = container.scrollHeight;
    }
    
    async newConversation() {
        if (confirm('Start a new conversation? Current chat will be saved.')) {
            try {
                // Create new conversation via API
                const response = await fetch('/api/chatbot/new/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        context_type: this.contextType,
                        context_id: this.contextId
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.conversationId = data.conversation_id;
                    this.contextType = data.context_type || 'general';
                    this.contextId = data.context_id || null;
                    
                    const container = document.getElementById('chatbot-messages');
                    container.innerHTML = `
                        <div class="chatbot-welcome">
                            <div class="welcome-icon">👋</div>
                            <h3>New Conversation Started</h3>
                            <p>Ask me anything about Python programming!</p>
                        </div>
                    `;
                    
                    this.updateContextBadge();
                    
                    // Reload history to show new conversation
                    if (document.getElementById('chatbot-history-sidebar')?.classList.contains('show')) {
                        this.loadHistory();
                    }
                } else {
                    alert('Failed to create new conversation: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error creating new conversation:', error);
                // Fallback: just clear UI
                this.conversationId = null;
                const container = document.getElementById('chatbot-messages');
                container.innerHTML = `
                    <div class="chatbot-welcome">
                        <div class="welcome-icon">👋</div>
                        <h3>New Conversation Started</h3>
                        <p>Ask me anything about Python programming!</p>
                    </div>
                `;
                this.updateContextBadge();
            }
        }
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ChatbotWidget();
    });
} else {
    new ChatbotWidget();
}

