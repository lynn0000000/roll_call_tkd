from flask import Flask, render_template, request, jsonify
from datetime import date, timedelta
import mysql.connector

app = Flask(__name__)

db_config = {
    'host':'localhost',
    'user':'root',
    'password':'haha123',
    'database':'roll_call'
}

@app.route('/')
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 讀取學生
    cursor.execute("SELECT id, name FROM students WHERE active=1 ORDER BY id")
    students = cursor.fetchall()

    # 讀取 class_slots
    cursor.execute("SELECT * FROM class_slots ORDER BY weekday, slot_name")
    slots = cursor.fetchall()

    conn.close()

    # 計算本週對應日期
    today = date.today()
    dates = {}
    for weekday in [2,3,4,5,6]:  # W2~W6
        delta_days = (weekday - today.isoweekday()) % 7
        dates[weekday] = (today + timedelta(days=delta_days)).strftime('%Y-%m-%d')

    return render_template('attendance_table.html', students=students, slots=slots, dates=dates)

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data.get('student_id')
    slot_id = data.get('slot_id')
    attend_date = data.get('attend_date')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attendance (student_id, class_slot_id, attend_date)
            VALUES (%s, %s, %s)
        """, (student_id, slot_id, attend_date))
        conn.commit()
        return jsonify({'success': True, 'message': '點名成功'})
    except mysql.connector.IntegrityError:
        return jsonify({'success': False, 'message': '已點過此堂'})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
