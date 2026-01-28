"""
Duplicate Review UI Module

Provides manual review interface for duplicate files.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging

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
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Duplicate Review")
        self.window.geometry("1000x700")
        
        # Store PhotoImage references to prevent garbage collection
        self.source_photo = None
        self.existing_photo = None
        
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
        
        # Binary match indicator
        self.match_label = ttk.Label(list_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.match_label.pack(side=tk.BOTTOM, pady=5)
        
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
        
        # Bottom frame: action buttons
        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.skip_btn = ttk.Button(
            button_frame,
            text="Skip (Keep Both)",
            command=self._on_skip
        )
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        
        self.replace_btn = ttk.Button(
            button_frame,
            text="Replace Existing with Source",
            command=self._on_replace
        )
        self.replace_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_source_btn = ttk.Button(
            button_frame,
            text="Keep Existing, Delete Source",
            command=self._on_delete_source
        )
        self.delete_source_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        self._update_status()
    
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
            
        self._update_status()

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
        Load and display image preview.
        
        Args:
            image_path: Path to image file
            label: Label widget to display image
            path_label: Label widget to display path
            is_source: Whether this is the source image
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Resize to fit (max 400x400)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Store reference to prevent garbage collection
            if is_source:
                self.source_photo = photo
            else:
                self.existing_photo = photo
            
            # Display
            label.config(image=photo)
            path_label.config(text=image_path)
            
        except Exception as e:
            logger.error(f"Error loading preview for {image_path}: {e}")
            label.config(text=f"Error loading image:\n{e}")
            path_label.config(text=image_path)
    
    def _on_list_select(self, event):
        """Handle listbox selection."""
        selection = self.duplicate_list.curselection()
        if selection:
            self.current_index = selection[0]
            self._load_current_duplicate()
    
    def _on_skip(self):
        """Skip to next duplicate (keep both files)."""
        self.current_index += 1
        self._load_current_duplicate()
    
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
        """Delete source file, keep existing."""
        if not self.duplicates or self.current_index >= len(self.duplicates):
            return
        
        dup = self.duplicates[self.current_index]
        
        # Confirm action
        msg = f"Delete source file?\n\n{dup['source']}"
        if dup.get('is_identical'):
             msg = f"✅ Files are identical.\n\n" + msg
        else:
             msg = f"⚠️ Files are NOT identical (Binary mistmatch).\n\n" + msg
             
        result = messagebox.askyesno(
            "Confirm Delete",
            msg
        )
        
        if result:
            try:
                os.remove(dup['source'])
                logger.info(f"Deleted source file: {dup['source']}")
                
                # Remove from list
                self.duplicates.pop(self.current_index)
                self.duplicate_list.delete(self.current_index)
                
                # Load next
                self._load_current_duplicate()
                
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                messagebox.showerror("Error", f"Failed to delete file:\n{e}")
    
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
        self.skip_btn.config(state=tk.DISABLED)
        self.replace_btn.config(state=tk.DISABLED)
        self.delete_source_btn.config(state=tk.DISABLED)
        
        self._update_status()
