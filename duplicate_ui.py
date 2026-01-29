"""
Duplicate Review UI Module

Provides manual review interface for duplicate files.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging
import threading

logger = logging.getLogger(__name__)


class DuplicateReviewWindow:
    """Window for manually reviewing and handling duplicate files."""
    
    def __init__(self, parent, duplicates):
        """
        Initialize duplicate review window.
        
        Args:
            parent: Parent tkinter window
            duplicates: List of duplicate dicts with 'source' and 'existing' keys
        """
        self.parent = parent
        self.duplicates = duplicates.copy()  # Work with a copy
        self.current_index = 0
        self.marked_indices = set()
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Duplicate Review")
        self.window.geometry("1000x700")
        
        self.source_photo = None
        self.existing_photo = None
        
        # UI State
        self.mark_delete_var = tk.BooleanVar(value=False)
        self.load_counter = 0
        
        self._build_ui()
        self._load_current_duplicate()
    
    def _build_ui(self):
        """Build the UI components."""
        # Top frame: duplicate list
        list_frame = ttk.LabelFrame(self.window, text="Duplicate Files", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        # Listbox with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.duplicate_list = tk.Listbox(
            list_frame,
            height=6,
            yscrollcommand=list_scroll.set
        )
        self.duplicate_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.duplicate_list.yview)
        
        self.match_label = ttk.Label(list_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.match_label.pack(side=tk.BOTTOM, pady=5)
        
        # Batch Process Button
        self.process_btn = ttk.Button(
            list_frame, 
            text="DELETE MARKED FILES NOW", 
            command=self._on_process_batch,
            state=tk.DISABLED
        )
        self.process_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Populate list
        for dup in self.duplicates:
            self.duplicate_list.insert(tk.END, os.path.basename(dup['source']))
        
        # Bind selection
        self.duplicate_list.bind('<<ListboxSelect>>', self._on_list_select)
        
        # Middle frame: image previews
        preview_frame = ttk.Frame(self.window, padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Source preview
        source_frame = ttk.LabelFrame(preview_frame, text="Source File", padding=5)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.source_label = ttk.Label(source_frame, text="", anchor=tk.CENTER)
        self.source_label.pack(fill=tk.BOTH, expand=True)
        
        self.source_path_label = ttk.Label(source_frame, text="", wraplength=400)
        self.source_path_label.pack(fill=tk.X)
        
        ttk.Button(source_frame, text="Open File", command=lambda: self._open_file(True)).pack(pady=5)
        
        # Existing preview
        existing_frame = ttk.LabelFrame(preview_frame, text="Existing File", padding=5)
        existing_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.existing_label = ttk.Label(existing_frame, text="", anchor=tk.CENTER)
        self.existing_label.pack(fill=tk.BOTH, expand=True)
        
        self.existing_path_label = ttk.Label(existing_frame, text="", wraplength=400)
        self.existing_path_label.pack(fill=tk.X)
        
        ttk.Button(existing_frame, text="Open File", command=lambda: self._open_file(False)).pack(pady=5)
        
        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Navigation
        ttk.Button(button_frame, text="< Previous", command=self._on_prev).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Next >", command=self._on_next).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Mark for deletion checkbox
        self.mark_check = ttk.Checkbutton(
            button_frame, 
            text="Mark to DELETE Source", 
            variable=self.mark_delete_var,
            command=self._on_mark_toggle
        )
        self.mark_check.pack(side=tk.LEFT, padx=10)
        
        # Replace remaining immediate action
        self.replace_btn = ttk.Button(
            button_frame,
            text="Replace Existing (Immediate)",
            command=self._on_replace
        )
        self.replace_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        self._update_status()
        
        # Bind keyboard shortcuts
        self.window.bind('<Left>', lambda e: self._on_prev())
        self.window.bind('<Right>', lambda e: self._on_next())
        self.window.bind('x', lambda e: self._on_mark_toggle())
        self.window.bind('X', lambda e: self._on_mark_toggle())  # Case insensitive
        self.window.bind('<space>', lambda e: self._on_mark_toggle()) # Space bar
        
        # Set focus to capture keys
        self.window.after(100, lambda: self.window.focus_force())
    
    def _load_current_duplicate(self):
        """Load and display current duplicate pair."""
        if not self.duplicates or self.current_index >= len(self.duplicates):
            self._show_completion()
            return
        
        dup = self.duplicates[self.current_index]
        
        # Select in listbox
        self.duplicate_list.selection_clear(0, tk.END)
        self.duplicate_list.selection_set(self.current_index)
        self.duplicate_list.see(self.current_index)
        
        # Load images
        self._load_image_preview(dup['source'], self.source_label, self.source_path_label, is_source=True)
        self._load_image_preview(dup['existing'], self.existing_label, self.existing_path_label, is_source=False)
        
        # Show binary match status
        is_identical = dup.get('is_identical')
        if is_identical is True:
            self.match_label.config(text="✅ Binary Match: YES (Files are identical)", foreground="green")
        elif is_identical is False:
            self.match_label.config(text="⚠️ Binary Match: NO (Content differs)", foreground="red")
        else:
            self.match_label.config(text="")
            
        # Update checkbox state without triggering event
        is_marked = self.current_index in self.marked_indices
        self.mark_delete_var.set(is_marked)
        
        self._update_status()

    def _on_mark_toggle(self):
        """Handle mark checkbox toggle."""
        if self.mark_delete_var.get():
            self.marked_indices.add(self.current_index)
        else:
            self.marked_indices.discard(self.current_index)
            
        self._refresh_list_item(self.current_index)
        self._update_process_btn()
        
    def _refresh_list_item(self, index):
        """Update listbox text for item."""
        if 0 <= index < len(self.duplicates):
            name = os.path.basename(self.duplicates[index]['source'])
            if index in self.marked_indices:
                name = f"[DEL] {name}"
                self.duplicate_list.itemconfig(index, foreground='red')
            else:
                self.duplicate_list.itemconfig(index, foreground='')
            
            self.duplicate_list.delete(index)
            self.duplicate_list.insert(index, name)
            
            # Reselect if needed
            if index == self.current_index:
                self.duplicate_list.selection_set(index)

    def _update_process_btn(self):
        """Update state of process button."""
        if self.marked_indices:
            self.process_btn.config(state=tk.NORMAL, text=f"DELETE {len(self.marked_indices)} MARKED FILES")
        else:
            self.process_btn.config(state=tk.DISABLED, text="DELETE MARKED FILES NOW")

    def _on_prev(self):
        """Go to previous item."""
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current_duplicate()
            
    def _on_next(self):
        """Go to next item."""
        if self.current_index < len(self.duplicates) - 1:
            self.current_index += 1
            self._load_current_duplicate()

    def _on_process_batch(self):
        """Process deletion of all marked files."""
        if not self.marked_indices:
            return
            
        count = len(self.marked_indices)
        if not messagebox.askyesno("Confirm Batch Delete", f"Are you sure you want to delete {count} source files?"):
            return
            
        deleted_count = 0
        # Sort indices in reverse order to remove safely
        for index in sorted(list(self.marked_indices), reverse=True):
            dup = self.duplicates[index]
            try:
                os.remove(dup['source'])
                logger.info(f"Deleted source file: {dup['source']}")
                
                # Remove from duplicates list
                self.duplicates.pop(index)
                self.duplicate_list.delete(index)
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Error deleting {dup['source']}: {e}")
        
        # Clear marks
        self.marked_indices.clear()
        
        messagebox.showinfo("Complete", f"Deleted {deleted_count} files.")
        
        # Reset view
        self.current_index = 0
        if self.duplicates:
            self._load_current_duplicate()
        else:
            self._show_completion()
        self._update_process_btn()

    def _open_file(self, is_source):
        """Open file in default viewer."""
        if not self.duplicates or self.current_index >= len(self.duplicates):
            return
            
        dup = self.duplicates[self.current_index]
        path = dup['source'] if is_source else dup['existing']
        
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def _load_image_preview(self, image_path, label, path_label, is_source=True):
        """
        Load and display image preview asynchronously.
        """
        # Update path immediately
        path_label.config(text=image_path)
        label.config(image='', text="Loading...")
        
        # Increment counter to invalidate previous requests for this slot
        # We need separate counters for source/existing or just one global? 
        # Simpler: pass current counter value to thread
        self.load_counter += 1
        # Capture current index to validate later
        target_index = self.current_index
        
        thread = threading.Thread(
            target=self._load_image_thread,
            args=(image_path, label, is_source, target_index),
            daemon=True
        )
        thread.start()

    def _load_image_thread(self, image_path, label, is_source, target_index):
        """Background thread for loading image."""
        try:
            # Check if video (simple extension check)
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.mp4', '.mov', '.avi', '.mkv', '.m4v']:
                # Is video, show placeholder
                self.window.after(0, lambda: label.config(image='', text="[Video File]\nNo Preview Available\nUse 'Open File' to view"))
                return

            # Perform heavy lifting
            img = Image.open(image_path)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Update UI on main thread
            self.window.after(0, lambda: self._update_image_ui(label, photo, is_source, target_index))
            
        except Exception as e:
            logger.error(f"Error loading preview for {image_path}: {e}")
            msg = f"Error loading image:\n{e}"
            self.window.after(0, lambda: label.config(text=msg))

    def _update_image_ui(self, label, photo, is_source, target_index):
        """Update UI with loaded image if we are still on the same item."""
        if target_index != self.current_index:
            return 
            
        try:
            # Store reference
            if is_source:
                self.source_photo = photo
            else:
                self.existing_photo = photo
                
            label.config(image=photo, text="")
        except Exception as e:
            logger.error(f"Error updating UI: {e}") 

    
    def _on_list_select(self, event):
        """Handle listbox selection."""
        selection = self.duplicate_list.curselection()
        if selection:
            self.current_index = selection[0]
            self._load_current_duplicate()
    
    def _on_skip(self):
        """Skip to next duplicate (keep both files)."""
        self._on_next()
    
    def _on_replace(self):
        """Replace existing file with source."""
        if not self.duplicates or self.current_index >= len(self.duplicates):
            return
        
        dup = self.duplicates[self.current_index]
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Replace",
            f"Replace existing file with source?\n\nExisting: {dup['existing']}\nSource: {dup['source']}"
        )
        
        if result:
            try:
                import shutil
                # Replace file
                shutil.copy2(dup['source'], dup['existing'])
                logger.info(f"Replaced {dup['existing']} with {dup['source']}")
                
                # Remove from list
                self.duplicates.pop(self.current_index)
                self.duplicate_list.delete(self.current_index)
                
                # Load next
                self._load_current_duplicate()
                
            except Exception as e:
                logger.error(f"Error replacing file: {e}")
                messagebox.showerror("Error", f"Failed to replace file:\n{e}")
    
    
    def _on_delete_source(self):
        """
        Delete source file (Legacy single action, kept for compatibility if needed).
        Currently replaced by batch delete, but keeping just in case.
        """
        self._on_mark_toggle() # Just mark it instead of deleting immediately?
        # Better: Reuse the logic but confirm immediately?
        # No, user wants batch. This button was removed from UI anyway.
        pass
    
    def _update_status(self):
        """Update status label."""
        if self.duplicates:
            self.status_label.config(
                text=f"Duplicate {self.current_index + 1} of {len(self.duplicates)}"
            )
        else:
            self.status_label.config(text="No duplicates remaining")
    
    def _show_completion(self):
        """Show completion message."""
        self.source_label.config(image='', text="All duplicates reviewed!")
        self.existing_label.config(image='', text="")
        self.source_path_label.config(text="")
        self.existing_path_label.config(text="")
        
        # Disable buttons
        # Disable buttons
        self.replace_btn.config(state=tk.DISABLED)
        self.mark_check.config(state=tk.DISABLED)
        
        self._update_status()
