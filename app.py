from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import re

app = Flask(__name__)
# Secret key for sessions/flash messages
app.secret_key = 'super_secret_hms_key'

# MySQL database configuration
# Assumes default 'root' user with no password
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'hms_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_user_tables(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """,
        (db_config['database'],)
    )
    tables = [row['TABLE_NAME'] for row in cursor.fetchall()]
    cursor.close()
    return tables

@app.route('/')
def index():
    # Simple dashboard summary
    conn = get_db_connection()
    stats = {'patients': 0, 'doctors': 0, 'appointments': 0, 'revenue': 0}
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM Patient")
        stats['patients'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Doctor")
        stats['doctors'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Appointment WHERE Status = 'Scheduled'")
        stats['appointments'] = cursor.fetchone()['count']
        cursor.execute("SELECT SUM(Amount) as total FROM Billing WHERE Payment_Status = 'Paid'")
        result = cursor.fetchone()
        stats['revenue'] = result['total'] if result['total'] else 0
        cursor.close()
        conn.close()
    return render_template('index.html', stats=stats)

# --- PATIENT ROUTES ---
@app.route('/patients')
def patients():
    conn = get_db_connection()
    patientsList = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Patient")
        patientsList = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('patients.html', patients=patientsList)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        disease = request.form['disease']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO Patient (Name, Age, Gender, Phone, Disease) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, age, gender, phone, disease))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients'))
        else:
            flash('Database connection failed', 'danger')
            
    return render_template('add_patient.html')

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('patients'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        disease = request.form['disease']

        cursor = conn.cursor()
        query = """
            UPDATE Patient
            SET Name = %s, Age = %s, Gender = %s, Phone = %s, Disease = %s
            WHERE Patient_ID = %s
        """
        cursor.execute(query, (name, age, gender, phone, disease, patient_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Patient WHERE Patient_ID = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        flash('Patient not found', 'warning')
        return redirect(url_for('patients'))

    return render_template('edit_patient.html', patient=patient)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('patients'))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Patient WHERE Patient_ID = %s", (patient_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients'))

# --- DOCTOR ROUTES ---
@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    docList = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Doctor")
        docList = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('doctors.html', doctors=docList)

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO Doctor (Name, Specialization, Phone) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, specialization, phone))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('doctors'))
        else:
            flash('Database connection failed', 'danger')
            
    return render_template('add_doctor.html')

@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('doctors'))

    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']

        cursor = conn.cursor()
        query = """
            UPDATE Doctor
            SET Name = %s, Specialization = %s, Phone = %s
            WHERE Doctor_ID = %s
        """
        cursor.execute(query, (name, specialization, phone, doctor_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('doctors'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()

    if not doctor:
        flash('Doctor not found', 'warning')
        return redirect(url_for('doctors'))

    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('doctors'))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Doctor WHERE Doctor_ID = %s", (doctor_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('doctors'))

# --- APPOINTMENT ROUTES ---
@app.route('/appointments')
def appointments():
    conn = get_db_connection()
    appt_list = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.Appointment_ID, p.Name as PatientName, d.Name as DoctorName, a.Date, a.Time, a.Status 
            FROM Appointment a
            JOIN Patient p ON a.Patient_ID = p.Patient_ID
            JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
            ORDER BY a.Date DESC, a.Time DESC
        """
        cursor.execute(query)
        appt_list = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('appointments.html', appointments=appt_list)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    conn = get_db_connection()
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO Appointment (Patient_ID, Doctor_ID, Date, Time) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (patient_id, doctor_id, date, time))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('appointments'))
            
    # GET method - fetch form data
    patients = []
    doctors = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Patient_ID, Name FROM Patient")
        patients = cursor.fetchall()
        cursor.execute("SELECT Doctor_ID, Name FROM Doctor")
        doctors = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('book_appointment.html', patients=patients, doctors=doctors)

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('appointments'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        status = request.form['status']

        cursor = conn.cursor()
        query = """
            UPDATE Appointment
            SET Patient_ID = %s, Doctor_ID = %s, Date = %s, Time = %s, Status = %s
            WHERE Appointment_ID = %s
        """
        cursor.execute(query, (patient_id, doctor_id, date, time, status, appointment_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Appointment WHERE Appointment_ID = %s", (appointment_id,))
    appointment = cursor.fetchone()

    if not appointment:
        cursor.close()
        conn.close()
        flash('Appointment not found', 'warning')
        return redirect(url_for('appointments'))

    cursor.execute("SELECT Patient_ID, Name FROM Patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT Doctor_ID, Name FROM Doctor")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'edit_appointment.html',
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('appointments'))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Appointment WHERE Appointment_ID = %s", (appointment_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('appointments'))

# --- BILLING ROUTES ---
@app.route('/billing')
def billing():
    conn = get_db_connection()
    bills = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.Bill_ID, p.Name as PatientName, b.Amount, b.Payment_Status, b.Date 
            FROM Billing b
            JOIN Patient p ON b.Patient_ID = p.Patient_ID
            ORDER BY b.Date DESC
        """
        cursor.execute(query)
        bills = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('billing.html', bills=bills)

@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    conn = get_db_connection()
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        amount = request.form['amount']
        date = request.form['date']
        
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO Billing (Patient_ID, Amount, Date) VALUES (%s, %s, %s)"
            cursor.execute(query, (patient_id, amount, date))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Bill generated successfully!', 'success')
            return redirect(url_for('billing'))
            
    patients = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Patient_ID, Name FROM Patient")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('generate_bill.html', patients=patients)

@app.route('/edit_bill/<int:bill_id>', methods=['GET', 'POST'])
def edit_bill(bill_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('billing'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        amount = request.form['amount']
        date = request.form['date']
        payment_status = request.form['payment_status']

        cursor = conn.cursor()
        query = """
            UPDATE Billing
            SET Patient_ID = %s, Amount = %s, Date = %s, Payment_Status = %s
            WHERE Bill_ID = %s
        """
        cursor.execute(query, (patient_id, amount, date, payment_status, bill_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Bill updated successfully!', 'success')
        return redirect(url_for('billing'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Billing WHERE Bill_ID = %s", (bill_id,))
    bill = cursor.fetchone()

    if not bill:
        cursor.close()
        conn.close()
        flash('Bill not found', 'warning')
        return redirect(url_for('billing'))

    cursor.execute("SELECT Patient_ID, Name FROM Patient")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('edit_bill.html', bill=bill, patients=patients)

@app.route('/delete_bill/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('billing'))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Billing WHERE Bill_ID = %s", (bill_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Bill deleted successfully!', 'success')
    return redirect(url_for('billing'))

# --- MEDICINE ROUTES ---
@app.route('/medicines')
def medicines():
    conn = get_db_connection()
    medicine_list = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Medicine ORDER BY Medicine_ID DESC")
        medicine_list = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('medicines.html', medicines=medicine_list)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['medicine_name']
        category = request.form['category']
        unit_price = request.form['unit_price']
        stock_qty = request.form['stock_qty']
        expiry_date = request.form['expiry_date']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO Medicine (Medicine_Name, Category, Unit_Price, Stock_Qty, Expiry_Date)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, category, unit_price, stock_qty, expiry_date))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('medicines'))

        flash('Database connection failed', 'danger')

    return render_template('add_medicine.html')

@app.route('/edit_medicine/<int:medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('medicines'))

    if request.method == 'POST':
        name = request.form['medicine_name']
        category = request.form['category']
        unit_price = request.form['unit_price']
        stock_qty = request.form['stock_qty']
        expiry_date = request.form['expiry_date']

        cursor = conn.cursor()
        query = """
            UPDATE Medicine
            SET Medicine_Name = %s, Category = %s, Unit_Price = %s, Stock_Qty = %s, Expiry_Date = %s
            WHERE Medicine_ID = %s
        """
        cursor.execute(query, (name, category, unit_price, stock_qty, expiry_date, medicine_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Medicine WHERE Medicine_ID = %s", (medicine_id,))
    medicine = cursor.fetchone()
    cursor.close()
    conn.close()

    if not medicine:
        flash('Medicine not found', 'warning')
        return redirect(url_for('medicines'))

    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
def delete_medicine(medicine_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('medicines'))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Medicine WHERE Medicine_ID = %s", (medicine_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines'))

# --- DYNAMIC DATABASE EXPLORER ROUTES ---
@app.route('/db')
def db_explorer():
    conn = get_db_connection()
    tables = []
    if conn:
        tables = get_user_tables(conn)
        conn.close()
    else:
        flash('Database connection failed', 'danger')
    return render_template('db_explorer.html', tables=tables)

@app.route('/db/<table_name>')
def db_table_view(table_name):
    # Restrict table names to safe characters before using identifier quoting.
    if not re.match(r'^[A-Za-z0-9_]+$', table_name):
        flash('Invalid table name', 'warning')
        return redirect(url_for('db_explorer'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('db_explorer'))

    tables = get_user_tables(conn)
    if table_name not in tables:
        conn.close()
        flash('Table not found in current database', 'warning')
        return redirect(url_for('db_explorer'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    columns = [col['Field'] for col in cursor.fetchall()]

    # Keep UI responsive by limiting preview rows.
    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 200")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'db_table.html',
        table_name=table_name,
        columns=columns,
        rows=rows,
        row_limit=200
    )

if __name__ == '__main__':
    app.run(debug=True)
