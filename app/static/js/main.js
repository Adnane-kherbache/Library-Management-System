/**
 * Neo-Bibliotheca — Library Management System
 * Client-side Controller & Modern Interactive Enhancements
 */

// Execute immediately to prevent dark mode flicker
(function() {
    const savedTheme = localStorage.getItem('library_theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
})();

document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initAutoHideAlerts();
    initConfirmDelete();
    initCheckoutInteractions();
    initTooltips();
});

/**
 * Dark / Light Mode Toggle with Persistence
 */
function initThemeToggle() {
    const toggleBtn = document.getElementById('themeToggleBtn');
    const toggleIcon = document.getElementById('themeToggleIcon');
    if (!toggleBtn || !toggleIcon) return;

    function updateIcon(theme) {
        if (theme === 'dark') {
            toggleIcon.className = 'bi bi-sun-fill text-warning';
            toggleBtn.setAttribute('title', 'Switch to light mode');
        } else {
            toggleIcon.className = 'bi bi-moon-stars-fill text-secondary';
            toggleBtn.setAttribute('title', 'Switch to dark mode');
        }
    }

    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
    updateIcon(currentTheme);

    toggleBtn.addEventListener('click', function() {
        const activeTheme = document.documentElement.getAttribute('data-bs-theme');
        const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', nextTheme);
        localStorage.setItem('library_theme', nextTheme);
        updateIcon(nextTheme);

        // Notify charts if present
        if (window.onThemeChanged) {
            window.onThemeChanged(nextTheme);
        }
    });
}

/**
 * Auto-hide flash messages after 5 seconds
 */
function initAutoHideAlerts() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        });
    }, 5500);
}

/**
 * Confirm before destructive delete actions
 */
function initConfirmDelete() {
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const confirmed = confirm('Are you sure you want to delete this record? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this record?');
}

/**
 * Initialize Bootstrap Tooltips
 */
function initTooltips() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(el) {
            return new bootstrap.Tooltip(el);
        });
    }
}

/**
 * Checkout Form Dynamic Previews
 */
function initCheckoutInteractions() {
    const bookSelect = document.getElementById('book_id');
    const memberSelect = document.getElementById('member_id');
    const daysInput = document.getElementById('borrow_days');

    if (!bookSelect && !memberSelect) return;

    // Book Selection Change
    if (bookSelect) {
        const bookPreviewCard = document.getElementById('bookPreviewCard');
        const previewTitle = document.getElementById('previewBookTitle');
        const previewAuthor = document.getElementById('previewBookAuthor');
        const previewCategory = document.getElementById('previewBookCategory');
        const previewAvailable = document.getElementById('previewBookAvailable');

        function updateBookPreview() {
            const selectedOpt = bookSelect.options[bookSelect.selectedIndex];
            if (selectedOpt && selectedOpt.value) {
                if (bookPreviewCard) bookPreviewCard.style.display = 'block';
                if (previewTitle) previewTitle.textContent = selectedOpt.dataset.title || '';
                if (previewAuthor) previewAuthor.textContent = selectedOpt.dataset.author || '';
                if (previewCategory) previewCategory.textContent = selectedOpt.dataset.category || 'General';
                if (previewAvailable) previewAvailable.textContent = (selectedOpt.dataset.available || '0') + ' copies left';
            } else {
                if (bookPreviewCard) bookPreviewCard.style.display = 'none';
            }
        }

        bookSelect.addEventListener('change', updateBookPreview);
        updateBookPreview();
    }

    // Member Selection Change
    if (memberSelect) {
        const memberPreviewCard = document.getElementById('memberPreviewCard');
        const previewName = document.getElementById('previewMemberName');
        const previewEmail = document.getElementById('previewMemberEmail');
        const previewTier = document.getElementById('previewMemberTier');
        const previewActiveBorrows = document.getElementById('previewActiveBorrows');

        function updateMemberPreview() {
            const selectedOpt = memberSelect.options[memberSelect.selectedIndex];
            if (selectedOpt && selectedOpt.value) {
                const tier = selectedOpt.dataset.tier || 'standard';
                const activeCount = selectedOpt.dataset.active || '0';
                const maxAllowed = selectedOpt.dataset.max || (tier === 'premium' ? '10' : '5');
                const defaultDays = tier === 'premium' ? 30 : 14;

                if (memberPreviewCard) memberPreviewCard.style.display = 'block';
                if (previewName) previewName.textContent = selectedOpt.dataset.name || '';
                if (previewEmail) previewEmail.textContent = selectedOpt.dataset.email || '';
                if (previewTier) {
                    previewTier.textContent = tier.toUpperCase();
                    previewTier.className = tier === 'premium' ? 'badge badge-soft-warning' : 'badge badge-soft-secondary';
                }
                if (previewActiveBorrows) {
                    previewActiveBorrows.textContent = `${activeCount} / ${maxAllowed} active borrows`;
                }

                // Auto-suggest loan duration if user hasn't typed a custom value
                if (daysInput && (!daysInput.value || daysInput.dataset.autoFilled === 'true')) {
                    daysInput.value = defaultDays;
                    daysInput.dataset.autoFilled = 'true';
                }
            } else {
                if (memberPreviewCard) memberPreviewCard.style.display = 'none';
            }
        }

        memberSelect.addEventListener('change', updateMemberPreview);
        updateMemberPreview();
    }
}