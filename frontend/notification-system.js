// Notification System for LogiTech
// Handles browser notifications, auto-refresh, and notification center

// API Configuration - use shared global
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.refreshInterval = 5 * 60 * 1000; // 5 minutes
        this.soundEnabled = true;
        this.lastTicketCheck = Date.now();
    }

    async init() {
        // Setup UI first so it's functional even if permissions are pending
        this.setupNotificationCenter();

        // Start auto-refresh
        this.startAutoRefresh();

        // Request notification permission (non-blocking)
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    notifyStatus(status) {
        let title, message, priority;

        switch (status) {
            case 'started':
                title = 'AI Analysis Started';
                message = 'Analyzing disruption impact...';
                priority = 'medium';
                break;
            case 'in_progress':
                title = 'Generating Options';
                message = 'Synchronizing response actions...';
                priority = 'medium';
                break;
            case 'completed':
                title = 'Analysis Complete';
                message = 'Response tickets are ready for review.';
                priority = 'high';
                break;
            default:
                return;
        }

        this.notify(title, message, priority);
        this.showToast(`${title}: ${message}`);
    }

    notify(title, message, priority = 'medium', ticketId = null) {
        // Add to notification center
        const notification = {
            id: Date.now(),
            read: false,
            timestamp: new Date(),
            title: title,
            message: message,
            priority: priority,
            ticketId: ticketId
        };
        this.notifications.unshift(notification);
        this.unreadCount++;

        // Update UI
        this.updateNotificationBadge();
        this.updateNotificationCenter();

        // Browser notification
        if (Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/favicon.ico'
            });
        }

        // Sound alert
        if (this.soundEnabled) {
            this.playSound(notification.priority);
        }
    }

    startAutoRefresh() {
        // Reduced interval for better demo experience
        this.refreshInterval = 30 * 1000;
        setInterval(async () => {
            await this.checkForUpdates();
        }, this.refreshInterval);
    }

    async checkForUpdates() {
        try {
            // Get all tickets
            const response = await fetch(`${window.API_BASE_URL}/tickets`);
            if (!response.ok) return;
            const tickets = await response.json();

            // Refresh ticket display if we are in a disruption view
            if (window.currentDisruptionId && typeof loadTickets === 'function') {
                // This will trigger a refresh of the tickets panel
                console.log('Auto-refreshing tickets...');
            }
        } catch (error) {
            console.error('Auto-refresh error:', error);
        }
    }

    notifyStatus(status) {
        const statuses = {
            'started': {
                title: 'Process Started',
                message: 'Analyzing disruption impact and evaluating routes...',
                priority: 'medium',
                icon: '🔍'
            },
            'in_progress': {
                title: 'In Progress',
                message: 'Generating optimized action tickets and strategy...',
                priority: 'medium',
                icon: '⚙️'
            },
            'completed': {
                title: 'Process Completed',
                message: 'Response strategy ready! Review action tickets in the panel.',
                priority: 'high',
                icon: '✅'
            }
        };

        const config = statuses[status];
        if (config) {
            this.notify({
                title: config.title,
                message: config.message,
                priority: config.priority,
                icon: config.icon
            });
        }
    }

    notify(notification) {
        // Add to notification center
        notification.id = Date.now();
        notification.read = false;
        notification.timestamp = new Date();
        this.notifications.unshift(notification);
        this.unreadCount++;

        // Update UI
        this.updateNotificationBadge();
        this.updateNotificationCenter();

        // Show toast
        this.showToast(notification.message);

        // Browser notification
        if (Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/favicon.ico'
            });
        }

        // Sound alert
        if (this.soundEnabled) {
            this.playSound(notification.priority);
        }
    }

    playSound(priority) {
        try {
            const context = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = context.createOscillator();
            const gainNode = context.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(context.destination);

            const frequencies = {
                urgent: 800,
                high: 600,
                medium: 400
            };
            oscillator.frequency.value = frequencies[priority] || 400;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.1, context.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.3);

            oscillator.start(context.currentTime);
            oscillator.stop(context.currentTime + 0.3);
        } catch (e) {
            console.log('Audio feedback suppressed by browser');
        }
    }

    setupNotificationCenter() {
        const bell = document.getElementById('notificationBell');
        const toggleSound = document.getElementById('toggleSound');
        const panel = document.getElementById('notificationPanel');

        if (!bell || !panel) {
            console.error('Notification elements not found');
            return;
        }

        // Use capture or direct click handler
        bell.onclick = (e) => {
            e.stopPropagation();
            this.toggleNotificationPanel();
        };

        if (toggleSound) {
            toggleSound.onclick = (e) => {
                e.stopPropagation();
                this.soundEnabled = !this.soundEnabled;
                this.showToast(this.soundEnabled ? 'Sound enabled' : 'Sound muted');
            };
        }

        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!panel.contains(e.target) && !bell.contains(e.target)) {
                panel.classList.remove('active');
            }
        });
    }

    toggleNotificationPanel() {
        const panel = document.getElementById('notificationPanel');
        if (!panel) return;

        const isActive = panel.classList.toggle('active');

        if (isActive) {
            this.markAllAsRead();
        }
    }

    updateNotificationBadge() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'flex' : 'none';
        }
    }

    updateNotificationCenter() {
        const list = document.getElementById('notificationList');
        if (!list) return;

        if (this.notifications.length === 0) {
            list.innerHTML = '<div class="empty-notifications">No notifications yet</div>';
            return;
        }

        list.innerHTML = this.notifications.map(n => `
            <div class="notification-item ${n.read ? 'read' : 'unread'} priority-${n.priority}" 
                 data-ticket-id="${n.ticketId}">
                <div class="notification-icon">
                    ${this.getNotificationIcon(n.priority)}
                </div>
                <div class="notification-content">
                    <div class="notification-title">${n.title}</div>
                    <div class="notification-message">${n.message}</div>
                    <div class="notification-time">${this.formatTime(n.timestamp)}</div>
                </div>
            </div>
        `).join('');

        // Add click handlers
        list.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const ticketId = item.dataset.ticketId;
                this.navigateToTicket(ticketId);
            });
        });
    }

    getNotificationIcon(priority) {
        const icons = {
            urgent: '🚨',
            high: '⚠️',
            medium: 'ℹ️'
        };
        return icons[priority] || 'ℹ️';
    }

    formatTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        const minutes = Math.floor(diff / 60000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        return time.toLocaleDateString();
    }

    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.unreadCount = 0;
        this.updateNotificationBadge();
        this.updateNotificationCenter();
    }

    navigateToTicket(ticketId) {
        // Expand the ticket
        expandedTicketId = ticketId;
        loadTickets();

        // Scroll to ticket
        setTimeout(() => {
            const ticketElement = document.querySelector(`[data-ticket-id="${ticketId}"]`);
            if (ticketElement) {
                ticketElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 300);

        // Close notification panel
        document.getElementById('notificationPanel').classList.remove('active');
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize notification system as a singleton on the window
// Initialize notification system
function initNotificationSystem() {
    if (!window.notificationSystem) {
        window.notificationSystem = new NotificationSystem();
        window.notificationSystem.init();
        console.log('Notification system initialized and ready');

        // Optional: Trigger a test notification if in dev mode
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('LogiTech: Notifications ready for testing.');
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotificationSystem);
} else {
    initNotificationSystem();
}
