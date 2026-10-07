import os
import sqlite3
import datetime
import random
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Initialize Flask Application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nandha-engineering-college-secret-key-2026-pbl'
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB maximum upload size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create database tables and seed initial demo data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Complaints Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            student_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            department TEXT NOT NULL,
            priority TEXT NOT NULL,
            description TEXT NOT NULL,
            attachment TEXT,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Resolved', 'Rejected')),
            admin_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()

    # Seed Admin User if not present
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    if not admin:
        hashed_admin_pw = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, student_id, username, password, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Nandha Admin Office', None, 'admin', hashed_admin_pw, 'admin', 'Administrative Office'))
        conn.commit()

    # Seed Demo Student if not present
    cursor.execute("SELECT id FROM users WHERE student_id = 'STU001'")
    student = cursor.fetchone()
    if not student:
        hashed_student_pw = generate_password_hash('student123')
        cursor.execute('''
            INSERT INTO users (name, student_id, username, password, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Kavitha R', 'STU001', 'stu001', hashed_student_pw, 'student', 'Computer Science & Engineering'))
        student_id_val = cursor.lastrowid
        conn.commit()

        # Seed initial realistic complaints for STU001
        sample_complaints = [
            (
                'NEC-2026-1001', 'STU001', student_id_val,
                'Projector issue in CSE Seminar Hall 2',
                'Infrastructure', 'Computer Science & Engineering', 'High',
                'The HDMI connection and display flickering persistently during morning technical seminar sessions.',
                None, 'In Progress',
                'Technical department team has been notified. Electrician and IT lab technician dispatched to replace the HDMI transceiver.',
                '2026-03-20 09:30:00', '2026-03-21 11:15:00'
            ),
            (
                'NEC-2026-1002', 'STU001', student_id_val,
                'Wi-Fi connectivity drop in Central Library Block B',
                'Internet/Wi-Fi', 'Library', 'Medium',
                'Signal strength frequently drops around study cubicles 15 to 25. Students are unable to access IEEE digital library portals.',
                None, 'Pending',
                None,
                '2026-03-24 14:10:00', '2026-03-24 14:10:00'
            ),
            (
                'NEC-2026-1003', 'STU001', student_id_val,
                'Hostel block water purifier filter replacement',
                'Hostel', 'Hostel', 'Medium',
                'Drinking water unit on second floor Girls Hostel Block A requires periodic filter and UV cartridge change.',
                None, 'Resolved',
                'Sanitation maintenance completed on 25-Mar-2026. New RO filter installed and water quality report verified clean.',
                '2026-03-15 16:45:00', '2026-03-18 10:20:00'
            )
        ]

        for comp in sample_complaints:
            cursor.execute('''
                INSERT INTO complaints (
                    complaint_id, student_id, user_id, title, category,
                    department, priority, description, attachment, status,
                    admin_response, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', comp)
        conn.commit()

    conn.close()


def generate_complaint_id():
    """Generate a clean, professional complaint ID like NEC-2026-4821."""
    suffix = random.randint(1000, 9999)
    candidate = f"NEC-2026-{suffix}"
    conn = get_db_connection()
    while conn.execute("SELECT 1 FROM complaints WHERE complaint_id = ?", (candidate,)).fetchone():
        suffix = random.randint(1000, 9999)
        candidate = f"NEC-2026-{suffix}"
    conn.close()
    return candidate


# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'student':
            flash('Access restricted to students only.', 'danger')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator to access this page.', 'warning')
            return redirect(url_for('login', tab='admin'))
        if session.get('role') != 'admin':
            flash('Access restricted to administrators only.', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------
# Routes
# ------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to appropriate dashboard
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))

    active_tab = request.args.get('tab', 'student')

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student').strip()
        active_tab = login_type

        conn = get_db_connection()

        if login_type == 'student':
            student_id = request.form.get('student_id', '').strip()
            password = request.form.get('password', '').strip()

            if not student_id or not password:
                flash('Please enter both Student ID and Password.', 'danger')
                return render_template('login.html', active_tab='student')

            user = conn.execute(
                "SELECT * FROM users WHERE UPPER(student_id) = UPPER(?) AND role = 'student'",
                (student_id,)
            ).fetchone()

            if user and check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id']
                session['student_id'] = user['student_id']
                session['name'] = user['name']
                session['role'] = 'student'
                session['department'] = user['department']
                flash(f"Welcome back, {user['name']}!", 'success')
                conn.close()
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid Student ID or Password. Demo: STU001 / student123', 'danger')
                conn.close()
                return render_template('login.html', active_tab='student', student_id=student_id)

        elif login_type == 'admin':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            if not username or not password:
                flash('Please enter both Admin Username and Password.', 'danger')
                return render_template('login.html', active_tab='admin')

            admin = conn.execute(
                "SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND role = 'admin'",
                (username,)
            ).fetchone()

            if admin and check_password_hash(admin['password'], password):
                session.clear()
                session['user_id'] = admin['id']
                session['username'] = admin['username']
                session['name'] = admin['name']
                session['role'] = 'admin'
                session['department'] = admin['department']
                flash(f"Welcome, Administrator {admin['name']}!", 'success')
                conn.close()
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Admin Username or Password. Demo: admin / admin123', 'danger')
                conn.close()
                return render_template('login.html', active_tab='admin', username=username)

    return render_template('login.html', active_tab=active_tab)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ------------------------
# Student Routes
# ------------------------

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    conn = get_db_connection()
    user_id = session['user_id']

    # Counts for dashboard cards
    total = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'Pending'", (user_id,)
    ).fetchone()[0]

    in_progress = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'In Progress'", (user_id,)
    ).fetchone()[0]

    resolved = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'Resolved'", (user_id,)
    ).fetchone()[0]

    # Recent 5 complaints
    recent_complaints = conn.execute(
        "SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,)
    ).fetchall()

    conn.close()
    return render_template(
        'student_dashboard.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        recent_complaints=recent_complaints
    )


@app.route('/student/submit-complaint', methods=['GET', 'POST'])
@student_required
def submit_complaint():
    categories = [
        'Academic', 'Infrastructure', 'Hostel', 'Transport',
        'Canteen', 'Library', 'Internet/Wi-Fi', 'Faculty', 'Other'
    ]
    departments = [
        'Computer Science & Engineering',
        'Electronics & Communication Engineering',
        'Electrical & Electronics Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Information Technology',
        'Artificial Intelligence & Data Science',
        'Master of Business Administration (MBA)',
        'Master of Computer Applications (MCA)',
        'Hostel & Residential Facilities',
        'Campus Transport Division',
        'General Administration'
    ]
    priorities = ['Low', 'Medium', 'High', 'Urgent']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        department = request.form.get('department', '').strip()
        priority = request.form.get('priority', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not title or not category or not department or not priority or not description:
            flash('Please fill in all mandatory complaint fields.', 'danger')
            return render_template(
                'submit_complaint.html',
                categories=categories,
                departments=departments,
                priorities=priorities,
                form_data=request.form
            )

        if category not in categories:
            flash('Invalid category selected.', 'danger')
            return render_template(
                'submit_complaint.html',
                categories=categories,
                departments=departments,
                priorities=priorities,
                form_data=request.form
            )

        if priority not in priorities:
            flash('Invalid priority level selected.', 'danger')
            return render_template(
                'submit_complaint.html',
                categories=categories,
                departments=departments,
                priorities=priorities,
                form_data=request.form
            )

        # Handle optional file attachment
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    original_name = secure_filename(file.filename)
                    timestamp_prefix = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
                    attachment_filename = timestamp_prefix + original_name
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))
                else:
                    flash('Invalid file format. Allowed formats: PNG, JPG, JPEG, GIF, PDF, TXT, DOC, DOCX.', 'danger')
                    return render_template(
                        'submit_complaint.html',
                        categories=categories,
                        departments=departments,
                        priorities=priorities,
                        form_data=request.form
                    )

        # Generate unique Complaint ID
        complaint_id = generate_complaint_id()
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO complaints (
                complaint_id, student_id, user_id, title, category,
                department, priority, description, attachment, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
        ''', (
            complaint_id, session['student_id'], session['user_id'],
            title, category, department, priority, description,
            attachment_filename, current_time, current_time
        ))
        conn.commit()
        conn.close()

        flash(f'Complaint submitted successfully! Your tracking ID is {complaint_id}.', 'success')
        return redirect(url_for('my_complaints'))

    return render_template(
        'submit_complaint.html',
        categories=categories,
        departments=departments,
        priorities=priorities,
        form_data={}
    )


@app.route('/student/my-complaints')
@student_required
def my_complaints():
    conn = get_db_connection()
    user_id = session['user_id']
    status_filter = request.args.get('status', '').strip()

    query = "SELECT * FROM complaints WHERE user_id = ?"
    params = [user_id]

    if status_filter in ['Pending', 'In Progress', 'Resolved', 'Rejected']:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY created_at DESC"
    complaints = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'my_complaints.html',
        complaints=complaints,
        current_filter=status_filter
    )


# ------------------------
# Admin Routes
# ------------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()

    # Metrics
    total = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'").fetchone()[0]
    in_progress = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Rejected'").fetchone()[0]

    # Filters and Search
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    department_filter = request.args.get('department', '').strip()

    query = '''
        SELECT c.*, u.name as student_name, u.department as student_dept
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE 1=1
    '''
    params = []

    if search_query:
        query += ''' AND (
            c.complaint_id LIKE ? OR
            c.title LIKE ? OR
            c.student_id LIKE ? OR
            u.name LIKE ?
        )'''
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    if status_filter:
        query += " AND c.status = ?"
        params.append(status_filter)

    if category_filter:
        query += " AND c.category = ?"
        params.append(category_filter)

    if priority_filter:
        query += " AND c.priority = ?"
        params.append(priority_filter)

    if department_filter:
        query += " AND c.department = ?"
        params.append(department_filter)

    query += " ORDER BY c.created_at DESC"

    complaints = conn.execute(query, params).fetchall()

    # Dropdown lists for filter UI
    categories = [
        'Academic', 'Infrastructure', 'Hostel', 'Transport',
        'Canteen', 'Library', 'Internet/Wi-Fi', 'Faculty', 'Other'
    ]
    priorities = ['Low', 'Medium', 'High', 'Urgent']
    departments = [
        'Computer Science & Engineering',
        'Electronics & Communication Engineering',
        'Electrical & Electronics Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Information Technology',
        'Artificial Intelligence & Data Science',
        'Master of Business Administration (MBA)',
        'Master of Computer Applications (MCA)',
        'Hostel & Residential Facilities',
        'Campus Transport Division',
        'General Administration'
    ]

    conn.close()

    return render_template(
        'admin_dashboard.html',
        complaints=complaints,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        rejected=rejected,
        categories=categories,
        priorities=priorities,
        departments=departments,
        current_search=search_query,
        current_status=status_filter,
        current_category=category_filter,
        current_priority=priority_filter,
        current_department=department_filter
    )


# ------------------------
# Shared & Action Routes
# ------------------------

@app.route('/complaint/<complaint_id>')
@login_required
def complaint_details(complaint_id):
    conn = get_db_connection()
    complaint = conn.execute('''
        SELECT c.*, u.name as student_name, u.department as student_dept, u.student_id as student_reg_id
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.complaint_id = ?
    ''', (complaint_id,)).fetchone()

    conn.close()

    if not complaint:
        flash('Complaint not found.', 'danger')
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('my_complaints'))

    # If logged in as student, make sure they only see their own complaint
    if session.get('role') == 'student' and complaint['user_id'] != session.get('user_id'):
        flash('Unauthorized access: You can only view your own complaints.', 'danger')
        return redirect(url_for('my_complaints'))

    return render_template('complaint_details.html', complaint=complaint)


@app.route('/admin/complaint/<complaint_id>/update', methods=['POST'])
@admin_required
def update_complaint_status(complaint_id):
    new_status = request.form.get('status', '').strip()
    admin_response = request.form.get('admin_response', '').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Rejected']
    if new_status not in valid_statuses:
        flash('Invalid status selection.', 'danger')
        return redirect(url_for('complaint_details', complaint_id=complaint_id))

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()

    conn.execute('''
        UPDATE complaints
        SET status = ?, admin_response = ?, updated_at = ?
        WHERE complaint_id = ?
    ''', (new_status, admin_response if admin_response else None, current_time, complaint_id))
    conn.commit()
    conn.close()

    flash(f'Complaint {complaint_id} status updated to "{new_status}" successfully.', 'success')
    return redirect(url_for('complaint_details', complaint_id=complaint_id))


@app.route('/admin/complaint/<complaint_id>/delete', methods=['POST'])
@admin_required
def delete_complaint(complaint_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM complaints WHERE complaint_id = ?", (complaint_id,))
    conn.commit()
    conn.close()

    flash(f'Complaint {complaint_id} has been permanently deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


# File download / preview route for attachments
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', not_found_error=True), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large! Maximum attachment size allowed is 10 MB.', 'danger')
    return redirect(request.url)


# Run Database Initialization on app start
with app.app_context():
    init_db()

if __name__ == '__main__':
    print("Starting Nandha Engineering College Complaint System...")
    print("Database initialized at:", app.config['DATABASE'])
    print("Demo Student: STU001 / student123")
    print("Demo Admin: admin / admin123")
    app.run(debug=True, host='127.0.0.1', port=5000)
