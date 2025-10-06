import os
import cv2
import csv
import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from admin import create_admin_dashboard
capture_timestamp = None  # Global variable to share timestamp between attendance and image

# Define colors
BG_COLOR = "#f8f9fa"
BTN_COLOR = "#007bff"
TXT_COLOR = "#343a40"

# Create necessary directories
for folder in ["TrainingImage", "TrainingImageLabel", "EmployeeDetails", "Attendance"]:
    os.makedirs(folder, exist_ok=True)

# Function to switch slides
def show_frame(frame):
    frame.tkraise()

# Function to handle login
def login():
    username = entry_username.get()
    password = entry_password.get()

    if username == "admin" and password == "admin123":
        messagebox.showinfo("Login Success", "Admin Logged In!")
        show_frame(dashboard_frame)
    elif username.startswith("student") and password == "student123":
        messagebox.showinfo("Login Success", "Student Logged In!")
        show_frame(student_entry_frame)
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password!")

# Function to save student data and proceed
def save_student_data():
    global capture_timestamp
    roll_no = entry_roll.get()
    name = entry_name.get()
    student_class = entry_class.get()
    branch = entry_branch.get()
    subject = entry_subject.get()

    if roll_no and name and student_class and branch and subject:
        file_path = "EmployeeDetails/EmployeeDetails.csv"
        file_exists = os.path.isfile(file_path)

        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Roll No", "Name", "Class", "Branch", "Subject"])
            writer.writerow([roll_no, name, student_class, branch, subject])

        # Generate and store shared timestamp
        capture_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success = mark_attendance(roll_no, name, student_class, branch, subject, capture_timestamp)

        if success:
            show_frame(capture_image_frame)
    else:
        messagebox.showerror("Error", "Please fill all fields!")

#function to mark attendance
def mark_attendance(roll_no, name, student_class, branch, subject, timestamp):
    date = timestamp.split()[0]
    file_path = f"Attendance/Attendance_{date}.csv"

    current_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    one_hour_ago = current_time - datetime.timedelta(hours=1)

    file_exists = os.path.isfile(file_path)
    already_marked = False

    if file_exists:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Roll No"] == roll_no:
                    last_time = datetime.datetime.strptime(f"{date} {row['Timestamp']}", "%Y-%m-%d %H:%M:%S")
                    if last_time > one_hour_ago:
                        already_marked = True
                        break

    if already_marked:
        messagebox.showerror("Attendance Error ❌", "Attendance already marked within the last 60 minutes!")
        return False
    else:
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Roll No", "Name", "Class", "Branch", "Subject", "Timestamp"])
            writer.writerow([roll_no, name, student_class, branch, subject, current_time.strftime("%H:%M:%S")])
        messagebox.showinfo("Success ✅", "Attendance marked successfully!")
        return True

# Function to capture image
def capture_image():
    global last_captured_image, capture_timestamp

    if not capture_timestamp:
        messagebox.showerror("Error", "Timestamp missing. Cannot capture image.")
        return

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Image")

    timestamp_obj = datetime.datetime.strptime(capture_timestamp, "%Y-%m-%d %H:%M:%S")
    filename_timestamp = timestamp_obj.strftime('%Y%m%d%H%M%S')

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Image", frame)

        k = cv2.waitKey(1)
        if k % 256 == 32:  # Press 'Space' to capture image
            img_name = f"TrainingImage/{entry_roll.get()}_{filename_timestamp}.jpg"
            cv2.imwrite(img_name, frame)
            last_captured_image = img_name
            messagebox.showinfo("Success", "Image Captured Successfully!")
            break

    cam.release()
    cv2.destroyAllWindows()
    show_frame(login_frame)

# GUI Setup
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.attributes('-fullscreen', True)  # Full-screen mode
root.configure(bg=BG_COLOR)

# Create a container for slides
container = tk.Frame(root)
container.pack(fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Define all slides as Frames
welcome_frame = tk.Frame(container, bg=BG_COLOR)
login_frame = tk.Frame(container, bg=BG_COLOR)
student_entry_frame = tk.Frame(container, bg=BG_COLOR)
dashboard_frame = tk.Frame(container, bg=BG_COLOR)
capture_image_frame = tk.Frame(container, bg=BG_COLOR)

for frame in (welcome_frame, login_frame, student_entry_frame, dashboard_frame, capture_image_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# Load and scale the welcome image
image_path = "BestFacialRecognition.jpg"
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

original_img = Image.open(image_path)
img = original_img.resize((screen_width, screen_height))
photo = ImageTk.PhotoImage(img)

# Welcome Screen
welcome_label = tk.Label(welcome_frame, image=photo)
welcome_label.place(relwidth=1, relheight=1)

login_button = tk.Button(welcome_frame, text="Proceed to Login", bg=BTN_COLOR, fg="white",
                         font=("Arial", 16, "bold"), command=lambda: show_frame(login_frame))
login_button.place(relx=0.5, rely=0.8, anchor="center")

# ---- Load background and logo images for login slide ----
bg_img = Image.open("clock.jpg")
bg_img = bg_img.resize((screen_width, screen_height))
bg_photo = ImageTk.PhotoImage(bg_img)

logo_img = Image.open("ymcaLogo.jpg")
logo_img = logo_img.resize((150, 110))  # Adjust size for better layout
logo_photo = ImageTk.PhotoImage(logo_img)

# ---- Login Slide ----
login_bg_label = tk.Label(login_frame, image=bg_photo)
login_bg_label.place(relwidth=1, relheight=1)  # Set background

# Create a container frame to better arrange elements
login_container = tk.Frame(login_frame, bg=BG_COLOR, padx=20, pady=20)
login_container.place(relx=0.5, rely=0.4, anchor="center")  # Centered position

# Add logo at the top
logo_label = tk.Label(login_container, image=logo_photo, bg=BG_COLOR)
logo_label.pack(pady=(0, 20))  # Extra bottom padding

# Title label
tk.Label(login_container, text="Login Here", font=("Arial", 18, "bold"), 
         bg=BG_COLOR, fg=TXT_COLOR, padx=10, pady=5).pack(pady=(0, 15))  # Increased spacing

# Username field
username_frame = tk.Frame(login_container, bg=BG_COLOR)
username_frame.pack(fill="x", pady=5)
tk.Label(username_frame, text="Username:", bg=BG_COLOR, fg=TXT_COLOR, font=("Arial", 12, "bold")).pack(side="left", padx=10)
entry_username = tk.Entry(username_frame, font=("Arial", 12), width=30)
entry_username.pack(side="left", padx=10)

# Password field
password_frame = tk.Frame(login_container, bg=BG_COLOR)
password_frame.pack(fill="x", pady=5)
tk.Label(password_frame, text="Password:", bg=BG_COLOR, fg=TXT_COLOR, font=("Arial", 12, "bold")).pack(side="left", padx=10)
entry_password = tk.Entry(password_frame, show="*", font=("Arial", 12), width=30)
entry_password.pack(side="left", padx=10)

# Login Button
tk.Button(login_container, text="Login", font=("Arial", 12, "bold"), 
          bg=BTN_COLOR, fg="white", width=12, command=login).pack(pady=10)

# Quit Button
tk.Button(login_container, text="Quit", font=("Arial", 12, "bold"), 
          bg="red", fg="white", width=12, command=root.quit).pack(pady=5)

from tkinter import ttk  # Import for modern UI elements

# ---- Student Entry Slide (With Background Image) ----

# Load and set the background image
bg1_img = Image.open("bg.jpg")
bg1_img = bg1_img.resize((screen_width, screen_height))
bg1_photo = ImageTk.PhotoImage(bg1_img)

bg_label = tk.Label(student_entry_frame, image=bg1_photo)
bg_label.place(relwidth=1, relheight=1)  # Full-screen background

# Title Label
tk.Label(student_entry_frame, text="Student Dashboard", font=("Arial", 24, "bold"), 
         bg=BG_COLOR, fg=TXT_COLOR).pack(pady=20)

# Semi-transparent form card
form_frame = tk.Frame(student_entry_frame, bg="white", padx=30, pady=30, relief="raised", bd=2)
form_frame.place(relx=0.5, rely=0.5, anchor="center")  # Centered form

# Add University Logo
#logo_img = Image.open("ymcaLogo.jpg")
#logo_img = logo_img.resize((150, 75))  # Adjust size
#logo_photo = ImageTk.PhotoImage(logo_img)

#logo_label = tk.Label(form_frame, image=logo_photo, bg="white")
#logo_label.pack(pady=(0, 20))

# Fields with icons
fields_frame = tk.Frame(form_frame, bg="white")
fields_frame.pack()

labels = [
    "📜 Roll No:", "👤 Name:", "🏫 Class:", 
    "🔬 Branch:", "📘 Subject:"
]
entries = []

for label_text in labels:
    row_frame = tk.Frame(fields_frame, bg="white")  # Row container
    row_frame.pack(fill="x", pady=5, anchor="w")  # Align left
    
    label = tk.Label(row_frame, text=label_text, font=("Arial", 14, "bold"), 
                     bg="white", fg=TXT_COLOR, width=12, anchor="w")
    label.pack(side="left", padx=10)

    entry = ttk.Entry(row_frame, width=30, font=("Arial", 14))
    entry.pack(side="left", padx=10, pady=2, ipady=4)  # Rounded input
    entries.append(entry)

# Assign entry fields
entry_roll, entry_name, entry_class, entry_branch, entry_subject = entries

# Status message
status_label = tk.Label(form_frame, text="", font=("Arial", 12), fg="red", bg="white")
status_label.pack(pady=5)

# Function to update status label
def update_status(message, color="green"):
    status_label.config(text=message, fg=color)

# Buttons with hover effects
def on_enter(e): e.widget.config(bg="#0056b3")
def on_leave(e): e.widget.config(bg=BTN_COLOR)

save_btn = tk.Button(form_frame, text="✅ Save & Proceed", bg=BTN_COLOR, fg="white",
                     font=("Arial", 14, "bold"), width=18, command=save_student_data)
save_btn.pack(pady=10)
save_btn.bind("<Enter>", on_enter)
save_btn.bind("<Leave>", on_leave)

quit_btn = tk.Button(form_frame, text="❌ Quit", bg="red", fg="white",
                     font=("Arial", 14, "bold"), width=18, command=root.quit)
quit_btn.pack(pady=5)
quit_btn.bind("<Enter>", lambda e: quit_btn.config(bg="#b30000"))
quit_btn.bind("<Leave>", lambda e: quit_btn.config(bg="red"))

# ---- Capture Image Slide ----
tk.Label(capture_image_frame, text="Capture Image", bg=BG_COLOR, fg=TXT_COLOR, font=("Arial", 18, "bold")).pack(pady=20)
tk.Button(capture_image_frame, text="Capture", bg=BTN_COLOR, fg="white", command=capture_image).pack(pady=10)
show_frame(student_entry_frame)

# ---- Dashboard Slide ----
#tk.Label(dashboard_frame, text="Dashboard", bg=BG_COLOR, fg=TXT_COLOR, font=("Arial", 18, "bold")).pack(pady=20)
#tk.Button(dashboard_frame, text="Train Model", bg=BTN_COLOR, fg="white").pack(pady=5)
#tk.Button(dashboard_frame, text="Mark Attendance", bg=BTN_COLOR, fg="white").pack(pady=5)
#tk.Button(dashboard_frame, text="Logout", bg="red", fg="white", command=lambda: show_frame(login_frame)).pack(pady=20)

# Create Admin Dashboard
dashboard_frame = create_admin_dashboard(container, show_frame, login_frame)

# Add frames to the container
for frame in (welcome_frame, login_frame, student_entry_frame, dashboard_frame, capture_image_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# Start at Welcome Slide
show_frame(welcome_frame)

root.mainloop()
