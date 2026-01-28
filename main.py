"""
Image Organization Tool - Main GUI

A lightweight tool for organizing images by EXIF date.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
from datetime import datetime

from utils import setup_logging
from copier import process_images
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
        self.root.title("Image Organization Tool")
        self.root.geometry("700x600")
        
        # State
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.is_processing = False
        self.progress_queue = queue.Queue()
        
        # Results
        self.results = None
        
        self._build_ui()
        self._start_queue_monitor()
    
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
        thread = threading.Thread(
            target=self._worker_thread,
            args=(source, dest),
            daemon=True
        )
        thread.start()
        
        self._log("Processing started...")
    
    def _worker_thread(self, source_folder, dest_folder):
        """
        Background worker thread for processing.
        
        Args:
            source_folder: Source directory
            dest_folder: Destination directory
        """
        try:
            # Process images
            results = process_images(
                source_folder,
                dest_folder,
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
            results: Results dict from process_images
        """
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 100
        
        # Log summary
        self._log(f"\n{'='*50}")
        self._log("Processing Complete!")
        self._log(f"{'='*50}")
        self._log(f"Successfully copied: {results['success_count']} files")
        self._log(f"Duplicates found: {results['duplicate_count']} files")
        self._log(f"Invalid images (skipped): {results['invalid_count']} files")
        self._log(f"Errors: {results['error_count']} files")
        
        # Log invalid images info
        if results['invalid_count'] > 0 and results.get('invalid_log_path'):
            self._log(f"\nInvalid images log: {results['invalid_log_path']}")
        
        # Log success report info
        if results['success_count'] > 0 and results.get('success_log_path'):
            self._log(f"Success report: {results['success_log_path']}")
        
        # Generate duplicate report
        duplicate_report_path = None
        if results['duplicates']:
            duplicate_report_path = self._generate_duplicate_report(results['duplicates'])
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
        
        messagebox.showinfo(
            "Complete",
            f"Processing complete!\n\n"
            f"Copied: {results['success_count']}\n"
            f"Duplicates: {results['duplicate_count']}\n"
            f"Invalid images: {results['invalid_count']}\n"
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
        
        self._log(f"\nERROR: {error_msg}")
        
        messagebox.showerror("Error", f"Processing failed:\n{error_msg}")
    
    def _generate_duplicate_report(self, duplicates):
        """
        Generate duplicate report file.
        
        Args:
            duplicates: List of duplicate dicts
            
        Returns:
            str: Path to the created report file
        """
        try:
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"duplicate_report_{timestamp}.txt"
            report_path = os.path.join(logs_dir, report_filename)
            
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
    
    logger.info("Starting Image Organization Tool")
    
    # Create GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
