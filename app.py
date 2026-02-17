from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import date, timedelta

app = Flask(__name__)

# connect database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='haha123',
    database='roll_call'
)
cursor = conn.cursor(dictionary=True)


@app.route('/attendance_form')
def attendance_form():
    # 抓學生資料
    cursor.execute("SELECT id, chinese_name, name FROM students WHERE active=1")
    students = cursor.fetchall()

    # 本週有課的日期
    cursor.execute("SELECT DISTINCT weekday FROM class_slots")
    weekdays_with_class = [row['weekday'] for row in cursor.fetchall()]

    start_date = date.today()
    dates = [str(start_date + timedelta(days=i)) for i in range(7) 
             if (start_date + timedelta(days=i)).isoweekday() in weekdays_with_class]

    # 抓已存在的點名資料
    cursor.execute("SELECT student_id, attend_date, slot_name, present FROM attendance")
    attendance_records = cursor.fetchall()
    
    # 轉成方便前端查詢的 dict
    attendance_map = {}
    for rec in attendance_records:
        key = (rec['student_id'], str(rec['attend_date']), rec['slot_name'])
        attendance_map[key] = rec['present']

    
    return render_template(
        "attendance.html", 
        students=students, 
        dates=dates, 
        attendance_map=attendance_map
    )


# 儲存點名
@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    data = request.get_json()
    for record in data:
        student_id = record['student_id']
        attend_date = record['attend_date']
        slot_name = record['slot_name']  # A/B/C
        present = int(record['present'])  # 存 0/1

        cursor.execute("""
            INSERT INTO attendance(student_id, slot_name, attend_date, present)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE present=VALUES(present)
        """, (student_id, slot_name, attend_date, present))
    
    conn.commit()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)