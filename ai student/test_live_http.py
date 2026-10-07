import urllib.request
import urllib.parse
import http.cookiejar
import json
import re

BASE_URL = 'http://127.0.0.1:5000'

def test_live_server():
    print("Testing Live HTTP Server on port 5000...")
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    # 1. GET /
    print("\n[Step 1] Visiting homepage (redirects to /login)...")
    res = opener.open(f"{BASE_URL}/")
    html = res.read().decode('utf-8')
    assert "Nandha Engineering College" in html, "Homepage should contain college name"
    assert "College Complaint System" in html, "Homepage should contain system title"
    print(" [OK] Login page loaded successfully. HTTP status:", res.status)

    # 2. Test Invalid Student Login
    print("\n[Step 2] Testing invalid login handling...")
    data = urllib.parse.urlencode({
        'login_type': 'student',
        'student_id': 'BAD_STUDENT',
        'password': 'bad_password'
    }).encode('utf-8')
    res = opener.open(f"{BASE_URL}/login", data=data)
    html = res.read().decode('utf-8')
    assert "Invalid Student ID or Password" in html, "Should show invalid credentials message"
    print(" [OK] Invalid student login appropriately rejected with warning banner.")

    # 3. Test Valid Student Login
    print("\n[Step 3] Testing valid student login (STU001 / student123)...")
    data = urllib.parse.urlencode({
        'login_type': 'student',
        'student_id': 'STU001',
        'password': 'student123'
    }).encode('utf-8')
    res = opener.open(f"{BASE_URL}/login", data=data)
    html = res.read().decode('utf-8')
    assert "Welcome back, Kavitha R" in html, "Should show student welcome banner"
    assert "Student Grievance Portal" in html
    print(" [OK] Student authenticated successfully and landed on dashboard.")

    # 4. Student submits a new complaint
    print("\n[Step 4] Submitting new student complaint...")
    data = urllib.parse.urlencode({
        'title': 'High Speed Wi-Fi Router Downtime in CSE Lab 3',
        'category': 'Internet/Wi-Fi',
        'department': 'Computer Science & Engineering',
        'priority': 'Urgent',
        'description': 'The Cisco gateway router in CSE Lab 3 keeps rebooting every 15 minutes during practical sessions.'
    }).encode('utf-8')
    res = opener.open(f"{BASE_URL}/student/submit-complaint", data=data)
    html = res.read().decode('utf-8')
    assert "Complaint submitted successfully" in html
    match = re.search(r'NEC-2026-\d{4}', html)
    assert match, "Generated complaint ID must be present in response"
    complaint_id = match.group(0)
    print(f" [OK] Complaint submitted successfully. Generated Tracking ID: {complaint_id}")

    # 5. Verify complaint appears in My Complaints
    print("\n[Step 5] Checking My Complaints list...")
    res = opener.open(f"{BASE_URL}/student/my-complaints")
    html = res.read().decode('utf-8')
    assert complaint_id in html
    assert "High Speed Wi-Fi Router Downtime in CSE Lab 3" in html
    print(" [OK] Complaint verified in student's complaint list.")

    # 6. Check Complaint Details as Student
    print(f"\n[Step 6] Opening Complaint Details for {complaint_id} as Student...")
    res = opener.open(f"{BASE_URL}/complaint/{complaint_id}")
    html = res.read().decode('utf-8')
    assert complaint_id in html
    assert "Cisco gateway router" in html
    assert "Awaiting Review" in html or "Submitted" in html
    print(" [OK] Complaint details and progress stepper rendered for student.")

    # 7. Student Logout
    print("\n[Step 7] Testing Student Logout...")
    res = opener.open(f"{BASE_URL}/logout")
    html = res.read().decode('utf-8')
    assert "You have been logged out successfully" in html
    print(" [OK] Student session terminated cleanly.")

    # 8. Admin Login
    print("\n[Step 8] Testing Admin Login (admin / admin123)...")
    admin_cookie_jar = http.cookiejar.CookieJar()
    admin_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(admin_cookie_jar))
    data = urllib.parse.urlencode({
        'login_type': 'admin',
        'username': 'admin',
        'password': 'admin123'
    }).encode('utf-8')
    res = admin_opener.open(f"{BASE_URL}/login", data=data)
    html = res.read().decode('utf-8')
    assert "Complaint Management Center" in html
    assert "Nandha Admin Office" in html
    print(" [OK] Admin authenticated and landed on management console.")

    # 9. Verify Complaint appears in Admin Dashboard
    print("\n[Step 9] Checking Admin Dashboard for complaint...")
    res = admin_opener.open(f"{BASE_URL}/admin/dashboard")
    html = res.read().decode('utf-8')
    assert complaint_id in html
    print(f" [OK] Complaint {complaint_id} visible in Admin complaints table.")

    # 10. Admin Updates Status to 'In Progress' with Official Response
    print(f"\n[Step 10] Admin updating status to 'In Progress' and adding response...")
    admin_note = "Network engineer assigned. Gateway firmware update scheduled for 4:30 PM today."
    data = urllib.parse.urlencode({
        'status': 'In Progress',
        'admin_response': admin_note
    }).encode('utf-8')
    res = admin_opener.open(f"{BASE_URL}/admin/complaint/{complaint_id}/update", data=data)
    html = res.read().decode('utf-8')
    assert "status updated to" in html
    assert "In Progress" in html
    assert admin_note in html
    print(" [OK] Complaint status updated to 'In Progress' with response attached.")

    # 11. Admin Logout
    print("\n[Step 11] Logging out Admin...")
    admin_opener.open(f"{BASE_URL}/logout")
    print(" [OK] Admin logged out.")

    # 12. Student logs back in and verifies updated status & admin response
    print("\n[Step 12] Student logs back in to verify real-time status update...")
    student_cookie_jar2 = http.cookiejar.CookieJar()
    student_opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(student_cookie_jar2))
    data = urllib.parse.urlencode({
        'login_type': 'student',
        'student_id': 'STU001',
        'password': 'student123'
    }).encode('utf-8')
    student_opener2.open(f"{BASE_URL}/login", data=data)
    res = student_opener2.open(f"{BASE_URL}/complaint/{complaint_id}")
    html = res.read().decode('utf-8')
    assert "In Progress" in html, "Student must see In Progress status"
    assert admin_note in html, "Student must see official administration response"
    print(" [OK] Verification successful! Student sees 'In Progress' and official admin note.")

    # 13. Test Search & Filter on Admin Dashboard
    print("\n[Step 13] Testing Search and Filter endpoints...")
    admin_cookie_jar3 = http.cookiejar.CookieJar()
    admin_opener3 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(admin_cookie_jar3))
    data = urllib.parse.urlencode({
        'login_type': 'admin',
        'username': 'admin',
        'password': 'admin123'
    }).encode('utf-8')
    admin_opener3.open(f"{BASE_URL}/login", data=data)

    search_res = admin_opener3.open(f"{BASE_URL}/admin/dashboard?search={complaint_id}")
    html_search = search_res.read().decode('utf-8')
    assert complaint_id in html_search
    print(" [OK] Live search returned matching complaint record.")

    filter_res = admin_opener3.open(f"{BASE_URL}/admin/dashboard?status=In+Progress")
    html_filter = filter_res.read().decode('utf-8')
    assert complaint_id in html_filter
    print(" [OK] Live status filter returned matching records.")

    print("\n=======================================================")
    print(">>> ALL 13 END-TO-END HTTP TESTS PASSED WITH 100% SUCCESS! <<<")
    print("=======================================================")

if __name__ == '__main__':
    test_live_server()
