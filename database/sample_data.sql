-- sample_data.sql
USE hms_db;

-- Insert Patients
INSERT INTO Patient (Name, Age, Gender, Phone, Disease) VALUES
('John Doe', 45, 'Male', '555-0101', 'Hypertension'),
('Jane Smith', 32, 'Female', '555-0102', 'Asthma'),
('Michael Johnson', 50, 'Male', '555-0103', 'Diabetes'),
('Emily Davis', 28, 'Female', '555-0104', 'Migraine');

-- Insert Doctors
INSERT INTO Doctor (Name, Specialization, Phone) VALUES
('Dr. Sarah Miller', 'Cardiologist', '555-0201'),
('Dr. James Wilson', 'Pulmonologist', '555-0202'),
('Dr. Robert Brown', 'Endocrinologist', '555-0203'),
('Dr. Lisa Taylor', 'Neurologist', '555-0204');

-- Insert Appointments
INSERT INTO Appointment (Patient_ID, Doctor_ID, Date, Time, Status) VALUES
(1, 1, '2023-10-25', '10:00:00', 'Completed'),
(2, 2, '2023-10-26', '11:30:00', 'Scheduled'),
(3, 3, '2023-10-27', '14:00:00', 'Scheduled'),
(4, 4, '2023-10-28', '15:45:00', 'Cancelled');

-- Insert Treatments
INSERT INTO Treatment (Patient_ID, Doctor_ID, Diagnosis, Prescription, Date) VALUES
(1, 1, 'High Blood Pressure', 'Lisinopril 10mg daily', '2023-10-25');

-- Insert Billing
INSERT INTO Billing (Patient_ID, Amount, Payment_Status, Date) VALUES
(1, 150.00, 'Paid', '2023-10-25'),
(2, 200.00, 'Pending', '2023-10-26');
