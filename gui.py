import tkinter as tk
from tkinter import filedialog
import pandas as pd
import pywhatkit
import pywhatkit.whats

class ExcelProcessorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Excel Processor")

        self.label = tk.Label(master, text="Select Excel File:")
        self.label.pack()

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        self.progress_label = tk.Label(master, text="")
        self.progress_label.pack()

        self.message = None
        self.success_list = []
        self.error_list = []
        self.done_interating = False

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.file_path:
            self.process_excel()

    def process_excel(self):
        self.df = pd.read_excel(self.file_path, header=1)  # Skip first row, use second row as header
        self.columns = self.df.columns.tolist()

        if "companion_phones" not in self.columns:
            self.progress_label.config(text="Error: 'companion_phones' column not found.")
        else:
            self.companion_phones = self.df["companion_phones"].tolist()
            self.clean_phones()
            self.progress_label.config(text="Excel processed successfully.")
            self.input_text_window()

    def clean_phones(self):
        cleaned_phones = []
        for number in self.companion_phones:
            numbers = str(number).split(", ")
            print(numbers)
            for n in numbers:
                cleaned_phones.append(n)
        cleaned_phones = list(set(cleaned_phones))
        for phone in cleaned_phones:
            if "+4" not in phone and phone[0:2] == "07":
                phone = f"+4{phone}"
        self.companion_phones = cleaned_phones

    def input_text_window(self):
        # Clear the initial window
        self.label.destroy()
        self.select_button.destroy()
        self.progress_label.destroy()

        # Create text entry
        self.text_label = tk.Label(self.master, text="Enter Text:")
        self.text_label.pack()

        self.text_entry = tk.Text(self.master, height=5, width=50)
        self.text_entry.pack()

        self.done_button = tk.Button(self.master, text="Done", command=lambda: self.save_text())
        self.done_button.pack()

    def save_text(self):
        self.message = self.text_entry.get("1.0", tk.END)
        self.start_iteration()

    def start_iteration(self):
        # Clear the input window
        self.text_label.destroy()
        self.text_entry.destroy()
        self.done_button.destroy()

        # Create iteration window
        self.iteration_label = tk.Label(self.master, text="")
        self.iteration_label.pack()
        
        self.error_label = tk.Label(self.master, text="")
        self.error_label.pack()

        self.current_index = 0
        self.iterate()
        
        # if self.done_interating:
        self.errors_button = tk.Button(self.master, text="Download unprocessed numbers", command=lambda: self.download_errors())
        self.errors_button.pack()
        self.ok_button = tk.Button(self.master, text="Download processed numbers", command=lambda: self.download_ok())
        self.ok_button.pack()

    def download_errors(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                for item in self.error_list:
                    file.write(item + "\n")
    
    def download_ok(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                for item in self.success_list:
                    file.write(item + "\n")

    def iterate(self):
        if self.message is not None:  # Check if text_entry is initialized
            if self.current_index < len(self.companion_phones):
                self.iteration_label.config(text=f"Processing element {self.current_index + 1} of {len(self.companion_phones)}")
                # Use self.text_entry
                print(f"Text: {self.message} - Companion Phone: {self.companion_phones[self.current_index]}")
                try:
                    self.send_whatsapp(self.companion_phones[self.current_index])
                    self.success_list.append(self.companion_phones[self.current_index])
                except Exception as e:
                    self.error_list.append(f"For phone number: {self.companion_phones[self.current_index]} got error: {e}")
                    self.error_label.config(text=f"Errors: {len(self.error_list)}")

                self.current_index += 1
                self.master.after(3000, self.iterate)
            else:
                self.iteration_label.config(text="Iteration complete.")
                self.done_interating = True

    def send_whatsapp(self, phone_number):
        print("sending")
        pywhatkit.whats.sendwhatmsg_instantly(phone_no=phone_number, message=self.message, tab_close=True, close_time=3)


def main():
    root = tk.Tk()
    root.geometry("500x200")

    app = ExcelProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
