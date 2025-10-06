import os
import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv

# Define colors & styles
BG_COLOR = "#f8f9fa"  # Light Gray
BTN_COLOR = "#007bff"  # Blue
BTN_HOVER_COLOR = "#0056b3"  # Dark Blue on Hover
TXT_COLOR = "#343a40"  # Dark Gray
LOGOUT_COLOR = "#ff9800"  # Orange
EXIT_COLOR = "#dc3545"  # Red
FONT = ("Arial", 16, "bold")

# Paths to icons
ICON_PATHS = {
    "View Attendance": "viewAttendance.jpg",
    "Manage Students": "manage.jpg",
    "Search Student Records": "search.jpg",  # Add your icon file here
    "Logout": "logout.jpg",
    "Exit": "exit.jpg"
}

def create_admin_dashboard(parent, show_frame, login_frame):
    dashboard_frame = tk.Frame(parent, bg=BG_COLOR)
    dashboard_frame.grid(row=0, column=0, sticky="nsew")

    # Get screen size
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()

    # Load and place background image
    try:
        bg_image = Image.open("admin.jpg")  
        bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)  
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(dashboard_frame, image=bg_photo)
        bg_label.image = bg_photo  
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Error loading background image: {e}")
        bg_label = tk.Label(dashboard_frame, text="Admin Dashboard", font=("Arial", 24, "bold"), bg=BG_COLOR, fg="black")
        bg_label.pack(pady=20)

    # Welcome Label
    tk.Label(dashboard_frame, text="Welcome, Admin", fg="white", bg="black", 
             font=("Arial", 28, "bold")).pack(pady=20)

    def view_attendance_report():
       today_date = datetime.datetime.now().strftime("%Y-%m-%d")
       file_path = os.path.abspath(f"Attendance/Attendance_{today_date}.csv")
       print(f"Checking for file: {file_path}")  # Debugging: Print the file path

       if os.path.exists(file_path):
        # Open the attendance CSV file
          with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            attendance_data = list(reader)

          print(f"Attendance Data: {attendance_data}")  # Debugging: Print the attendance data

          if attendance_data:
            # Create a new popup window to display the attendance and images
            report_window = tk.Toplevel()
            report_window.title(f"Attendance Report - {today_date}")
            report_window.geometry("800x600")
            report_window.config(bg=BG_COLOR)

            # Create a Canvas and a scrollbar for handling large data
            canvas = tk.Canvas(report_window, bg=BG_COLOR)
            scrollbar = tk.Scrollbar(report_window, orient="vertical", command=canvas.yview)
            frame = tk.Frame(canvas, bg=BG_COLOR)
            canvas.config(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            canvas.create_window((0, 0), window=frame, anchor="nw")

            # Loop through the attendance data and display it along with images
            for idx, student in enumerate(attendance_data):
                # Student info
                student_info = f"Roll No: {student['Roll No']}\n"
                student_info += f"Name: {student['Name']}\n"
                student_info += f"Class: {student['Class']}\n"
                student_info += f"Branch: {student['Branch']}\n"
                student_info += f"Subject: {student['Subject']}\n"
                student_info += f"Timestamp: {student['Timestamp']}"

                # Show student info label
                student_info_label = tk.Label(frame, text=student_info, font=("Arial", 12), bg=BG_COLOR)
                student_info_label.grid(row=idx, column=0, padx=10, pady=10, sticky="w")

                # Try to load and display the image
                try:
                    # Clean up the timestamp (remove any milliseconds)
                    timestamp_clean = student['Timestamp'].replace(":", "").split('.')[0]  # Remove milliseconds
                    image_filename = f"{student['Roll No']}_{today_date.replace('-', '')}{timestamp_clean}.jpg"
                    image_path = os.path.join("TrainingImage", image_filename)

                    print(f"Image Path: {image_path}")  # Debugging: Print the image path

                    # Check if the exact image file exists
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        img = img.resize((100, 120), Image.LANCZOS)  # Resize image to fit well
                        img_tk = ImageTk.PhotoImage(img)

                        # Display the image
                        image_label = tk.Label(frame, image=img_tk, bg=BG_COLOR)
                        image_label.image = img_tk  # Prevent garbage collection
                        image_label.grid(row=idx, column=1, padx=10, pady=10)
                    else:
                        # Allow for a small tolerance (±1 second difference)
                        base_timestamp = timestamp_clean[-6:]  # Get last 6 digits (for seconds)
                        possible_match = False
                        for delta in [-1, 0, 1]:  # Check for 1 second tolerance
                            candidate_timestamp = f"{int(base_timestamp) + delta:06d}"
                            candidate_filename = f"{student['Roll No']}_{today_date.replace('-', '')}{timestamp_clean[:-6]}{candidate_timestamp}.jpg"
                            candidate_path = os.path.join("TrainingImage", candidate_filename)

                            print(f"Trying candidate image: {candidate_path}")  # Debugging: Check candidate image path
                            if os.path.exists(candidate_path):
                                img = Image.open(candidate_path)
                                img = img.resize((100, 120), Image.LANCZOS)  # Resize image to fit well
                                img_tk = ImageTk.PhotoImage(img)
                                
                                # Display the image
                                image_label = tk.Label(frame, image=img_tk, bg=BG_COLOR)
                                image_label.image = img_tk  # Prevent garbage collection
                                image_label.grid(row=idx, column=1, padx=10, pady=10)
                                possible_match = True
                                break

                        if not possible_match:
                            error_label = tk.Label(frame, text="Image not found.", font=("Arial", 12), fg="red", bg=BG_COLOR)
                            error_label.grid(row=idx, column=1, padx=10, pady=10)

                except Exception as e:
                    # If image not found, display an error message
                    print(f"Error loading image: {e}")  # Debugging: Print error message
                    error_label = tk.Label(frame, text="Image not found.", font=("Arial", 12), fg="red", bg=BG_COLOR)
                    error_label.grid(row=idx, column=1, padx=10, pady=10)

            # Update scroll region after adding all the data
            frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

          else:
            print("No attendance data found.")  # Debugging: Print if no attendance data found
            messagebox.showinfo("No Attendance", "No attendance data available for today.")
       else:
        print(f"File {file_path} not found.")  # Debugging: Print if file not found
        messagebox.showerror("Error", f"Attendance file for today ({today_date}) not found!")

    # Function: Manage Students
    def manage_students():
        file_path = os.path.abspath("EmployeeDetails/EmployeeDetails.csv")
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            messagebox.showerror("Error", "No student data available!")

    # Function: Search Student Records
    def search_student_records():
        def perform_search():
            roll = roll_entry.get().strip()
            subject = subject_entry.get().strip()

            if not roll or not subject:
                messagebox.showwarning("Input Error", "Please fill in both Roll No and Subject!")
                return

            count = 0
            for filename in os.listdir("EmployeeDetails"):
                if filename.endswith(".csv"):
                    with open(os.path.join("EmployeeDetails", filename), "r") as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            if row["Roll No"] == roll and row["Subject"].lower() == subject.lower():
                                count += 1

            messagebox.showinfo("Total Attendance", 
                f"Roll No: {roll}\nSubject: {subject}\nTotal Attendance: {count}")
    
        # Popup window
        popup = tk.Toplevel()
        popup.title("Search Student Records")
        popup.geometry("400x250")
        popup.config(bg=BG_COLOR)

        tk.Label(popup, text="Enter Roll No:", font=FONT, bg=BG_COLOR).pack(pady=10)
        roll_entry = tk.Entry(popup, font=FONT)
        roll_entry.pack(pady=5)

        tk.Label(popup, text="Enter Subject:", font=FONT, bg=BG_COLOR).pack(pady=10)
        subject_entry = tk.Entry(popup, font=FONT)
        subject_entry.pack(pady=5)

        tk.Button(popup, text="Search", font=FONT, bg=BTN_COLOR, fg="white", command=perform_search).pack(pady=20)

    # Function: Hover Effect for Buttons
    def on_enter(e, button):
        button.config(bg=BTN_HOVER_COLOR)

    def on_leave(e, button):
        button.config(bg=BTN_COLOR)

    # Function to Create Button with Image
    def create_button(frame, text, command, row, col):
        try:
            img = Image.open(ICON_PATHS[text])  # Load icon
            img = img.resize((120, 120), Image.LANCZOS)  # Increased size
            img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image for {text}: {e}")
            img = None

        # Create frame for icon & button
        container = tk.Frame(frame, bg=BG_COLOR)
        container.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

        # Icon
        icon_label = tk.Label(container, image=img, bg=BG_COLOR)
        icon_label.image = img
        icon_label.pack(pady=10)

        # Button
        btn = tk.Button(container, text=text, bg=BTN_COLOR, fg="white", font=FONT,
                        width=20, height=2, relief="flat", borderwidth=3,
                        command=command, cursor="hand2")
        btn.pack(pady=5)
        btn.bind("<Enter>", lambda e: on_enter(e, btn))
        btn.bind("<Leave>", lambda e: on_leave(e, btn))

    # Create a frame for buttons & center it
    button_frame = tk.Frame(dashboard_frame, bg=BG_COLOR)
    button_frame.pack(expand=True)

    # Configure grid layout
    for i in range(3):
        button_frame.columnconfigure(i, weight=1)  
    for i in range(3):  # 3 rows now
        button_frame.rowconfigure(i, weight=1)

    # Adding Buttons
    create_button(button_frame, "View Attendance", view_attendance_report, 0, 0)
    create_button(button_frame, "Manage Students", manage_students, 0, 1)
    create_button(button_frame, "Search Student Records", search_student_records, 0, 2)
    create_button(button_frame, "Logout", lambda: show_frame(login_frame), 1, 1)
    create_button(button_frame, "Exit", parent.quit, 1, 2)

    return dashboard_frame
