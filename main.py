"""
Media Organization Tool - Main GUI

A lightweight tool for organizing images and videos by date.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
from datetime import datetime

from utils import setup_logging
from copier import process_media
from duplicate_ui import DuplicateReviewWindow

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window."""
    
    def __init__(self, root):
        """
        Initialize main window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Media Organization Tool")
        self.root.geometry("700x600")
        
        # Set icon
        icon_path = self.resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Could not load window icon: {e}")
        
        # State
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.move_files = tk.BooleanVar(value=False)
        self.is_processing = False
        self.progress_queue = queue.Queue()
        self.current_log_dir = None
        
        # Results
        self.results = None
        
        self._build_ui()
        self._start_queue_monitor()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    
    def _build_ui(self):
        """Build the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source folder selection
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="Source Folder:", width=15).pack(side=tk.LEFT)
        ttk.Entry(source_frame, textvariable=self.source_folder).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        ttk.Button(source_frame, text="Browse", command=self._browse_source).pack(side=tk.LEFT)
        
        # Destination folder selection
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="Destination Folder:", width=15).pack(side=tk.LEFT)
        ttk.Entry(dest_frame, textvariable=self.dest_folder).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        ttk.Button(dest_frame, text="Browse", command=self._browse_dest).pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            options_frame,
            text="Move files instead of copying (delete source after processing)",
            variable=self.move_files
        ).pack(side=tk.LEFT, padx=5)
        
        # Start button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="Start Processing",
            command=self._start_processing
        )
        self.start_btn.pack()
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(fill=tk.X)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_source(self):
        """Browse for source folder."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
    
    def _browse_dest(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
    
    def _start_processing(self):
        """Start processing images."""
        # Validate inputs
        source = self.source_folder.get()
        dest = self.dest_folder.get()
        
        if not source or not os.path.isdir(source):
            messagebox.showerror("Error", "Please select a valid source folder")
            return
        
        if not dest:
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing already in progress")
            return
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_bar['value'] = 0
        
        # Disable start button
        self.start_btn.config(state=tk.DISABLED)
        self.is_processing = True
        
        # Start worker thread
        move = self.move_files.get()
        
        # Create session log directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_base = os.path.join(os.path.dirname(__file__), 'logs')
        self.current_log_dir = os.path.join(logs_base, timestamp)
        os.makedirs(self.current_log_dir, exist_ok=True)
        
        # Add a file handler for the session log
        session_log_file = os.path.join(self.current_log_dir, "session.log")
        self.session_handler = logging.FileHandler(session_log_file, encoding='utf-8')
        self.session_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.session_handler)
        
        self._log(f"Session logs will be saved to: {self.current_log_dir}")
        
        thread = threading.Thread(
            target=self._worker_thread,
            args=(source, dest, move, self.current_log_dir),
            daemon=True
        )
        thread.start()
        
        mode = "Moving" if move else "Copying"
        self._log(f"Processing started ({mode})...")
    
    def _worker_thread(self, source_folder, dest_folder, move_files, log_dir):
        """
        Background worker thread for processing.
        
        Args:
            source_folder: Source directory
            dest_folder: Destination directory
            move_files: Whether to move instead of copy
            log_dir: Directory to save logs
        """
        try:
            # Process media files (images and videos)
            results = process_media(
                source_folder,
                dest_folder,
                move_files=move_files,
                log_dir=log_dir,
                progress_callback=self._progress_callback
            )
            
            # Store results
            self.results = results
            
            # Signal completion
            self.progress_queue.put(('complete', results))
            
        except Exception as e:
            logger.error(f"Error in worker thread: {e}")
            self.progress_queue.put(('error', str(e)))
    
    def _progress_callback(self, current, total, status):
        """
        Progress callback from worker thread.
        
        Args:
            current: Current item number
            total: Total items
            status: Status message
        """
        self.progress_queue.put(('progress', (current, total, status)))
    
    def _start_queue_monitor(self):
        """Start monitoring the progress queue."""
        self._check_queue()
    
    def _check_queue(self):
        """Check progress queue for updates."""
        try:
            while True:
                msg_type, data = self.progress_queue.get_nowait()
                
                if msg_type == 'progress':
                    current, total, status = data
                    # Update progress bar
                    if total > 0:
                        percent = (current / total) * 100
                        self.progress_bar['value'] = percent
                    # Update status
                    self.status_label.config(text=status)
                    
                elif msg_type == 'complete':
                    self._on_processing_complete(data)
                    
                elif msg_type == 'error':
                    self._on_processing_error(data)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._check_queue)
    
    def _on_processing_complete(self, results):
        """
        Handle processing completion.
        
        Args:
            results: Results dict from process_media
        """
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 100
        
        # Remove session handler
        if hasattr(self, 'session_handler') and self.session_handler:
            logging.getLogger().removeHandler(self.session_handler)
            self.session_handler.close()
            self.session_handler = None
        
        # Log summary
        self._log(f"\n{'='*50}")
        self._log("Processing Complete!")
        self._log(f"{'='*50}")
        action = "moved" if self.move_files.get() else "copied"
        image_count = results.get('image_count', 0)
        video_count = results.get('video_count', 0)
        self._log(f"Successfully {action}: {results['success_count']} files")
        self._log(f"  - Images: {image_count}, Videos: {video_count}")
        self._log(f"Duplicates found: {results['duplicate_count']} files")
        self._log(f"Invalid files (skipped): {results['invalid_count']} files")
        self._log(f"Errors: {results['error_count']} files")
        
        # Log invalid files info
        if results['invalid_count'] > 0 and results.get('invalid_log_path'):
            self._log(f"\nInvalid files log: {results['invalid_log_path']}")
        
        # Log success report info
        if results['success_count'] > 0 and results.get('success_log_path'):
            self._log(f"Success report: {results['success_log_path']}")
        
        # Generate duplicate report
        duplicate_report_path = None
        if results['duplicates']:
            duplicate_report_path = self._generate_duplicate_report(results['duplicates'], self.current_log_dir)
            if duplicate_report_path:
                self._log(f"Duplicate report: {duplicate_report_path}")
            
            # Ask to open duplicate review
            response = messagebox.askyesno(
                "Duplicates Found",
                f"Found {results['duplicate_count']} duplicate files.\n\n"
                "Would you like to review them now?"
            )
            
            if response:
                self._open_duplicate_review(results['duplicates'])
        
        # Log errors if any
        if results['errors']:
            self._log(f"\n{'='*50}")
            self._log("Errors:")
            self._log(f"{'='*50}")
            for error in results['errors'][:10]:  # Show first 10
                self._log(f"  {error['source']}: {error['error']}")
            if len(results['errors']) > 10:
                self._log(f"  ... and {len(results['errors']) - 10} more errors")
        
        self.status_label.config(text="Processing complete")
        
        label = "Moved" if self.move_files.get() else "Copied"
        image_count = results.get('image_count', 0)
        video_count = results.get('video_count', 0)
        messagebox.showinfo(
            "Complete",
            f"Processing complete!\n\n"
            f"{label}: {results['success_count']}\n"
            f"  (Images: {image_count}, Videos: {video_count})\n"
            f"Duplicates: {results['duplicate_count']}\n"
            f"Invalid files: {results['invalid_count']}\n"
            f"Errors: {results['error_count']}"
        )
    
    def _on_processing_error(self, error_msg):
        """
        Handle processing error.
        
        Args:
            error_msg: Error message
        """
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Error occurred")
        
        # Remove session handler
        if hasattr(self, 'session_handler') and self.session_handler:
            logging.getLogger().removeHandler(self.session_handler)
            self.session_handler.close()
            self.session_handler = None
        
        self._log(f"\nERROR: {error_msg}")
        
        messagebox.showerror("Error", f"Processing failed:\n{error_msg}")
    
    def _generate_duplicate_report(self, duplicates, log_dir):
        """
        Generate duplicate report file.
        
        Args:
            duplicates: List of duplicate dicts
            log_dir: Directory to save the report (optional)
            
        Returns:
            str: Path to the created report file
        """
        try:
            if log_dir:
                # Use provided session directory
                report_path = os.path.join(log_dir, 'duplicate_report.txt')
            else:
                # Fallback to old behavior (shouldn't happen with new logic but good for safety)
                logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
                os.makedirs(logs_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = os.path.join(logs_dir, f"duplicate_report_{timestamp}.txt")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Duplicate Report - Generated {datetime.now()}\n")
                f.write(f"{'='*80}\n\n")
                
                for dup in duplicates:
                    f.write(f"{dup['source']}  -->  {dup['existing']}\n")
            
            logger.info(f"Duplicate report saved to: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating duplicate report: {e}")
            return None

    
    def _open_duplicate_review(self, duplicates):
        """
        Open duplicate review window.
        
        Args:
            duplicates: List of duplicate dicts
        """
        try:
            DuplicateReviewWindow(self.root, duplicates)
        except Exception as e:
            logger.error(f"Error opening duplicate review: {e}")
            messagebox.showerror("Error", f"Failed to open duplicate review:\n{e}")
    
    def _log(self, message):
        """
        Add message to log.
        
        Args:
            message: Message to log
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


def main():
    """Main entry point."""
    # Setup logging
    setup_logging()
    
    logger.info("Starting Media Organization Tool")
    
    # Create GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
