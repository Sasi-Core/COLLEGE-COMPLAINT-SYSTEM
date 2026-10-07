/**
 * Nandha Engineering College - College Complaint Management System
 * Client-Side JavaScript Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Navigation Toggle
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    if (mobileBtn && navLinks) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
    }

    // 2. Auto-dismiss flash alert banners after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 6000);
    }

    // 3. Admin Live Clock Display
    const clockEl = document.getElementById('portalClock');
    if (clockEl) {
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const dateString = now.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
            clockEl.textContent = `${dateString} • ${timeString}`;
        }
        updateClock();
        setInterval(updateClock, 1000);
    }
});

/**
 * Switch tabs on the login page between Student and Admin
 */
function switchLoginTab(role) {
    const studentTabBtn = document.getElementById('studentTabBtn');
    const adminTabBtn = document.getElementById('adminTabBtn');
    const studentForm = document.getElementById('studentLoginForm');
    const adminForm = document.getElementById('adminLoginForm');

    if (!studentTabBtn || !adminTabBtn || !studentForm || !adminForm) return;

    if (role === 'admin') {
        studentTabBtn.classList.remove('active');
        adminTabBtn.classList.add('active');
        studentForm.classList.add('hidden');
        adminForm.classList.remove('hidden');
        const adminInput = document.getElementById('admin_username');
        if (adminInput) adminInput.focus();
    } else {
        adminTabBtn.classList.remove('active');
        studentTabBtn.classList.add('active');
        adminForm.classList.add('hidden');
        studentForm.classList.remove('hidden');
        const studentInput = document.getElementById('student_id');
        if (studentInput) studentInput.focus();
    }
}

/**
 * 1-Click Auto-fill credentials for demonstration & testing
 */
function autoFillCredentials(role, identifier, password) {
    switchLoginTab(role);

    if (role === 'student') {
        const idInput = document.getElementById('student_id');
        const pwInput = document.getElementById('student_password');
        if (idInput && pwInput) {
            idInput.value = identifier;
            pwInput.value = password;
            idInput.classList.add('input-highlight');
            pwInput.classList.add('input-highlight');
            setTimeout(() => {
                idInput.classList.remove('input-highlight');
                pwInput.classList.remove('input-highlight');
            }, 800);
        }
    } else {
        const userInput = document.getElementById('admin_username');
        const pwInput = document.getElementById('admin_password');
        if (userInput && pwInput) {
            userInput.value = identifier;
            pwInput.value = password;
            userInput.classList.add('input-highlight');
            pwInput.classList.add('input-highlight');
            setTimeout(() => {
                userInput.classList.remove('input-highlight');
                pwInput.classList.remove('input-highlight');
            }, 800);
        }
    }
}

/**
 * Toggle password field visibility (show/hide password)
 */
function togglePasswordVisibility(fieldId, button) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    const icon = button.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

/**
 * Handle file attachment input display
 */
function displaySelectedFile(input) {
    const placeholder = document.getElementById('uploadPlaceholder');
    const fileInfo = document.getElementById('fileSelectedInfo');
    const fileNameSpan = document.getElementById('selectedFileName');

    if (input.files && input.files[0]) {
        const file = input.files[0];
        if (placeholder) placeholder.classList.add('hidden');
        if (fileInfo) fileInfo.classList.remove('hidden');
        if (fileNameSpan) {
            fileNameSpan.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        }
    }
}

/**
 * Clear selected file
 */
function clearSelectedFile() {
    const input = document.getElementById('attachment');
    const placeholder = document.getElementById('uploadPlaceholder');
    const fileInfo = document.getElementById('fileSelectedInfo');

    if (input) input.value = '';
    if (fileInfo) fileInfo.classList.add('hidden');
    if (placeholder) placeholder.classList.remove('hidden');
}

/**
 * Confirmation dialog before permanently deleting a complaint
 */
function confirmDelete(complaintId) {
    return confirm(`Are you sure you want to permanently delete complaint record "${complaintId}"?\nThis action cannot be undone.`);
}
