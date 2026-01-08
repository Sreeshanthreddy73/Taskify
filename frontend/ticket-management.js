// Interactive Ticket Management JavaScript
// This file extends app.js with ticket management features

// API Configuration - use shared global
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';

let expandedTicketId = null;
let ticketFilters = {
    action: 'all',
    status: 'all',
    search: ''
};

// ============================================================================
// TICKET RENDERING WITH EXPANDABLE DETAILS
// ============================================================================
function renderTickets(tickets) {
    const container = document.getElementById('ticketsContainer');
    const countBadge = document.getElementById('ticketCount');
    const headerTitle = document.querySelector('.actions-section .section-header h2');

    // Update badge count
    if (countBadge) {
        countBadge.textContent = tickets ? tickets.length : 0;
    }

    // Update header title with context
    if (headerTitle) {
        if (window.currentDisruptionId && window.currentDisruption) {
            headerTitle.textContent = `Tickets: ${window.currentDisruption.location.split(',')[0]}`;
        } else {
            headerTitle.textContent = 'Action Tickets';
        }
    }

    if (!tickets || tickets.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No action tickets yet</p>
                <p class="empty-hint">Process a disruption to generate action tickets</p>
            </div>
        `;
        return;
    }

    // Apply filters
    const filteredTickets = filterTickets(tickets);

    container.innerHTML = filteredTickets.map(ticket => {
        // Use destination from backend
        const destination = ticket.destination || 'Unknown';

        return `
        <div class="ticket-card ${ticket.id === expandedTicketId ? 'expanded' : ''}" data-ticket-id="${ticket.id}">
            <div class="ticket-header" onclick="toggleTicketExpansion('${ticket.id}')">
                <div class="ticket-main-info">
                    <div class="ticket-id-row">
                        <span class="ticket-id">${ticket.id}</span>
                        <span class="ticket-badge ticket-badge-${ticket.action}">${ticket.action.toUpperCase()}</span>
                        <span class="ticket-status status-${ticket.status}">${formatStatus(ticket.status)}</span>
                    </div>
                    <div class="ticket-shipment">
                        <span class="shipment-id">${ticket.shipment_id}</span>
                        <span class="shipment-arrow">→</span>
                        <span class="shipment-destination">${destination}</span>
                    </div>
                </div>
                <button class="expand-icon">${ticket.id === expandedTicketId ? '▼' : '▶'}</button>
            </div>
            
            ${ticket.id === expandedTicketId ? renderTicketDetails(ticket) : ''}
        </div>
    `;
    }).join('');
}

function renderTicketDetails(ticket) {
    const canApprove = ticket.status === 'pending';
    const canStart = ticket.status === 'approved';
    const canComplete = ticket.status === 'in_progress';

    return `
        <div class="ticket-details">
            <div class="ticket-section">
                <h4>Decision Details</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Reasoning:</span>
                        <span class="detail-value">${ticket.decision.reasoning}</span>
                    </div>
                    ${ticket.decision.estimated_cost_impact !== null ? `
                        <div class="detail-item">
                            <span class="detail-label">Cost Impact:</span>
                            <span class="detail-value">+${ticket.decision.estimated_cost_impact.toFixed(1)}%</span>
                        </div>
                    ` : ''}
                    ${ticket.decision.estimated_delay_hours !== null ? `
                        <div class="detail-item">
                            <span class="detail-label">Estimated Delay:</span>
                            <span class="detail-value">${ticket.decision.estimated_delay_hours} hours</span>
                        </div>
                    ` : ''}
                    ${ticket.decision.alternative_route_id ? `
                        <div class="detail-item">
                            <span class="detail-label">Alternative Route:</span>
                            <span class="detail-value">${ticket.decision.alternative_route_id}</span>
                        </div>
                    ` : ''}
                    <div class="detail-item">
                        <span class="detail-label">Confidence:</span>
                        <span class="detail-value">${(ticket.decision.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
            
            <div class="ticket-section">
                <h4>Explanation</h4>
                <div class="ticket-explanation">${formatExplanation(ticket.explanation)}</div>
            </div>
            
            ${ticket.assigned_to ? `
                <div class="ticket-section">
                    <h4>Assignment</h4>
                    <p>Assigned to: <strong>${ticket.assigned_to}</strong></p>
                </div>
            ` : ''}
            
            ${ticket.notes && ticket.notes.length > 0 ? `
                <div class="ticket-section">
                    <h4>Notes</h4>
                    <div class="ticket-notes">
                        ${ticket.notes.map(note => `
                            <div class="ticket-note">
                                <div class="note-header">
                                    <strong>${note.author}</strong>
                                    <span class="note-time">${formatTimestamp(note.timestamp)}</span>
                                </div>
                                <div class="note-content">${note.content}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div class="ticket-actions">
                ${canApprove ? `
                    <button class="ticket-btn btn-approve" onclick="approveTicket('${ticket.id}')">
                        ✓ Approve
                    </button>
                    <button class="ticket-btn btn-reject" onclick="rejectTicket('${ticket.id}')">
                        ✗ Reject
                    </button>
                ` : ''}
                ${canStart ? `
                    <button class="ticket-btn btn-start" onclick="startTicket('${ticket.id}')">
                        ▶ Start
                    </button>
                ` : ''}
                ${canComplete ? `
                    <button class="ticket-btn btn-complete" onclick="completeTicket('${ticket.id}')">
                        ✓ Complete
                    </button>
                ` : ''}
                <button class="ticket-btn btn-note" onclick="addNote('${ticket.id}')">
                    📝 Add Note
                </button>
            </div>
        </div>
    `;
}

// ============================================================================
// TICKET ACTIONS
// ============================================================================
async function approveTicket(ticketId) {
    try {
        const operator = JSON.parse(sessionStorage.getItem('operator'));
        const response = await fetch(`${window.API_BASE_URL}/tickets/${ticketId}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operator_id: operator.id })
        });

        if (!response.ok) throw new Error('Failed to approve ticket');

        await loadTickets();
    } catch (error) {
        console.error('Error approving ticket:', error);
        alert('Failed to approve ticket');
    }
}

async function rejectTicket(ticketId) {
    const reason = prompt('Reason for rejection:');
    if (!reason) return;

    try {
        const operator = JSON.parse(sessionStorage.getItem('operator'));
        const response = await fetch(`${window.API_BASE_URL}/tickets/${ticketId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operator_id: operator.id, reason })
        });

        if (!response.ok) throw new Error('Failed to reject ticket');

        await loadTickets();
    } catch (error) {
        console.error('Error rejecting ticket:', error);
        alert('Failed to reject ticket');
    }
}

async function startTicket(ticketId) {
    try {
        const operator = JSON.parse(sessionStorage.getItem('operator'));
        const response = await fetch(`${window.API_BASE_URL}/tickets/${ticketId}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operator_id: operator.id })
        });

        if (!response.ok) throw new Error('Failed to start ticket');

        await loadTickets();
    } catch (error) {
        console.error('Error starting ticket:', error);
        alert('Failed to start ticket');
    }
}

async function completeTicket(ticketId) {
    const notes = prompt('Completion notes (optional):');

    try {
        const operator = JSON.parse(sessionStorage.getItem('operator'));
        const response = await fetch(`${window.API_BASE_URL}/tickets/${ticketId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operator_id: operator.id, notes })
        });

        if (!response.ok) throw new Error('Failed to complete ticket');

        await loadTickets();
    } catch (error) {
        console.error('Error completing ticket:', error);
        alert('Failed to complete ticket');
    }
}

async function addNote(ticketId) {
    const content = prompt('Add a note:');
    if (!content) return;

    try {
        const operator = JSON.parse(sessionStorage.getItem('operator'));
        const response = await fetch(`${window.API_BASE_URL}/tickets/${ticketId}/notes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author: operator.name, content })
        });

        if (!response.ok) throw new Error('Failed to add note');

        await loadTickets();
    } catch (error) {
        console.error('Error adding note:', error);
        alert('Failed to add note');
    }
}

// ============================================================================
// FILTERING & SORTING
// ============================================================================
function filterTickets(tickets) {
    return tickets.filter(ticket => {
        // Filter by action type
        if (ticketFilters.action !== 'all' && ticket.action !== ticketFilters.action) {
            return false;
        }

        // Filter by status
        if (ticketFilters.status !== 'all' && ticket.status !== ticketFilters.status) {
            return false;
        }

        // Filter by search
        if (ticketFilters.search) {
            const searchLower = ticketFilters.search.toLowerCase();
            return ticket.id.toLowerCase().includes(searchLower) ||
                ticket.shipment_id.toLowerCase().includes(searchLower);
        }

        return true;
    });
}

function updateFilter(filterType, value) {
    ticketFilters[filterType] = value;
    loadTickets();
}

// ============================================================================
// EXPORT FUNCTIONALITY
// ============================================================================
async function exportTickets(format) {
    try {
        const response = await fetch(`${window.API_BASE_URL}/tickets`);
        const tickets = await response.json();

        if (format === 'csv') {
            exportToCSV(tickets);
        } else if (format === 'json') {
            exportToJSON(tickets);
        }
    } catch (error) {
        console.error('Error exporting tickets:', error);
        alert('Failed to export tickets');
    }
}

function exportToCSV(tickets) {
    const headers = ['ID', 'Disruption', 'Shipment', 'Action', 'Status', 'Created', 'Assigned To'];
    const rows = tickets.map(t => [
        t.id,
        t.disruption_id,
        t.shipment_id,
        t.action,
        t.status,
        new Date(t.created_at).toLocaleString(),
        t.assigned_to || 'Unassigned'
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    downloadFile(csv, 'tickets.csv', 'text/csv');
}

function exportToJSON(tickets) {
    const json = JSON.stringify(tickets, null, 2);
    downloadFile(json, 'tickets.json', 'application/json');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
function toggleTicketExpansion(ticketId) {
    expandedTicketId = expandedTicketId === ticketId ? null : ticketId;
    loadTickets();
}

function formatStatus(status) {
    return status.replace('_', ' ').toUpperCase();
}

function formatExplanation(text) {
    // Convert markdown-style bold to HTML
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

async function loadTickets() {
    try {
        // Use disruption-specific endpoint if a disruption is selected
        let url = `${window.API_BASE_URL}/tickets`;
        if (window.currentDisruptionId) {
            url = `${window.API_BASE_URL}/tickets/disruption/${window.currentDisruptionId}`;
            console.log(`Loading tickets for disruption: ${window.currentDisruptionId}`);
        } else {
            // If no disruption selected, clear tickets or show all
            renderTickets([]);
            return;
        }

        const response = await fetch(url);
        const tickets = await response.json();

        console.log(`Loaded ${tickets.length} tickets`);
        renderTickets(tickets);
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

function clearTickets() {
    window.currentDisruptionId = null;
    renderTickets([]);
}

// Helper function to get shipment destination (DEPRECATED: now handled by backend)
function getShipmentDestination(shipmentId) {
    return 'Unknown';
}
