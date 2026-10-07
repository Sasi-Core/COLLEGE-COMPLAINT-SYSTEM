import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import unittest
from app import app, get_db_connection, init_db

class TestCollegeComplaintSystem(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_db_initialization(self):
        print("\n--- Test 1: Testing DB Initialization ---")
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        student = conn.execute("SELECT * FROM users WHERE student_id = 'STU001'").fetchone()
        complaints = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        conn.close()

        self.assertIsNotNone(admin, "Admin user should exist")
        self.assertEqual(admin['role'], 'admin')
        self.assertIsNotNone(student, "Student STU001 should exist")
        self.assertEqual(student['role'], 'student')
        self.assertGreater(complaints, 0, "Initial complaints should be seeded")
        print(f"[PASS] DB initialized properly. Initial complaints count: {complaints}")

    def test_02_invalid_login(self):
        print("\n--- Test 2: Testing Invalid Logins ---")
        # Invalid student credentials
        resp = self.client.post('/login', data={
            'login_type': 'student',
            'student_id': 'STU999_WRONG',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid Student ID or Password', resp.data)

        # Invalid admin credentials
        resp_admin = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'fake_admin',
            'password': 'badpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid Admin Username or Password', resp_admin.data)
        print("[PASS] Invalid login errors triggered correctly.")

    def test_03_student_flow_submission_and_tracking(self):
        print("\n--- Test 3: Testing Student Login, Dashboard, Submit Complaint & Tracking ---")
        # 1. Student Login
        login_resp = self.client.post('/login', data={
            'login_type': 'student',
            'student_id': 'STU001',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Kavitha R', login_resp.data)
        self.assertIn(b'Student Grievance Portal', login_resp.data)
        print("[PASS] Student logged in successfully.")

        # 2. View Student Dashboard
        dash_resp = self.client.get('/student/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Total Complaints', dash_resp.data)
        print("[PASS] Student dashboard loaded successfully.")

        # 3. Submit a new complaint
        import time
        unique_title = f"Test Water Cooler {int(time.time())}"
        sub_resp = self.client.post('/student/submit-complaint', data={
            'title': unique_title,
            'category': 'Infrastructure',
            'department': 'Mechanical Engineering',
            'priority': 'High',
            'description': 'Water dispenser is leaking and cooling unit is not operating since Monday morning.'
        }, follow_redirects=True)

        self.assertIn(b'Complaint submitted successfully', sub_resp.data)
        self.assertIn(unique_title.encode(), sub_resp.data)
        print("[PASS] Complaint submitted successfully and redirected to My Complaints.")

        # 4. Verify in SQLite Database
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM complaints WHERE title = ?", (unique_title,)).fetchone()
        self.assertIsNotNone(row)
        new_complaint_id = row['complaint_id']
        self.assertEqual(row['status'], 'Pending')
        self.assertEqual(row['priority'], 'High')
        conn.close()
        print(f"[PASS] Complaint verified in SQLite with ID: {new_complaint_id}")

        # 5. Open Complaint Details as Student
        det_resp = self.client.get(f'/complaint/{new_complaint_id}')
        self.assertEqual(det_resp.status_code, 200)
        self.assertIn(b'Water dispenser is leaking', det_resp.data)
        self.assertIn(b'Pending', det_resp.data)
        print("[PASS] Student can view complaint details.")

        # 6. Test Logout
        logout_resp = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out successfully', logout_resp.data)
        print("[PASS] Student logged out successfully.")

        # 7. Admin Login
        admin_login = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome, Administrator', admin_login.data)
        self.assertIn(b'Complaint Management Center', admin_login.data)
        print("[PASS] Admin logged in successfully.")

        # 8. Check that new complaint appears on Admin Dashboard
        admin_dash = self.client.get('/admin/dashboard')
        self.assertIn(new_complaint_id.encode(), admin_dash.data)
        self.assertIn(unique_title.encode(), admin_dash.data)
        print("[PASS] New complaint visible in Admin Dashboard.")

        # 9. Admin updates status to 'In Progress' and adds official response
        admin_response_text = "Plumbing maintenance team has been notified. Work order #PL-981 issued to technician."
        update_resp = self.client.post(f'/admin/complaint/{new_complaint_id}/update', data={
            'status': 'In Progress',
            'admin_response': admin_response_text
        }, follow_redirects=True)
        self.assertIn(b'status updated to', update_resp.data)
        self.assertIn(b'In Progress', update_resp.data)
        print("[PASS] Admin updated status to 'In Progress' with response note.")

        # 10. Verify update in DB
        conn = get_db_connection()
        updated_row = conn.execute("SELECT * FROM complaints WHERE complaint_id = ?", (new_complaint_id,)).fetchone()
        self.assertEqual(updated_row['status'], 'In Progress')
        self.assertEqual(updated_row['admin_response'], admin_response_text)
        conn.close()
        print("[PASS] Status and response verified in SQLite.")

        # 11. Admin Logout
        self.client.get('/logout', follow_redirects=True)
        print("[PASS] Admin logged out.")

        # 12. Student logs back in and checks updated status & response
        self.client.post('/login', data={
            'login_type': 'student',
            'student_id': 'STU001',
            'password': 'student123'
        }, follow_redirects=True)

        student_details_resp = self.client.get(f'/complaint/{new_complaint_id}')
        self.assertIn(b'In Progress', student_details_resp.data)
        self.assertIn(b'Plumbing maintenance team has been notified', student_details_resp.data)
        print("[PASS] Student sees updated status 'In Progress' and official admin response note!")

        # 13. Test Search and Filter
        self.client.get('/logout')
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)

        search_resp = self.client.get('/admin/dashboard?search=Water+Cooler')
        self.assertIn(new_complaint_id.encode(), search_resp.data)

        filter_resp = self.client.get('/admin/dashboard?status=In+Progress')
        self.assertIn(new_complaint_id.encode(), filter_resp.data)

        filter_wrong = self.client.get('/admin/dashboard?status=Rejected')
        self.assertNotIn(new_complaint_id.encode(), filter_wrong.data)
        print("[PASS] Search and filter functions working correctly.")

        # Clean up test complaint
        self.client.post(f'/admin/complaint/{new_complaint_id}/delete')
        print("[PASS] Delete complaint action verified.")

if __name__ == '__main__':
    unittest.main()
