import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
from datetime import datetime
import csv


class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=' ',
                database='attendance_system'
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None

    def is_connected(self):
        """Check if database is connected"""
        return self.connection is not None and self.connection.is_connected()

    def backup_students(self):
        """Backup student data from CSV to database"""
        if not self.is_connected():
            print("Database not connected")
            return False

        csv_file = "StudentDetails/StudentDetails.csv"
        if not os.path.exists(csv_file):
            print("Student details CSV file not found")
            return False

        try:
            cursor = self.connection.cursor()

            # Clear existing data (optional - you might want to keep historical data)
            cursor.execute("DELETE FROM students")

            # Read CSV and insert into database
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute(
                        "INSERT INTO students (serial_no, student_id, student_name) "
                        "VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE student_name = VALUES(student_name)",
                        (row['SERIAL NO.'], row['ID'], row['NAME'])
                    )

            self.connection.commit()
            print(f"Successfully backed up {cursor.rowcount} students to database")
            return True
        except Error as e:
            print(f"Error backing up students: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def backup_attendance(self, subject, date):
        """Backup attendance data for a specific subject and date"""
        if not self.is_connected():
            print("Database not connected")
            return False

        csv_file = f"Attendance/{subject}/Attendance_{date}.csv"
        if not os.path.exists(csv_file):
            print(f"Attendance CSV file not found: {csv_file}")
            return False

        try:
            cursor = self.connection.cursor()

            # Read CSV and insert into database
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Check if student exists
                    cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (row['Id'],))
                    if not cursor.fetchone():
                        # Student doesn't exist, insert basic info
                        cursor.execute(
                            "INSERT INTO students (student_id, student_name) VALUES (%s, %s)",
                            (row['Id'], row['Name'])
                        )

                    # Insert attendance record
                    cursor.execute(
                        "INSERT INTO attendance (student_id, student_name, subject, date, time) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (row['Id'], row['Name'], row['Subject'],
                         datetime.strptime(row['Date'], '%d-%m-%Y').date(),
                         datetime.strptime(row['Time'], '%H:%M:%S').time())
                    )

            self.connection.commit()
            print(f"Successfully backed up attendance for {subject} on {date}")
            return True
        except Error as e:
            print(f"Error backing up attendance: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def restore_students(self):
        """Restore student data from database to CSV"""
        if not self.is_connected():
            print("Database not connected")
            return False

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students ORDER BY serial_no")
            students = cursor.fetchall()

            if not students:
                print("No student data found in database")
                return False

            # Prepare CSV data
            csv_data = [['SERIAL NO.', 'ID', 'NAME']]
            for student in students:
                csv_data.append([student['serial_no'], student['student_id'], student['student_name']])

            # Write to CSV
            os.makedirs("StudentDetails", exist_ok=True)
            with open("StudentDetails/StudentDetails.csv", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)

            print(f"Successfully restored {len(students)} students from database")
            return True
        except Error as e:
            print(f"Error restoring students: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def restore_attendance(self, subject, date):
        """Restore attendance data for a specific subject and date"""
        if not self.is_connected():
            print("Database not connected")
            return False

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM attendance WHERE subject = %s AND date = %s ORDER BY time",
                (subject, datetime.strptime(date, '%d-%m-%Y').date())
            )
            attendance_records = cursor.fetchall()

            if not attendance_records:
                print(f"No attendance records found for {subject} on {date}")
                return False

            # Prepare CSV data
            csv_data = [['Id', 'Name', 'Subject', 'Date', 'Time']]
            for record in attendance_records:
                csv_data.append([
                    record['student_id'],
                    record['student_name'],
                    record['subject'],
                    record['date'].strftime('%d-%m-%Y'),
                    record['time'].strftime('%H:%M:%S')
                ])

            # Write to CSV
            os.makedirs(f"Attendance/{subject}", exist_ok=True)
            with open(f"Attendance/{subject}/Attendance_{date}.csv", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)

            print(f"Successfully restored {len(attendance_records)} attendance records")
            return True
        except Error as e:
            print(f"Error restoring attendance: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_attendance_stats(self, subject=None, date=None):
        """Get attendance statistics"""
        if not self.is_connected():
            print("Database not connected")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)

            query = "SELECT COUNT(*) as total FROM attendance"
            params = []

            if subject and date:
                query += " WHERE subject = %s AND date = %s"
                params.extend([subject, datetime.strptime(date, '%d-%m-%Y').date()])
            elif subject:
                query += " WHERE subject = %s"
                params.append(subject)
            elif date:
                query += " WHERE date = %s"
                params.append(datetime.strptime(date, '%d-%m-%Y').date())

            cursor.execute(query, params)
            total = cursor.fetchone()['total']

            # Get hourly distribution
            hourly_query = """
                SELECT HOUR(time) as hour, COUNT(*) as count 
                FROM attendance
                {where_clause}
                GROUP BY HOUR(time)
                ORDER BY hour
            """.format(
                where_clause="WHERE subject = %s AND date = %s" if subject and date else
                "WHERE subject = %s" if subject else
                "WHERE date = %s" if date else ""
            )

            cursor.execute(hourly_query, params)
            hourly_dist = cursor.fetchall()

            return {
                'total': total,
                'hourly_distribution': hourly_dist
            }
        except Error as e:
            print(f"Error getting attendance stats: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")