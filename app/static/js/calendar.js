// FullCalendar initialization and event handling
let currentCalendar = null;

// Retry mechanism for failed requests
function fetchWithRetry(url, maxRetries = 2) {
    return new Promise((resolve, reject) => {
        let retries = 0;
        
        function attempt() {
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(resolve)
                .catch(error => {
                    retries++;
                    if (retries <= maxRetries) {
                        console.warn(`Request failed, retrying (${retries}/${maxRetries}):`, error.message);
                        setTimeout(attempt, 1000 * retries); // Exponential backoff
                    } else {
                        reject(error);
                    }
                });
        }
        
        attempt();
    });
}

// Function to initialize calendar
function initializeCalendar() {
    console.log('Initializing calendar...');
    
    // Clean up any existing calendar
    if (currentCalendar) {
        console.log('Cleaning up existing calendar');
        currentCalendar.destroy();
        currentCalendar = null;
    }

    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.warn('Calendar element not found');
        return;
    }
    
    // Check if FullCalendar is loaded
    if (typeof FullCalendar === 'undefined') {
        console.error('FullCalendar library not loaded');
        const loadingEl = document.getElementById('calendar-loading');
        if (loadingEl) {
            loadingEl.innerHTML = '<div class="text-center text-white/60"><div class="mb-2">⚠️</div><div>Calendar library failed to load</div><div class="text-sm mt-2"><button onclick="location.reload()" class="text-mine-gold hover:underline">Refresh page</button></div></div>';
        }
        return;
    }

    const endpoint = calendarEl.dataset.endpoint || '/api/events/data';
    
    // Determine initial view and toolbar based on screen size
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth < 1024;
    
    currentCalendar = new FullCalendar.Calendar(calendarEl, {
        initialView: isMobile ? 'listWeek' : 'dayGridMonth',
        height: 'auto',
        aspectRatio: isMobile ? 1.0 : (isTablet ? 1.2 : 1.35),
        headerToolbar: isMobile ? {
            left: 'prev,next',
            center: 'title',
            right: 'today'
        } : {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        buttonText: {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            list: 'List'
        },
        // Mobile-specific options
        dayMaxEvents: isMobile ? 2 : true,
        eventDisplay: 'block',
        events: function(info, successCallback, failureCallback) {
            // Fetch events from our API with retry mechanism
            console.log(`Fetching events from ${endpoint} for ${info.startStr} to ${info.endStr}`);
            fetchWithRetry(`${endpoint}?start=${info.startStr}&end=${info.endStr}`)
                .then(data => {
                    console.log('Events data received:', data);
                    if (Array.isArray(data)) {
                        successCallback(data);
                    } else {
                        console.error('Invalid events data:', data);
                        successCallback([]);
                    }
                })
                .catch(error => {
                    console.error('Failed to fetch events after retries:', error);
                    // Show error message in calendar
                    failureCallback(error);
                });
        },
        eventClick: function(info) {
            // Show event details
            const event = info.event;
            const descEl = document.getElementById('event-description');
            const descTextEl = document.getElementById('event-desc-text');
            
            if (descEl && descTextEl) {
                descTextEl.textContent = event.extendedProps.description || 'No description available.';
                descEl.classList.remove('hidden');
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    descEl.classList.add('hidden');
                }, 5000);
            }
        },
        eventColor: '#C8A349', // mine-gold color
        eventTextColor: '#000000',
        moreLinkClick: 'popover',
        popoverFormat: { 
            month: 'long', 
            day: 'numeric', 
            year: 'numeric' 
        }
    });

    // Render the calendar
    try {
        currentCalendar.render();
        console.log('Calendar rendered successfully');
        
        // Hide loading indicator
        const loadingEl = document.getElementById('calendar-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    } catch (error) {
        console.error('Failed to render calendar:', error);
        
        // Show error message instead of loading
        const loadingEl = document.getElementById('calendar-loading');
        if (loadingEl) {
            loadingEl.innerHTML = '<div class="text-center text-white/60"><div class="mb-2">⚠️</div><div>Calendar failed to load</div><div class="text-sm mt-2"><button onclick="location.reload()" class="text-mine-gold hover:underline">Refresh page</button></div></div>';
        }
    }
    
    // Handle window resize for responsive behavior
    let resizeTimeout;
    const handleResize = () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (currentCalendar) {
                const isMobile = window.innerWidth < 768;
                const currentView = currentCalendar.view.type;
                
                // Switch to appropriate view for screen size
                if (isMobile && (currentView === 'dayGridMonth' || currentView === 'timeGridWeek')) {
                    currentCalendar.changeView('listWeek');
                } else if (!isMobile && currentView === 'listWeek') {
                    currentCalendar.changeView('dayGridMonth');
                }
                
                currentCalendar.updateSize();
            }
        }, 250);
    };
    
    window.addEventListener('resize', handleResize);
}

// Initialize calendar on page load and after HTMX content swaps
document.addEventListener('DOMContentLoaded', initializeCalendar);
document.addEventListener('htmx:afterSettle', initializeCalendar);

// Clean up old calendar instance before new content
document.addEventListener('htmx:beforeSwap', function() {
    if (currentCalendar) {
        currentCalendar.destroy();
        currentCalendar = null;
    }
});