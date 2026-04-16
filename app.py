from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
# Secret key for sessions/flash messages
app.secret_key = 'super_secret_hms_key'

# MySQL database configuration
# Assumes default 'root' user with no password
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'harsh101',
    'database': 'hms_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

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

if __name__ == '__main__':
    app.run(debug=True)
