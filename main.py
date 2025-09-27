import os
import shutil
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

class FontManagerApp:
    """
    A GUI application to replace fonts or undo replacements, featuring a mode-based UI
    and intelligent folder selection.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Font Manager")
        self.root.geometry("600x500")
        self.root.resizable(False, True)

        self.source_file_path_var = tk.StringVar()
        self.target_folder_path_var = tk.StringVar()
        self.selected_backup_var = tk.StringVar()
        
        self.source_folder_name = "PLACE YOUR CUSTOM FONT HERE"
        self.script_dir = self._get_script_directory()
        if not self.script_dir:
            messagebox.showerror("Critical Error", "Could not determine the script's directory.")
            root.destroy()
            return
        self.source_folder_path = os.path.join(self.script_dir, self.source_folder_name)
        
        self.last_source_status = None
        self.current_source_file = None


        self._setup_gui()
        

        self.monitor_source_folder()
        self.show_frame(self.main_menu_frame)

    def _setup_gui(self):
        """Creates and arranges all the GUI widgets and frames."""

        container = ttk.Frame(self.root, padding=15)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.main_menu_frame = ttk.Frame(container)
        self.replace_frame = ttk.Frame(container)
        self.undo_frame = ttk.Frame(container)

        for frame in (self.main_menu_frame, self.replace_frame, self.undo_frame):
            frame.grid(row=0, column=0, sticky='nsew')


        self._create_main_menu_frame()
        self._create_replace_frame()
        self._create_undo_frame()


        log_frame = ttk.LabelFrame(self.root, text="Log", padding=(10, 5))
        log_frame.pack(side="bottom", fill="x", expand=False, padx=15, pady=(0, 15))
        self.log_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=8)
        self.log_widget.pack(fill="x", expand=True)
        
        style = ttk.Style(self.root)
        style.configure('Accent.TButton', foreground='Green', background='#4CAF50')

    def show_frame(self, frame_to_show):
        """Raises the selected frame to the top."""
        frame_to_show.tkraise()

    def _create_main_menu_frame(self):
        """Creates the initial screen with task choices."""
        frame = self.main_menu_frame
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure((0, 1, 2), weight=1)
        
        ttk.Label(frame, text="What would you like to do?", font=("Helvetica", 14)).pack(pady=20)
        
        replace_btn = ttk.Button(frame, text="Replace Fonts", style='Accent.TButton', command=lambda: self.show_frame(self.replace_frame))
        replace_btn.pack(fill='x', ipady=10, pady=5, padx=50)

        undo_btn = ttk.Button(frame, text="Undo / Restore from Backup", command=lambda: self.show_frame(self.undo_frame))
        undo_btn.pack(fill='x', ipady=10, pady=5, padx=50)

    def _create_replace_frame(self):
        """Creates the UI for the 'Replace Fonts' task."""
        frame = self.replace_frame
        
        ttk.Label(frame, text="Replace Fonts", font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
        
        source_frame = ttk.LabelFrame(frame, text="1. Source Font File", padding=10)
        source_frame.pack(fill='x', pady=5)
        ttk.Entry(source_frame, textvariable=self.source_file_path_var, state='readonly').pack(fill='x')

        target_frame = ttk.LabelFrame(frame, text="2. Select Target Folder", padding=10)
        target_frame.pack(fill='x', pady=5)
        target_entry = ttk.Entry(target_frame, textvariable=self.target_folder_path_var, state='readonly')
        target_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(target_frame, text="Browse...", command=self.select_target_folder).pack(side='right', padx=(5,0))

        ttk.Button(frame, text="Perform Replacement", style='Accent.TButton', command=self.run_replacement_process).pack(fill='x', ipady=8, pady=10)
        ttk.Button(frame, text="« Back to Menu", command=lambda: self.show_frame(self.main_menu_frame)).pack(fill='x', ipady=2)

    def _create_undo_frame(self):
        """Creates the UI for the 'Undo / Restore' task."""
        frame = self.undo_frame
        
        ttk.Label(frame, text="Undo / Restore", font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
        
        target_frame = ttk.LabelFrame(frame, text="1. Select Target Folder to Scan", padding=10)
        target_frame.pack(fill='x', pady=5)
        target_entry = ttk.Entry(target_frame, textvariable=self.target_folder_path_var, state='readonly')
        target_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(target_frame, text="Browse & Scan...", command=self.select_target_folder).pack(side='right', padx=(5,0))

        backup_frame = ttk.LabelFrame(frame, text="2. Choose Backup to Restore", padding=10)
        backup_frame.pack(fill='x', pady=5)
        self.backup_menu = ttk.OptionMenu(backup_frame, self.selected_backup_var, "No Target Selected")
        self.backup_menu.pack(fill='x')
        self.backup_menu.config(state='disabled')

        self.undo_button = ttk.Button(frame, text="Restore This Backup", command=self.run_undo_process)
        self.undo_button.pack(fill='x', ipady=8, pady=10)
        self.undo_button.config(state='disabled')
        ttk.Button(frame, text="« Back to Menu", command=lambda: self.show_frame(self.main_menu_frame)).pack(fill='x', ipady=2)
    
    def log(self, message):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')
        self.root.update_idletasks()

    def _get_script_directory(self):
        try: return os.path.dirname(os.path.abspath(__file__))
        except NameError: return os.path.dirname(os.path.abspath(sys.argv[0]))

    def monitor_source_folder(self):

        if not os.path.isdir(self.source_folder_path):
            try:
                os.makedirs(self.source_folder_path)
                self.log(f"Source folder created at: {self.source_folder_path}")
            except Exception as e:
                self.source_file_path_var.set(f"CRITICAL: Failed to create source folder.")
                return
        try: source_files = [f for f in os.listdir(self.source_folder_path) if os.path.isfile(os.path.join(self.source_folder_path, f))]
        except Exception:
            self.source_file_path_var.set("CRITICAL: Cannot access source folder.")
            return

        status = ""
        if len(source_files) == 0: status, self.current_source_file, msg = "waiting", None, "Waiting for a font file..."
        elif len(source_files) > 1: status, self.current_source_file, msg = "multiple_files", None, "ERROR: Too many files found."
        else:
            self.current_source_file = os.path.join(self.source_folder_path, source_files[0])
            status, msg = f"ok:{self.current_source_file}", self.current_source_file
        
        self.source_file_path_var.set(msg)

        if status != self.last_source_status:
            if status == "waiting": self.log("Source folder is empty. Waiting...")
            elif status == "multiple_files": self.log("ERROR: Multiple files detected in source folder.")
            elif status.startswith("ok:"): self.log(f"Source font detected: {os.path.basename(self.current_source_file)}")
            self.last_source_status = status
        self.root.after(5000, self.monitor_source_folder)

    def select_target_folder(self):
        """Opens a dialog to select the target directory and auto-corrects if 'Fonts.old' is chosen."""
        folder_selected = filedialog.askdirectory(title="Select the folder")
        
        if folder_selected:

            if os.path.basename(folder_selected) == "Fonts.old":
                self.log("💡 'Fonts.old' was selected. Auto-correcting to the parent folder.")
                folder_selected = os.path.dirname(folder_selected)

            self.target_folder_path_var.set(folder_selected)
            self.log(f"Target folder set to: {folder_selected}")
            self.scan_for_backups()

    def scan_for_backups(self):

        self.backup_menu.config(state='disabled')
        self.undo_button.config(state='disabled')
        self.selected_backup_var.set("No backups found")
        
        base_backup_dir = os.path.join(self.target_folder_path_var.get(), "Fonts.old")
        if os.path.isdir(base_backup_dir):
            try:
                backups = sorted([d for d in os.listdir(base_backup_dir) if os.path.isdir(os.path.join(base_backup_dir, d))], reverse=True)
                if backups:
                    menu = self.backup_menu["menu"]
                    menu.delete(0, "end")
                    for backup in backups:
                        menu.add_command(label=backup, command=lambda v=backup: self.selected_backup_var.set(v))
                    self.selected_backup_var.set(backups[0])
                    self.backup_menu.config(state='normal')
                    self.undo_button.config(state='normal')
                    self.log(f"Found {len(backups)} backup session(s).")
                    return
            except Exception as e: self.log(f"Error scanning backups: {e}")
        self.log("No valid backups found in 'Fonts.old' folder.")

    def run_replacement_process(self):

        if not self.current_source_file: messagebox.showerror("Error", "Source font is not ready."); return
        target_folder = self.target_folder_path_var.get()
        if not target_folder or not os.path.isdir(target_folder): messagebox.showerror("Error", "Please select a valid target folder first."); return
        if not messagebox.askyesno("Confirmation", f"This will replace all fonts in:\n'{target_folder}'\n\nwith:\n'{os.path.basename(self.current_source_file)}'\n\nA new backup will be created. Proceed?"): self.log("Replacement cancelled."); return
        
        self.log("\n--- Starting replacement ---")
        try:
            backup_folder_path = os.path.join(target_folder, "Fonts.old", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            os.makedirs(backup_folder_path, exist_ok=True)
            self.log(f"Creating backup: {os.path.basename(backup_folder_path)}")
            font_ext = ('.ttf', '.otf', '.woff', '.woff2', '.eot')
            replaced_count = 0
            for filename in os.listdir(target_folder):
                if os.path.isfile(os.path.join(target_folder, filename)) and filename.lower().endswith(font_ext):
                    shutil.move(os.path.join(target_folder, filename), os.path.join(backup_folder_path, filename))
                    shutil.copy2(self.current_source_file, os.path.join(target_folder, filename))
                    replaced_count += 1
            self.log(f"Successfully replaced {replaced_count} file(s).")
            messagebox.showinfo("Success", f"Process finished! Replaced {replaced_count} file(s).")
            self.scan_for_backups()
        except Exception as e: messagebox.showerror("Error", f"Replacement failed: {e}"); self.log(f"ERROR: {e}")

    def run_undo_process(self):
        target_folder, selected_backup = self.target_folder_path_var.get(), self.selected_backup_var.get()
        if not target_folder or selected_backup in ["No Target Selected", "No backups found"]: messagebox.showerror("Error", "Select a valid target and backup session."); return
        backup_path = os.path.join(target_folder, "Fonts.old", selected_backup)
        if not os.path.isdir(backup_path): messagebox.showerror("Error", f"Backup folder not found:\n{backup_path}"); return
        if not messagebox.askyesno("Confirmation", f"This will restore files from:\n'{selected_backup}'\n\nThis will overwrite current fonts. Proceed?"): self.log("Undo cancelled."); return
        
        self.log(f"\n--- Starting Undo from '{selected_backup}' ---")
        try:
            files_to_restore = [f for f in os.listdir(backup_path) if os.path.isfile(os.path.join(backup_path, f))]
            if not files_to_restore: messagebox.showinfo("Information", "Backup folder is empty."); self.log("Backup is empty."); return
            
            for filename in files_to_restore: shutil.move(os.path.join(backup_path, filename), os.path.join(target_folder, filename))
            self.log(f"Restored {len(files_to_restore)} file(s).")
            messagebox.showinfo("Success", f"Successfully restored {len(files_to_restore)} file(s).")
            
            if messagebox.askyesno("Cleanup", f"Remove the now-empty backup folder '{selected_backup}'?"):
                os.rmdir(backup_path); self.log(f"Removed empty backup: {selected_backup}")
            self.scan_for_backups()
        except Exception as e: messagebox.showerror("Error", f"Undo failed: {e}"); self.log(f"ERROR: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FontManagerApp(root)
    root.mainloop()
