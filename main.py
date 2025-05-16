
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2, os
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import shutil
import webbrowser
from database_handler import DatabaseHandler

############################################# FUNCTIONS ################################################
def backup_to_database():
    db = DatabaseHandler()
    if db.is_connected():
        # Backup students
        db.backup_students()

        # Backup all attendance records
        if os.path.exists("Attendance"):
            for subject in os.listdir("Attendance"):
                subject_path = os.path.join("Attendance", subject)
                if os.path.isdir(subject_path):
                    for att_file in os.listdir(subject_path):
                        if att_file.startswith("Attendance_") and att_file.endswith(".csv"):
                            date = att_file[11:-4]  # Extract date from filename
                            db.backup_attendance(subject, date)
        db.close()
    else:
        mess.showerror("Database Error", "Could not connect to database")


def restore_from_database():
    db = DatabaseHandler()
    if db.is_connected():
        if mess.askyesno("Confirm Restore", "This will overwrite all current data with database records. Continue?"):
            # Restore students
            db.restore_students()

            # Restore attendance (you might want to implement a selection dialog)
            # For now, we'll just show a message
            mess.showinfo("Restore",
                          "Students restored. Use the View Records option to restore specific attendance data.")
        db.close()
    else:
        mess.showerror("Database Error", "Could not connect to database")

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def tick():
    time_string = time.strftime('%H:%M:%S')
    time_label.config(text=time_string)
    window.after(200, tick)


def contact():
    webbrowser.open("mailto:yashnagapure25@gmail.com")


def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        mess.showerror(title='File Missing',
                       message='haarcascade_frontalface_default.xml not found. Please download it from OpenCV GitHub.')
        window.destroy()


def save_pass():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")

    if exists1:
        tf = open("TrainingImageLabel/psd.txt", "r")
        key = tf.read()
    else:
        master.destroy()
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas is None:
            mess.showwarning(title='No Password Entered', message='Password not set! Please try again')
        else:
            tf = open("TrainingImageLabel/psd.txt", "w")
            tf.write(new_pas)
            mess.showinfo(title='Password Registered', message='New password was registered successfully!')
            return

    op = old.get()
    newp = new.get()
    nnewp = nnew.get()

    if op == key:
        if newp == nnewp:
            txf = open("TrainingImageLabel/psd.txt", "w")
            txf.write(newp)
            mess.showinfo(title='Password Changed', message='Password changed successfully!')
            master.destroy()
        else:
            mess.showerror(title='Error', message='Confirm new password again!')
    else:
        mess.showerror(title='Wrong Password', message='Please enter correct old password.')


def change_pass():
    global master
    master = tk.Toplevel(window)
    master.title("Change Password")
    master.geometry("400x200")
    master.resizable(False, False)
    master.configure(bg="#f0f0f0")

    global old, new, nnew

    tk.Label(master, text="Enter Old Password:", bg="#f0f0f0", font=('Helvetica', 12)).pack(pady=5)
    old = tk.Entry(master, width=25, show='*', font=('Helvetica', 12))
    old.pack()

    tk.Label(master, text="Enter New Password:", bg="#f0f0f0", font=('Helvetica', 12)).pack(pady=5)
    new = tk.Entry(master, width=25, show='*', font=('Helvetica', 12))
    new.pack()

    tk.Label(master, text="Confirm New Password:", bg="#f0f0f0", font=('Helvetica', 12)).pack(pady=5)
    nnew = tk.Entry(master, width=25, show='*', font=('Helvetica', 12))
    nnew.pack()

    btn_frame = tk.Frame(master, bg="#f0f0f0")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Save", command=save_pass, bg="#4CAF50", fg="white",
              font=('Helvetica', 10), width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=master.destroy, bg="#f44336", fg="white",
              font=('Helvetica', 10), width=10).pack(side=tk.LEFT, padx=5)


def psw():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")

    if exists1:
        tf = open("TrainingImageLabel/psd.txt", "r")
        key = tf.read()
    else:
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas is None:
            mess.showwarning(title='No Password Entered', message='Password not set! Please try again')
        else:
            tf = open("TrainingImageLabel/psd.txt", "w")
            tf.write(new_pas)
            mess.showinfo(title='Password Registered', message='New password was registered successfully!')
            return

    password = tsd.askstring('Password', 'Enter Password', show='*')
    if password == key:
        TrainImages()
    elif password is None:
        pass
    else:
        mess.showerror(title='Wrong Password', message='You have entered wrong password')


def clear_entries():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    status_label.config(text="1) Take Images  >>>  2) Save Profile")


def TakeImages():
    check_haarcascadefile()
    columns = ['SERIAL NO.', 'ID', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")

    serial = 0
    exists = os.path.isfile("StudentDetails/StudentDetails.csv")

    if exists:
        with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            serial = sum(1 for _ in reader1)
        csvFile1.close()
    else:
        with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
        csvFile1.close()

    Id = id_entry.get().strip()
    name = name_entry.get().strip()

    if not name.replace(' ', '').isalpha():
        mess.showerror(title="Invalid Name", message="Name must contain only alphabets and spaces")
        return

    if not Id:
        mess.showerror(title="Empty Field", message="Please enter Student ID")
        return

    if not Id.isdigit():
        mess.showerror(title="Invalid ID", message="Student ID must be numeric")
        return

    # Check if ID already exists
    if exists:
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
        if Id in df['ID'].values:
            mess.showerror("ID Exists", "This Student ID already exists!")
            return

    cam = cv2.VideoCapture(0)
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0

    cv2.namedWindow("Taking Images", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Taking Images", 800, 600)

    while True:
        ret, img = cam.read()
        if not ret:
            mess.showerror("Camera Error", "Could not access camera")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(100, 100))

        if len(faces) == 0:
            cv2.putText(img, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            sampleNum += 1
            face_roi = gray[y:y + h, x:x + w]
            if face_roi.size == 0:
                continue

            cv2.imwrite(f"TrainingImage/{name}.{Id}.{sampleNum}.jpg", face_roi)
            cv2.putText(img, f"Captured: {sampleNum}/100", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow('Taking Images', img)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif sampleNum >= 100:
            break

    cam.release()
    cv2.destroyAllWindows()

    if sampleNum > 0:
        row = [serial, Id, name]
        with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)

        status_label.config(text=f"Successfully captured {sampleNum} images for ID: {Id}")
        update_registration_count()
        update_student_tree()
    else:
        mess.showerror("Error", "No faces were captured. Please try again.")


def TrainImages():
    check_haarcascadefile()
    assure_path_exists("TrainingImageLabel/")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)

    faces, Id = getImagesAndLabels("TrainingImage")

    if not Id:
        mess.showwarning(title='No Data', message='Please register someone first!')
        return

    try:
        recognizer.train(faces, np.array(Id))
    except Exception as e:
        mess.showerror(title='Error', message=f'Training failed: {str(e)}')
        return

    recognizer.save("TrainingImageLabel/Trainner.yml")
    status_label.config(text="Profile Saved Successfully")
    update_registration_count()


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
    faces = []
    Ids = []

    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')

            # Extract ID from filename (format: Name.ID.SampleNo.jpg)
            Id = int(os.path.split(imagePath)[-1].split(".")[1])

            faces.append(imageNp)
            Ids.append(Id)
        except Exception as e:
            print(f"Error processing {imagePath}: {str(e)}")
            continue

    return faces, Ids


def TrackImages():
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")

    subject = subject_entry.get().strip()
    if not subject:
        mess.showerror("Error", "Please enter subject name")
        return

    for k in att_tree.get_children():
        att_tree.delete(k)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    exists3 = os.path.isfile("TrainingImageLabel/Trainner.yml")

    if not exists3:
        mess.showerror(title='Data Missing', message='Please click on Save Profile to train the data first!')
        return

    try:
        recognizer.read("TrainingImageLabel/Trainner.yml")
    except Exception as e:
        mess.showerror("Error", f"Failed to load trainer data: {str(e)}")
        return

    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)

    try:
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
    except Exception as e:
        mess.showerror("Error", f"Failed to load student details: {str(e)}")
        return

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        mess.showerror("Error", "Could not open camera")
        return

    font = cv2.FONT_HERSHEY_SIMPLEX

    attendance_window = tk.Toplevel(window)
    attendance_window.title(f"Live Attendance Tracking - {subject}")
    attendance_window.geometry("1000x700")
    attendance_window.configure(bg="#f0f0f0")

    subject_attendance_dir = f"Attendance/{subject}"
    assure_path_exists(subject_attendance_dir)

    video_label = tk.Label(attendance_window)
    video_label.pack(pady=10)

    info_frame = tk.Frame(attendance_window, bg="#f0f0f0")
    info_frame.pack(pady=10)

    recognized_label = tk.Label(info_frame, text="Recognized: ", font=('Helvetica', 14), bg="#f0f0f0")
    recognized_label.pack(side=tk.LEFT, padx=10)

    confidence_label = tk.Label(info_frame, text="Confidence: ", font=('Helvetica', 14), bg="#f0f0f0")
    confidence_label.pack(side=tk.LEFT, padx=10)

    stop_button = tk.Button(attendance_window, text="Stop Attendance",
                            command=lambda: [cam.release(), cv2.destroyAllWindows(), attendance_window.destroy()],
                            bg="#f44336", fg="white", font=('Helvetica', 12))
    stop_button.pack(pady=10)

    attendance_list = []
    marked_ids = set()

    def update_frame():
        nonlocal marked_ids
        ret, im = cam.read()

        if not ret:
            recognized_label.config(text="Camera Error")
            return

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])

            if conf < 50:
                try:
                    student_info = df[df['ID'] == Id].iloc[0]  # Search by ID
                    bb = student_info['NAME']
                    ID = student_info['ID']

                    recognized_label.config(text=f"Recognized: {bb} (ID: {ID})")
                    confidence_label.config(text=f"Confidence: {round(100 - conf, 2)}%")

                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

                    if ID not in marked_ids:
                        marked_ids.add(ID)
                        attendance_list.append([ID, bb, subject, date, timeStamp])
                        cv2.putText(im, "Attendance Marked", (x, y + h + 30), font, 0.8, (0, 255, 0), 2)
                        att_tree.insert('', 'end', values=(bb, ID, subject, date, timeStamp))
                        save_attendance_entry(ID, bb, subject, date, timeStamp)
                    else:
                        cv2.putText(im, "Already Marked", (x, y + h + 30), font, 0.8, (0, 0, 255), 2)
                except IndexError:
                    recognized_label.config(text="Recognized: Unknown")
                    confidence_label.config(text="Confidence: -")
            else:
                recognized_label.config(text="Recognized: Unknown")
                confidence_label.config(text="Confidence: -")

        img = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        video_label.after(10, update_frame)

    def save_attendance_entry(student_id, name, subject, date, time):
        subject_attendance_dir = f"Attendance/{subject}"
        os.makedirs(subject_attendance_dir, exist_ok=True)
        attendance_file = f"{subject_attendance_dir}/Attendance_{date}.csv"

        file_exists = os.path.isfile(attendance_file)
        with open(attendance_file, 'a+', newline='') as csvFile:
            writer = csv.writer(csvFile)
            if not file_exists:
                writer.writerow(['Id', 'Name', 'Subject', 'Date', 'Time'])
            writer.writerow([student_id, name, subject, date, time])

    update_frame()

    attendance_window.protocol("WM_DELETE_WINDOW", lambda: [cam.release(), cv2.destroyAllWindows(),
                                                            attendance_window.destroy()])


def view_attendance():
    view_window = tk.Toplevel(window)
    view_window.title("View Attendance Records")
    view_window.geometry("1200x700")
    view_window.configure(bg="#f0f0f0")

    if not os.path.exists("Attendance"):
        mess.showinfo("No Records", "No attendance records found")
        view_window.destroy()
        return

    subjects = [d for d in os.listdir("Attendance") if os.path.isdir(os.path.join("Attendance", d))]

    if not subjects:
        mess.showinfo("No Records", "No attendance records found")
        view_window.destroy()
        return

    subject_frame = tk.Frame(view_window, bg="#f0f0f0")
    subject_frame.pack(pady=10)

    tk.Label(subject_frame, text="Select Subject:", bg="#f0f0f0", font=('Helvetica', 12)).pack(side=tk.LEFT, padx=5)

    subject_var = tk.StringVar(view_window)
    subject_var.set(subjects[0])

    subject_menu = tk.OptionMenu(subject_frame, subject_var, *subjects)
    subject_menu.pack(side=tk.LEFT, padx=5)

    date_frame = tk.Frame(view_window, bg="#f0f0f0")
    date_frame.pack(pady=5)

    tk.Label(date_frame, text="Select Date:", bg="#f0f0f0", font=('Helvetica', 12)).pack(side=tk.LEFT, padx=5)

    date_var = tk.StringVar(view_window)
    date_menu = tk.OptionMenu(date_frame, date_var, "")
    date_menu.pack(side=tk.LEFT, padx=5)

    def update_dates(*args):
        selected_subject = subject_var.get()
        attendance_dir = f"Attendance/{selected_subject}"

        if os.path.exists(attendance_dir):
            attendance_files = [f for f in os.listdir(attendance_dir) if
                                f.startswith("Attendance_") and f.endswith(".csv")]
            dates = [f[11:-4] for f in attendance_files]

            date_menu['menu'].delete(0, 'end')
            for date in dates:
                date_menu['menu'].add_command(label=date, command=tk._setit(date_var, date))

            if dates:
                date_var.set(dates[0])
                load_attendance(selected_subject, dates[0])
            else:
                date_var.set("")
                for item in attendance_tree.get_children():
                    attendance_tree.delete(item)
        else:
            date_var.set("")
            for item in attendance_tree.get_children():
                attendance_tree.delete(item)

    subject_var.trace('w', update_dates)

    button_frame = tk.Frame(view_window, bg="#f0f0f0")
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Load", command=lambda: load_attendance(subject_var.get(), date_var.get()),
              bg="#4CAF50", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Export to Excel",
              command=lambda: export_attendance(subject_var.get(), date_var.get()),
              bg="#2196F3", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="View Stats", command=lambda: show_stats(subject_var.get(), date_var.get()),
              bg="#9C27B0", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(view_window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_y = ttk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    attendance_tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Subject', 'Date', 'Time'),
                                   show='headings', yscrollcommand=scroll_y.set)

    attendance_tree.heading('ID', text='ID')
    attendance_tree.heading('Name', text='Name')
    attendance_tree.heading('Subject', text='Subject')
    attendance_tree.heading('Date', text='Date')
    attendance_tree.heading('Time', text='Time')

    attendance_tree.column('ID', width=100, anchor=tk.CENTER)
    attendance_tree.column('Name', width=200, anchor=tk.CENTER)
    attendance_tree.column('Subject', width=150, anchor=tk.CENTER)
    attendance_tree.column('Date', width=150, anchor=tk.CENTER)
    attendance_tree.column('Time', width=150, anchor=tk.CENTER)

    attendance_tree.pack(fill=tk.BOTH, expand=True)
    scroll_y.config(command=attendance_tree.yview)

    def load_attendance(subject, date):
        for item in attendance_tree.get_children():
            attendance_tree.delete(item)

        attendance_file = f"Attendance/{subject}/Attendance_{date}.csv"

        if os.path.exists(attendance_file):
            try:
                with open(attendance_file, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        attendance_tree.insert('', 'end',
                                               values=(
                                                   row['Id'], row['Name'], row['Subject'], row['Date'], row['Time']))
            except Exception as e:
                mess.showerror("Error", f"Failed to load attendance: {str(e)}")
        else:
            mess.showwarning("File Not Found", f"No attendance records found for {subject} on {date}")

    def export_attendance(subject, date):
        attendance_file = f"Attendance/{subject}/Attendance_{date}.csv"

        if os.path.exists(attendance_file):
            export_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                       filetypes=[("Excel files", "*.xlsx")],
                                                       title="Save attendance as")
            if export_path:
                try:
                    df = pd.read_csv(attendance_file)
                    df.to_excel(export_path, index=False)
                    mess.showinfo("Success", f"Attendance exported to {export_path}")
                except Exception as e:
                    mess.showerror("Error", f"Failed to export attendance: {str(e)}")
        else:
            mess.showwarning("File Not Found", f"No attendance records found for {subject} on {date}")

    def show_stats(subject, date):
        attendance_file = f"Attendance/{subject}/Attendance_{date}.csv"

        if os.path.exists(attendance_file):
            try:
                df = pd.read_csv(attendance_file)

                stats_window = tk.Toplevel(view_window)
                stats_window.title(f"Attendance Statistics - {subject} ({date})")
                stats_window.geometry("800x600")

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
                fig.suptitle(f"Attendance Statistics - {subject} ({date})")

                attendance_count = len(df)
                ax1.bar(['Total Attendance'], [attendance_count], color='skyblue')
                ax1.set_title('Total Attendance Count')
                ax1.set_ylabel('Number of Students')

                df['Time'] = pd.to_datetime(df['Time'])
                df['Hour'] = df['Time'].dt.hour
                time_dist = df['Hour'].value_counts().sort_index()
                time_dist.plot(kind='bar', ax=ax2, color='lightgreen')
                ax2.set_title('Attendance Time Distribution')
                ax2.set_xlabel('Hour of Day')
                ax2.set_ylabel('Number of Students')

                canvas = FigureCanvasTkAgg(fig, master=stats_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                tk.Button(stats_window, text="Close", command=stats_window.destroy,
                          bg="#f44336", fg="white").pack(pady=10)
            except Exception as e:
                mess.showerror("Error", f"Failed to generate stats: {str(e)}")
        else:
            mess.showwarning("File Not Found", f"No attendance records found for {subject} on {date}")

    update_dates()


def backup_data():
    if not os.path.exists("Backup"):
        os.makedirs("Backup")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"Backup/Attendance_System_Backup_{timestamp}"
    os.makedirs(backup_folder)

    folders_to_backup = ["StudentDetails", "TrainingImage", "TrainingImageLabel", "Attendance"]

    for folder in folders_to_backup:
        if os.path.exists(folder):
            shutil.copytree(folder, f"{backup_folder}/{folder}")

    mess.showinfo("Backup Complete", f"All data has been backed up to:\n{backup_folder}")


def restore_data():
    backup_folder = filedialog.askdirectory(title="Select Backup Folder to Restore",
                                            initialdir="Backup")
    if not backup_folder:
        return

    required_folders = ["StudentDetails", "TrainingImage", "TrainingImageLabel", "Attendance"]
    valid_backup = all(os.path.exists(f"{backup_folder}/{folder}") for folder in required_folders)

    if not valid_backup:
        mess.showerror("Invalid Backup", "The selected folder doesn't contain valid backup data.")
        return

    if not mess.askyesno("Confirm Restore", "This will overwrite all current data. Continue?"):
        return

    try:
        for folder in required_folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            shutil.copytree(f"{backup_folder}/{folder}", folder)

        mess.showinfo("Restore Complete", "Data has been successfully restored.")
        update_registration_count()
        update_student_tree()
    except Exception as e:
        mess.showerror("Restore Error", f"An error occurred during restore:\n{str(e)}")


def reset_system():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")

    if exists1:
        # Use 'with' to ensure the file is automatically closed
        with open("TrainingImageLabel/psd.txt", "r") as tf:
            key = tf.read()
    else:
        mess.showwarning(title='No Password', message='System password not set!')
        return

    # Ask for admin password
    password = tsd.askstring('Password', 'Enter Admin Password to Reset System', show='*')
    if password != key:
        mess.showerror(title='Wrong Password', message='Incorrect password!')
        return

    # Confirm reset
    if not mess.askyesno("Confirm Reset", "WARNING: This will delete ALL data including:\n\n"
                                          "- All registered students\n- All attendance records\n- All training images\n\n"
                                          "This action cannot be undone. Continue?"):
        return

    try:
        # Delete CSV file
        if os.path.exists("StudentDetails/StudentDetails.csv"):
            os.remove("StudentDetails/StudentDetails.csv")

        # Clear and recreate directories
        for folder in ["TrainingImage", "TrainingImageLabel", "Attendance"]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.makedirs(folder)

        # Clear the attendance tree
        for item in att_tree.get_children():
            att_tree.delete(item)

        update_registration_count()

        mess.showinfo("System Reset", "All system data has been successfully reset.")

    except Exception as e:
        mess.showerror("Reset Error", f"An error occurred during reset:\n{str(e)}")


def update_registration_count():
    count = 0
    if os.path.exists("StudentDetails/StudentDetails.csv"):
        with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
            reader = csv.reader(csvFile1)
            next(reader)  # Skip header row
            count = sum(1 for _ in reader)

    count_label.config(text=f"Total Registrations: {count}")


def open_documentation():
    webbrowser.open("https://github.com/yashn555")


def show_developer_info():
    dev_window = tk.Toplevel(window)
    dev_window.title("Developer Information")
    dev_window.geometry("400x300")
    dev_window.configure(bg="#f0f0f0")

    tk.Label(dev_window, text="Face Recognition Attendance System",
             font=('Helvetica', 16, 'bold'), bg="#f0f0f0").pack(pady=10)

    tk.Label(dev_window, text="Version: 2.1", bg="#f0f0f0").pack()
    tk.Label(dev_window, text="Developed By:", bg="#f0f0f0").pack(pady=(10, 0))

    dev_info = """
    Yash Nagapure
    yashnagapure25@gmail.com

    © 2025 All Rights Reserved
    """

    tk.Label(dev_window, text=dev_info, bg="#f0f0f0", justify=tk.LEFT).pack()

    tk.Button(dev_window, text="Close", command=dev_window.destroy,
              bg="#4CAF50", fg="white").pack(pady=10)


def manage_students():
    manage_window = tk.Toplevel(window)
    manage_window.title("Student Management")
    manage_window.geometry("1000x600")
    manage_window.configure(bg="#f0f0f0")

    tree_frame = tk.Frame(manage_window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_y = ttk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    global student_tree
    student_tree = ttk.Treeview(tree_frame, columns=('Serial', 'ID', 'Name'),
                                show='headings', yscrollcommand=scroll_y.set)

    student_tree.heading('Serial', text='Serial No.')
    student_tree.heading('ID', text='Student ID')
    student_tree.heading('Name', text='Student Name')

    student_tree.column('Serial', width=100, anchor=tk.CENTER)
    student_tree.column('ID', width=150, anchor=tk.CENTER)
    student_tree.column('Name', width=300, anchor=tk.CENTER)

    student_tree.pack(fill=tk.BOTH, expand=True)
    scroll_y.config(command=student_tree.yview)

    btn_frame = tk.Frame(manage_window, bg="#f0f0f0")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Refresh", command=update_student_tree,
              bg="#2196F3", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete Selected", command=delete_student,
              bg="#f44336", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Update Selected", command=update_student,
              bg="#4CAF50", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=manage_window.destroy,
              bg="#9E9E9E", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)

    update_student_tree()


def update_student_tree():
    for item in student_tree.get_children():
        student_tree.delete(item)

    if os.path.exists("StudentDetails/StudentDetails.csv"):
        with open("StudentDetails/StudentDetails.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student_tree.insert('', 'end', values=(row['SERIAL NO.'], row['ID'], row['NAME']))


def delete_student():
    selected_item = student_tree.selection()
    if not selected_item:
        mess.showwarning("No Selection", "Please select a student to delete")
        return

    student_data = student_tree.item(selected_item, 'values')
    student_id = student_data[1]
    student_name = student_data[2]

    if not mess.askyesno("Confirm Delete", f"Delete student {student_name} (ID: {student_id})?"):
        return

    try:
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
        df = df[df['ID'] != student_id]
        df.to_csv("StudentDetails/StudentDetails.csv", index=False)

        image_files = [f for f in os.listdir("TrainingImage") if f.split('.')[1] == student_id]
        for f in image_files:
            os.remove(os.path.join("TrainingImage", f))

        update_student_tree()
        update_registration_count()
        TrainImages()

        mess.showinfo("Success", "Student deleted successfully")
    except Exception as e:
        mess.showerror("Error", f"Failed to delete student: {str(e)}")


def update_student():
    selected_item = student_tree.selection()
    if not selected_item:
        mess.showwarning("No Selection", "Please select a student to update")
        return

    student_data = student_tree.item(selected_item, 'values')
    serial_no = student_data[0]
    old_id = student_data[1]
    old_name = student_data[2]

    update_window = tk.Toplevel(window)
    update_window.title("Update Student")
    update_window.geometry("400x250")
    update_window.resizable(False, False)
    update_window.configure(bg="#f0f0f0")

    tk.Label(update_window, text="Student ID:", bg="#f0f0f0", font=('Helvetica', 12)).grid(row=0, column=0, padx=10,
                                                                                           pady=10, sticky=tk.W)
    id_entry = tk.Entry(update_window, font=('Helvetica', 12), width=25)
    id_entry.grid(row=0, column=1, padx=10, pady=10)
    id_entry.insert(0, old_id)

    tk.Label(update_window, text="Student Name:", bg="#f0f0f0", font=('Helvetica', 12)).grid(row=1, column=0, padx=10,
                                                                                             pady=10, sticky=tk.W)
    name_entry = tk.Entry(update_window, font=('Helvetica', 12), width=25)
    name_entry.grid(row=1, column=1, padx=10, pady=10)
    name_entry.insert(0, old_name)

    def save_changes():
        new_id = id_entry.get()
        new_name = name_entry.get()

        if not new_name.replace(' ', '').isalpha():
            mess.showerror(title="Invalid Name", message="Name must contain only alphabets and spaces")
            return

        if not new_id:
            mess.showerror(title="Empty Field", message="Please enter Student ID")
            return

        if not new_id.isdigit():
            mess.showerror(title="Invalid ID", message="Student ID must be numeric")
            return

        try:
            df = pd.read_csv("StudentDetails/StudentDetails.csv")

            if (new_id != old_id) and (new_id in df['ID'].values):
                mess.showerror("ID Exists", "This Student ID already exists!")
                return

            df.loc[df['ID'] == old_id, 'ID'] = new_id
            df.loc[df['ID'] == new_id, 'NAME'] = new_name
            df.to_csv("StudentDetails/StudentDetails.csv", index=False)

            if new_id != old_id:
                image_files = [f for f in os.listdir("TrainingImage") if f.split('.')[1] == old_id]
                for f in image_files:
                    parts = f.split('.')
                    new_filename = f"{parts[0]}.{new_id}.{parts[2]}.{parts[3]}"
                    os.rename(os.path.join("TrainingImage", f), os.path.join("TrainingImage", new_filename))

            update_student_tree()
            update_registration_count()
            TrainImages()

            mess.showinfo("Success", "Student updated successfully")
            update_window.destroy()
        except Exception as e:
            mess.showerror("Error", f"Failed to update student: {str(e)}")

    btn_frame = tk.Frame(update_window, bg="#f0f0f0")
    btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

    tk.Button(btn_frame, text="Save", command=save_changes,
              bg="#4CAF50", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", command=update_window.destroy,
              bg="#f44336", fg="white", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=10)


############################################# MAIN GUI #############################################

window = tk.Tk()
window.title("Advanced Face Recognition Attendance System")
window.geometry("1280x800")
window.configure(bg='#2c3e50')

# Header
header_frame = tk.Frame(window, bg="#3498db", height=80)
header_frame.pack(fill=tk.X)

title_label = tk.Label(header_frame, text="FACE RECOGNITION ATTENDANCE SYSTEM",
                       font=('Helvetica', 24, 'bold'), bg="#3498db", fg="white")
title_label.pack(pady=20)

# Main content
main_frame = tk.Frame(window, bg="#ecf0f1")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Left frame (Registration)
left_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.RIDGE)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Right frame (Attendance)
right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.RIDGE)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Registration Section
reg_header = tk.Label(left_frame, text="STUDENT REGISTRATION", font=('Helvetica', 16, 'bold'),
                      bg="#2ecc71", fg="white", padx=10, pady=5)
reg_header.pack(fill=tk.X)

reg_content = tk.Frame(left_frame, bg="#ffffff", padx=10, pady=10)
reg_content.pack(fill=tk.BOTH, expand=True)

# ID Entry
tk.Label(reg_content, text="Student ID:", bg="#ffffff", font=('Helvetica', 12)).grid(row=0, column=0, sticky=tk.W,
                                                                                     pady=5)
id_entry = tk.Entry(reg_content, font=('Helvetica', 12), width=25)
id_entry.grid(row=0, column=1, pady=5, padx=5)

# Name Entry
tk.Label(reg_content, text="Student Name:", bg="#ffffff", font=('Helvetica', 12)).grid(row=1, column=0, sticky=tk.W,
                                                                                       pady=5)
name_entry = tk.Entry(reg_content, font=('Helvetica', 12), width=25)
name_entry.grid(row=1, column=1, pady=5, padx=5)

# Buttons
btn_frame = tk.Frame(reg_content, bg="#ffffff")
btn_frame.grid(row=2, column=0, columnspan=2, pady=15)

take_img_btn = tk.Button(btn_frame, text="Take Images", command=TakeImages,
                         bg="#3498db", fg="white", font=('Helvetica', 12), width=15)
take_img_btn.pack(side=tk.LEFT, padx=5)

train_img_btn = tk.Button(btn_frame, text="Save Profile", command=psw,
                          bg="#2ecc71", fg="white", font=('Helvetica', 12), width=15)
train_img_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear", command=clear_entries,
                      bg="#f39c12", fg="white", font=('Helvetica', 12), width=10)
clear_btn.pack(side=tk.LEFT, padx=5)

# Status message
status_label = tk.Label(reg_content, text="1) Take Images  >>>  2) Save Profile",
                        bg="#ffffff", font=('Helvetica', 11), fg="#7f8c8d")
status_label.grid(row=3, column=0, columnspan=2, pady=10)

# Registration count
count_label = tk.Label(reg_content, text="Total Registrations: 0",
                       bg="#ffffff", font=('Helvetica', 12, 'bold'), fg="#e74c3c")
count_label.grid(row=4, column=0, columnspan=2, pady=10)

# Manage Students button
manage_btn = tk.Button(reg_content, text="Manage Students", command=manage_students,
                       bg="#9b59b6", fg="white", font=('Helvetica', 12), width=20)
manage_btn.grid(row=5, column=0, columnspan=2, pady=10)

# Attendance Section
att_header = tk.Label(right_frame, text="ATTENDANCE MANAGEMENT", font=('Helvetica', 16, 'bold'),
                      bg="#e74c3c", fg="white", padx=10, pady=5)
att_header.pack(fill=tk.X)

att_content = tk.Frame(right_frame, bg="#ffffff")
att_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Subject Entry
subject_frame = tk.Frame(att_content, bg="#ffffff")
subject_frame.pack(fill=tk.X, pady=5)

tk.Label(subject_frame, text="Subject Name:", bg="#ffffff", font=('Helvetica', 12)).pack(side=tk.LEFT, padx=5)
subject_entry = tk.Entry(subject_frame, font=('Helvetica', 12), width=25)
subject_entry.pack(side=tk.LEFT, padx=5)

# Treeview for attendance records
tree_frame = tk.Frame(att_content, bg="#ffffff")
tree_frame.pack(fill=tk.BOTH, expand=True)

scroll_y = ttk.Scrollbar(tree_frame)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

att_tree = ttk.Treeview(tree_frame, columns=('Name', 'ID', 'Subject', 'Date', 'Time'),
                        show='headings', yscrollcommand=scroll_y.set)

att_tree.heading('Name', text='Name')
att_tree.heading('ID', text='ID')
att_tree.heading('Subject', text='Subject')
att_tree.heading('Date', text='Date')
att_tree.heading('Time', text='Time')

att_tree.column('Name', width=200, anchor=tk.CENTER)
att_tree.column('ID', width=100, anchor=tk.CENTER)
att_tree.column('Subject', width=150, anchor=tk.CENTER)
att_tree.column('Date', width=150, anchor=tk.CENTER)
att_tree.column('Time', width=150, anchor=tk.CENTER)

att_tree.pack(fill=tk.BOTH, expand=True)
scroll_y.config(command=att_tree.yview)

# Buttons for attendance
att_btn_frame = tk.Frame(att_content, bg="#ffffff")
att_btn_frame.pack(fill=tk.X, pady=10)

take_att_btn = tk.Button(att_btn_frame, text="Take Attendance", command=TrackImages,
                         bg="#e74c3c", fg="white", font=('Helvetica', 12), width=20)
take_att_btn.pack(side=tk.LEFT, padx=5)

view_att_btn = tk.Button(att_btn_frame, text="View Records", command=view_attendance,
                         bg="#9b59b6", fg="white", font=('Helvetica', 12), width=15)
view_att_btn.pack(side=tk.LEFT, padx=5)

# Footer
footer_frame = tk.Frame(window, bg="#34495e", height=40)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

date_label = tk.Label(footer_frame, text="", font=('Helvetica', 10), bg="#34495e", fg="white")
date_label.pack(side=tk.LEFT, padx=10)

time_label = tk.Label(footer_frame, text="", font=('Helvetica', 10), bg="#34495e", fg="white")
time_label.pack(side=tk.RIGHT, padx=10)


# Update date and time
def update_datetime():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M:%S %p")
    date_label.config(text=date_str)
    time_label.config(text=time_str)
    window.after(1000, update_datetime)


update_datetime()

# Menu bar
menubar = tk.Menu(window)

# File menu
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Backup Data", command=backup_data)
filemenu.add_command(label="Restore Data", command=restore_data)
filemenu.add_command(label="Reset System", command=reset_system)
# In the File menu section, add these commands:
filemenu.add_command(label="Backup to Database", command=backup_to_database)
filemenu.add_command(label="Restore from Database", command=restore_from_database)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.destroy)
menubar.add_cascade(label="File", menu=filemenu)

# Tools menu
toolsmenu = tk.Menu(menubar, tearoff=0)
toolsmenu.add_command(label="Change Password", command=change_pass)
menubar.add_cascade(label="Tools", menu=toolsmenu)

# Help menu
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Documentation", command=open_documentation)
helpmenu.add_command(label="Developer Info", command=show_developer_info)
helpmenu.add_command(label="Contact Us", command=contact)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)

# Initialize the registration count
update_registration_count()

# Start the main loop
window.mainloop()