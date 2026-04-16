-- schema.sql
-- Database creation and use (Optional, can be run manually first)
CREATE DATABASE IF NOT EXISTS hms_db;
USE hms_db;

-- 1. Patient Table
CREATE TABLE IF NOT EXISTS Patient (
    Patient_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Disease VARCHAR(100)
);

-- 2. Doctor Table
CREATE TABLE IF NOT EXISTS Doctor (
    Doctor_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Specialization VARCHAR(100) NOT NULL,
    Phone VARCHAR(20) NOT NULL
);

-- 3. Appointment Table
CREATE TABLE IF NOT EXISTS Appointment (
    Appointment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT NOT NULL,
    Doctor_ID INT NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Status VARCHAR(50) DEFAULT 'Scheduled',
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
);

-- 4. Treatment Table
CREATE TABLE IF NOT EXISTS Treatment (
    Treatment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT NOT NULL,
    Doctor_ID INT NOT NULL,
    Diagnosis TEXT NOT NULL,
    Prescription TEXT NOT NULL,
    Date DATE NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
);

-- 5. Billing Table
CREATE TABLE IF NOT EXISTS Billing (
    Bill_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Payment_Status VARCHAR(50) DEFAULT 'Pending',
    Date DATE NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE
);
