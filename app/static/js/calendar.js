// FullCalendar initialization and event handling
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const endpoint = calendarEl.dataset.endpoint || '/api/events/data';
    
    // Initialize FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        height: 'auto',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        buttonText: {
            today: 'Today',
            month: 'Month',
            week: 'Week'
        },
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
        eventDisplay: 'block',
        eventColor: '#C8A349', // mine-gold color
        eventTextColor: '#000000',
        dayMaxEvents: true,
        moreLinkClick: 'popover',
        popoverFormat: { 
            month: 'long', 
            day: 'numeric', 
            year: 'numeric' 
        }
    });

    // Render the calendar
    calendar.render();
    
    // Set default datetime-local values to current time
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);
    
    // Set start time to current time
    const startInput = document.querySelector('input[name="start"]');
    if (startInput) {
        startInput.value = localDateTime;
    }
    
    // Set end time to current time + 2 hours
    const endInput = document.querySelector('input[name="end"]');
    if (endInput) {
        const endTime = new Date(now.getTime() + 2 * 60 * 60 * 1000);
        const endLocalDateTime = new Date(endTime.getTime() - endTime.getTimezoneOffset() * 60000)
            .toISOString()
            .slice(0, 16);
        endInput.value = endLocalDateTime;
    }
});
  