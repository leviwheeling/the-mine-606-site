// FullCalendar initialization and event handling
let currentCalendar = null;

// Function to initialize calendar
function initializeCalendar() {
    // Clean up any existing calendar
    if (currentCalendar) {
        currentCalendar.destroy();
        currentCalendar = null;
    }

    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

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
            // Fetch events from our API
            fetch(`${endpoint}?start=${info.startStr}&end=${info.endStr}`)
                .then(response => response.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        successCallback(data);
                    } else {
                        console.error('Invalid events data:', data);
                        successCallback([]);
                    }
                })
                .catch(error => {
                    console.error('Failed to fetch events:', error);
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
    currentCalendar.render();
    
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