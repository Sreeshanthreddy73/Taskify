// API Configuration
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';
const API_BASE_URL = window.API_BASE_URL;

// State Management
let currentDisruption = null;
let currentImpact = null;
let conversationState = 'idle'; // idle, waiting_for_response, processing
let currentOperator = null;

// ============================================================================
// SESSION & AUTHENTICATION
// ============================================================================
async function checkSession() {
    const operatorData = sessionStorage.getItem('operator');
    const sessionToken = sessionStorage.getItem('sessionToken');

    if (!operatorData || !sessionToken) {
        // No session data at all, redirect to login
        console.log('No session found in sessionStorage, redirecting to login');
        window.location.href = '/login.html';
        return false;
    }

    // We have session data, use it (don't verify with backend to avoid redirects)
    try {
        currentOperator = JSON.parse(operatorData);
        displayOperatorInfo(currentOperator);
        console.log('✅ Session loaded from sessionStorage:', currentOperator.name);
        return true;
    } catch (error) {
        console.error('Error parsing session data:', error);
        // Even if parsing fails, don't redirect - just use default values
        currentOperator = { id: 'UNKNOWN', name: 'Operator', role: 'user' };
        displayOperatorInfo(currentOperator);
        return true;
    }
}

function displayOperatorInfo(operator) {
    // Get initials
    const nameParts = operator.name.split(' ');
    const initials = nameParts.map(part => part[0]).join('').toUpperCase();

    // Update UI
    document.getElementById('operatorInitials').textContent = initials;
    document.getElementById('operatorName').textContent = operator.name;
    document.getElementById('operatorRole').textContent = operator.role;
}

async function logout() {
    const sessionToken = sessionStorage.getItem('sessionToken');

    if (sessionToken) {
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${sessionToken}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    // Clear session and redirect
    sessionStorage.clear();
    window.location.href = '/login.html';
}

// ============================================================================
// INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {
    // Check session first
    const sessionValid = await checkSession();
    if (!sessionValid) return;

    // Load disruptions and setup event listeners
    loadDisruptions();
    setupEventListeners();
});

function setupEventListeners() {
    // Severity filter
    document.getElementById('severityFilter').addEventListener('change', filterDisruptions);

    // Chat input
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendButton.disabled) {
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);

    // Logout button
    document.getElementById('logoutButton').addEventListener('click', logout);
}

// ============================================================================
// DISRUPTIONS
// ============================================================================
async function loadDisruptions() {
    const listElement = document.getElementById('disruptionsList');

    try {
        const response = await fetch(`${API_BASE_URL}/disruptions`);
        const disruptions = await response.json();

        listElement.innerHTML = '';

        disruptions.forEach(disruption => {
            const card = createDisruptionCard(disruption);
            listElement.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading disruptions:', error);
        listElement.innerHTML = `
            <div class="empty-state">
                <p>Failed to load disruptions</p>
                <span>${error.message}</span>
            </div>
        `;
    }
}

function createDisruptionCard(disruption) {
    const card = document.createElement('div');
    card.className = 'disruption-card';
    card.dataset.severity = disruption.severity;
    card.dataset.disruptionId = disruption.id;

    const timestamp = new Date(disruption.timestamp).toLocaleString();
    const duration = disruption.estimated_duration_hours || 'Unknown';

    card.innerHTML = `
        <div class="disruption-header">
            <span class="disruption-type">${disruption.type.replace('_', ' ')}</span>
            <span class="severity-badge">${disruption.severity}</span>
        </div>
        <div class="disruption-location">${disruption.location}</div>
        <div class="disruption-description">${disruption.description}</div>
        <div class="disruption-meta">
            <div class="disruption-meta-item">
                <span>⏰</span>
                <span>${timestamp}</span>
            </div>
            <div class="disruption-meta-item">
                <span>⏱️</span>
                <span>${duration}h</span>
            </div>
            <div class="disruption-meta-item">
                <span>🛣️</span>
                <span>${disruption.affected_routes.length} routes</span>
            </div>
        </div>
    `;

    card.addEventListener('click', () => selectDisruption(disruption));

    return card;
}

async function selectDisruption(disruption) {
    currentDisruption = disruption;

    // Set current disruption ID for ticket filtering
    window.currentDisruptionId = disruption.id;
    window.currentDisruption = disruption;

    // Highlight selected card
    document.querySelectorAll('.disruption-card').forEach(card => {
        card.style.borderColor = '';
    });
    event.currentTarget.style.borderColor = 'var(--color-accent-primary)';

    // Load tickets for this disruption
    if (typeof loadTickets === 'function') {
        loadTickets();
    }

    // Add message to chat
    addChatMessage('user', `Analyze disruption: ${disruption.location}`);

    // Get AI question
    try {
        const response = await fetch(`${API_BASE_URL}/conversation/question/${disruption.id}`);
        const data = await response.json();

        currentImpact = data.impact;
        window.currentImpact = data.impact;

        addChatMessage('assistant', data.message.content);

        // Enable chat input
        document.getElementById('chatInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
        document.getElementById('chatInput').placeholder = 'Type your response...';

        conversationState = 'waiting_for_response';
    } catch (error) {
        console.error('Error getting AI question:', error);
        addChatMessage('assistant', '❌ Failed to analyze disruption. Please try again.');
    }
}

function filterDisruptions() {
    const severity = document.getElementById('severityFilter').value;
    const cards = document.querySelectorAll('.disruption-card');

    cards.forEach(card => {
        if (severity === 'all' || card.dataset.severity === severity) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// ============================================================================
// CHAT
// ============================================================================
function addChatMessage(role, content) {
    const messagesContainer = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'assistant' ? 'AI' : 'You';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Parse markdown-style content
    const formattedContent = content
        .split('\n')
        .map(line => `<p>${line}</p>`)
        .join('');

    contentDiv.innerHTML = formattedContent;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || conversationState !== 'waiting_for_response') return;

    // Add user message
    addChatMessage('user', message);
    input.value = '';

    // Disable input while processing
    input.disabled = true;
    document.getElementById('sendButton').disabled = true;
    conversationState = 'processing';

    // Trigger notification
    if (window.notificationSystem) {
        window.notificationSystem.notifyStatus('started');
    }

    try {
        // Parse operator response
        const parseResponse = await fetch(`${API_BASE_URL}/conversation/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: message })
        });

        if (!parseResponse.ok) {
            throw new Error(`Parse failed: ${parseResponse.status}`);
        }

        const operatorResponse = await parseResponse.json();
        operatorResponse.disruption_id = currentDisruption.id;

        // Trigger in-progress notification
        if (window.notificationSystem) {
            window.notificationSystem.notifyStatus('in_progress');
        }

        // Get decisions and create tickets
        const ticketsResponse = await fetch(`${API_BASE_URL}/tickets/${currentDisruption.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(operatorResponse)
        });

        if (!ticketsResponse.ok) {
            const errorData = await ticketsResponse.json().catch(() => ({}));
            console.error('Tickets API error:', errorData);
            throw new Error(`Tickets failed: ${ticketsResponse.status}`);
        }

        const tickets = await ticketsResponse.json();

        // Get summary
        const summaryResponse = await fetch(`${API_BASE_URL}/summary/${currentDisruption.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(operatorResponse)
        });

        if (!summaryResponse.ok) {
            const errorData = await summaryResponse.json().catch(() => ({}));
            console.error('Summary API error:', errorData);
            throw new Error(`Summary failed: ${summaryResponse.status}`);
        }

        const summaryData = await summaryResponse.json();

        // Display summary (with null check)
        if (summaryData && summaryData.message && summaryData.message.content) {
            addChatMessage('assistant', summaryData.message.content);
        } else {
            addChatMessage('assistant', '✅ Decisions processed successfully. Check the Action Tickets panel.');
        }

        // Display tickets
        displayTickets(tickets);

        // Reset conversation state
        conversationState = 'idle';
        input.placeholder = 'Select another disruption...';

        // Trigger completed notification
        if (window.notificationSystem) {
            window.notificationSystem.notifyStatus('completed');
        }

    } catch (error) {
        console.error('Error processing message:', error);
        addChatMessage('assistant', `❌ ${error.message || 'Failed to process your response. Please try again.'}`);

        // Re-enable input
        input.disabled = false;
        document.getElementById('sendButton').disabled = false;
        conversationState = 'waiting_for_response';
    }
}

// ============================================================================
// ACTION TICKETS
// ============================================================================
function displayTickets(tickets) {
    // Rely on renderTickets from ticket-management.js to handle badge and header context
    if (typeof renderTickets === 'function') {
        renderTickets(tickets);
    } else {
        console.error('renderTickets function not found');
    }
}

// ============================================================================
// MODAL
// ============================================================================
function closeModal() {
    document.getElementById('impactModal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('impactModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'impactModal') {
        closeModal();
    }
});
