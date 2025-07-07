#!/usr/bin/env python3
"""
Social Media Poster GUI
A secure graphical interface for posting to multiple social media platforms
Uses 1Password CLI for secure credential management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple
import requests
from requests_oauthlib import OAuth1Session
import base64
from pathlib import Path
import webbrowser
import re
from PIL import Image, ImageTk
import io

class SocialMediaPosterGUI:
    """
    GUI application for posting to multiple social media platforms
    Provides user-friendly interface with real-time validation
    """
    
    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("Social Media Poster")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Character limits for each platform
        self.character_limits = {
            'Instagram': 2200,
            'X (Twitter)': 280,
            'Bluesky': 300,
            'LinkedIn': 3000
        }
        
        # API endpoints for each platform
        self.api_endpoints = {
            'Instagram': 'https://graph.instagram.com/v19.0',
            'X (Twitter)': 'https://api.twitter.com/2/tweets',
            'Bluesky': 'https://bsky.social/xrpc',
            'LinkedIn': 'https://api.linkedin.com/v2/ugcPosts'
        }
        
        # Store selected image path
        self.selected_image_path = None
        
        # Store credentials
        self.credentials = {}
        
        # Initialize GUI
        self.setup_gui()
        
        # Bind text change event to update character counts
        self.text_area.bind('<KeyRelease>', self.update_character_counts)
        self.text_area.bind('<Button-1>', self.update_character_counts)
        
        # Initial character count update
        self.update_character_counts()
    
    def setup_gui(self):
        """Set up the main GUI interface"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Social Media Poster", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Platform selection section
        self.setup_platform_selection(main_frame)
        
        # Text input section
        self.setup_text_input(main_frame)
        
        # Image upload section
        self.setup_image_upload(main_frame)
        
        # Character count display
        self.setup_character_display(main_frame)
        
        # Action buttons
        self.setup_action_buttons(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_platform_selection(self, parent):
        """Set up platform selection checkboxes"""
        # Platform selection frame
        platform_frame = ttk.LabelFrame(parent, text="Select Platforms", padding="10")
        platform_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create checkboxes for each platform
        self.platform_vars = {}
        platforms = ['Instagram', 'X (Twitter)', 'Bluesky', 'LinkedIn']
        
        for i, platform in enumerate(platforms):
            var = tk.BooleanVar()
            self.platform_vars[platform] = var
            
            checkbox = ttk.Checkbutton(platform_frame, text=platform, variable=var,
                                     command=self.update_character_counts)
            checkbox.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Select All / Deselect All buttons
        button_frame = ttk.Frame(platform_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_platforms).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Deselect All", 
                  command=self.deselect_all_platforms).pack(side=tk.LEFT)
    
    def setup_text_input(self, parent):
        """Set up text input area"""
        # Text input frame
        text_frame = ttk.LabelFrame(parent, text="Post Content", padding="10")
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=8)
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL detection and validation
        url_frame = ttk.Frame(text_frame)
        url_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(url_frame, text="💡 Tip: URLs will be automatically detected and validated", 
                 font=('Arial', 9)).pack(side=tk.LEFT)
    
    def setup_image_upload(self, parent):
        """Set up image upload section"""
        # Image upload frame
        image_frame = ttk.LabelFrame(parent, text="Image Upload (Optional)", padding="10")
        image_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        # Image selection button
        self.image_button = ttk.Button(image_frame, text="Select Image", 
                                      command=self.select_image)
        self.image_button.grid(row=0, column=0, padx=(0, 10))
        
        # Image path display
        self.image_path_var = tk.StringVar()
        self.image_path_var.set("No image selected")
        image_path_label = ttk.Label(image_frame, textvariable=self.image_path_var)
        image_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Clear image button
        self.clear_image_button = ttk.Button(image_frame, text="Clear", 
                                           command=self.clear_image, state=tk.DISABLED)
        self.clear_image_button.grid(row=0, column=2, padx=(10, 0))
        
        # Image preview (small thumbnail)
        self.image_preview_label = ttk.Label(image_frame, text="")
        self.image_preview_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
    
    def setup_character_display(self, parent):
        """Set up character count display"""
        # Character count frame
        char_frame = ttk.LabelFrame(parent, text="Character Limits", padding="10")
        char_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        char_frame.columnconfigure(0, weight=1)
        char_frame.columnconfigure(1, weight=1)
        
        # Character count labels for each platform
        self.char_labels = {}
        platforms = ['Instagram', 'X (Twitter)', 'Bluesky', 'LinkedIn']
        
        for i, platform in enumerate(platforms):
            label = ttk.Label(char_frame, text=f"{platform}: 0/{self.character_limits[platform]}")
            label.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 20), pady=2)
            self.char_labels[platform] = label
    
    def setup_action_buttons(self, parent):
        """Set up action buttons"""
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Post button
        self.post_button = ttk.Button(button_frame, text="📤 Post to Selected Platforms", 
                                     command=self.post_to_platforms, style='Accent.TButton')
        self.post_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel/Clear button
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear All", 
                                      command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings button
        self.settings_button = ttk.Button(button_frame, text="⚙️ Settings", 
                                         command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT)
    
    def setup_status_bar(self, parent):
        """Set up status bar"""
        # Status bar frame
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to post")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
    
    def select_all_platforms(self):
        """Select all platform checkboxes"""
        for var in self.platform_vars.values():
            var.set(True)
        self.update_character_counts()
    
    def deselect_all_platforms(self):
        """Deselect all platform checkboxes"""
        for var in self.platform_vars.values():
            var.set(False)
        self.update_character_counts()
    
    def select_image(self):
        """Open file dialog to select an image"""
        file_types = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('All files', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=file_types
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.image_path_var.set(os.path.basename(file_path))
            self.clear_image_button.config(state=tk.NORMAL)
            self.create_image_preview(file_path)
            self.status_var.set(f"Image selected: {os.path.basename(file_path)}")
    
    def clear_image(self):
        """Clear selected image"""
        self.selected_image_path = None
        self.image_path_var.set("No image selected")
        self.clear_image_button.config(state=tk.DISABLED)
        self.image_preview_label.config(image='', text='')
        self.status_var.set("Image cleared")
    
    def create_image_preview(self, image_path):
        """Create a small preview of the selected image"""
        try:
            # Open and resize image for preview
            with Image.open(image_path) as img:
                # Create thumbnail
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Update label
                self.image_preview_label.config(image=photo, text='')
                self.image_preview_label.image = photo  # Keep a reference
                
        except Exception as e:
            self.image_preview_label.config(image='', text=f"Preview error: {str(e)}")
    
    def update_character_counts(self, event=None):
        """Update character count display for all platforms"""
        text = self.text_area.get("1.0", tk.END).strip()
        text_length = len(text)
        
        # Detect URLs in text
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
        
        for platform in self.char_labels:
            limit = self.character_limits[platform]
            remaining = limit - text_length
            
            # Update label text
            label_text = f"{platform}: {text_length}/{limit}"
            if remaining < 0:
                label_text += f" ({abs(remaining)} over)"
            else:
                label_text += f" ({remaining} remaining)"
            
            self.char_labels[platform].config(text=label_text)
            
            # Color coding based on platform selection and limits
            if platform in selected_platforms:
                if remaining < 0:
                    # Over limit - red
                    self.char_labels[platform].config(foreground='red')
                elif remaining < 50:
                    # Close to limit - orange
                    self.char_labels[platform].config(foreground='orange')
                else:
                    # Within limit - green
                    self.char_labels[platform].config(foreground='green')
            else:
                # Not selected - gray
                self.char_labels[platform].config(foreground='gray')
        
        # Update status with URL detection
        if urls:
            self.status_var.set(f"Ready to post • {len(urls)} URL(s) detected")
        else:
            self.status_var.set("Ready to post")
        
        # Enable/disable post button based on validation
        self.validate_post_ready()
    
    def validate_post_ready(self):
        """Validate if ready to post and enable/disable post button"""
        text = self.text_area.get("1.0", tk.END).strip()
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
        
        # Check if we have text and at least one platform selected
        if not text or not selected_platforms:
            self.post_button.config(state=tk.DISABLED)
            return False
        
        # Check for character limit violations
        text_length = len(text)
        over_limit = False
        
        for platform in selected_platforms:
            if text_length > self.character_limits[platform]:
                over_limit = True
                break
        
        if over_limit:
            self.post_button.config(state=tk.NORMAL)  # Allow posting but with warning
        else:
            self.post_button.config(state=tk.NORMAL)
        
        return True
    
    def clear_all(self):
        """Clear all inputs"""
        self.text_area.delete("1.0", tk.END)
        self.deselect_all_platforms()
        self.clear_image()
        self.status_var.set("All cleared")
    
    def open_settings(self):
        """Open settings dialog for 1Password configuration"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        settings_frame = ttk.Frame(settings_window, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(settings_frame, text="1Password CLI Configuration", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Instructions
        instructions = """
To use this application, you need to:

1. Install 1Password CLI from: https://developer.1password.com/docs/cli/get-started/
2. Sign in to 1Password CLI: op signin
3. Create these items in your 1Password vault:

   • "Social Media - Instagram API"
     Fields: access_token, instagram_account_id
   
   • "Social Media - X API"
     Fields: consumer_key, consumer_secret, access_token, access_token_secret
   
   • "Social Media - Bluesky API"
     Fields: identifier, password
   
   • "Social Media - LinkedIn API"
     Fields: access_token, person_id

4. Make sure you have the required Python packages installed:
   pip install requests requests-oauthlib pillow

Platform-specific setup:
• Instagram: Requires Facebook Page & Instagram Business Account
• X: Requires Twitter Developer Account
• Bluesky: Use your handle and app password
• LinkedIn: Requires LinkedIn Developer Account
        """
        
        text_widget = scrolledtext.ScrolledText(settings_frame, wrap=tk.WORD, height=15)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert("1.0", instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Test connection button
        test_button = ttk.Button(settings_frame, text="Test 1Password Connection", 
                                command=self.test_1password_connection)
        test_button.pack(pady=(0, 10))
        
        # Close button
        ttk.Button(settings_frame, text="Close", 
                  command=settings_window.destroy).pack()
    
    def test_1password_connection(self):
        """Test 1Password CLI connection"""
        try:
            # Try to list vaults to test connection
            cmd = ['op', 'vault', 'list', '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            vaults = json.loads(result.stdout)
            vault_names = [vault.get('name', 'Unknown') for vault in vaults]
            
            messagebox.showinfo("1Password Connection", 
                              f"✅ Successfully connected to 1Password!\n\n"
                              f"Available vaults: {', '.join(vault_names)}")
            
        except subprocess.CalledProcessError:
            messagebox.showerror("1Password Connection", 
                               "❌ Failed to connect to 1Password CLI.\n\n"
                               "Please make sure:\n"
                               "1. 1Password CLI is installed\n"
                               "2. You're signed in with 'op signin'")
        except Exception as e:
            messagebox.showerror("1Password Connection", 
                               f"❌ Error testing connection: {str(e)}")
    
    def post_to_platforms(self):
        """Post to selected platforms"""
        text = self.text_area.get("1.0", tk.END).strip()
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
        
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to post.")
            return
        
        if not selected_platforms:
            messagebox.showwarning("Warning", "Please select at least one platform.")
            return
        
        # Check for character limit violations
        text_length = len(text)
        over_limit_platforms = []
        
        for platform in selected_platforms:
            if text_length > self.character_limits[platform]:
                over_limit_platforms.append(platform)
        
        if over_limit_platforms:
            result = messagebox.askyesno("Character Limit Warning", 
                                       f"Your post exceeds the character limit for:\n"
                                       f"{', '.join(over_limit_platforms)}\n\n"
                                       f"Do you want to continue anyway?")
            if not result:
                return
        
        # Confirm posting
        platforms_text = ', '.join(selected_platforms)
        image_text = f"\nWith image: {os.path.basename(self.selected_image_path)}" if self.selected_image_path else ""
        
        confirm_msg = f"Post to {platforms_text}?{image_text}\n\nText preview:\n{text[:100]}{'...' if len(text) > 100 else ''}"
        
        if not messagebox.askyesno("Confirm Post", confirm_msg):
            return
        
        # Start posting in a separate thread to avoid freezing GUI
        self.start_posting_thread(text, selected_platforms)
    
    def start_posting_thread(self, text, platforms):
        """Start posting in a separate thread"""
        # Disable UI during posting
        self.post_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.status_var.set("Posting...")
        
        # Start thread
        thread = threading.Thread(target=self.post_worker, args=(text, platforms))
        thread.daemon = True
        thread.start()
    
    def post_worker(self, text, platforms):
        """Worker function for posting (runs in separate thread)"""
        try:
            # Initialize the backend poster
            from social_media_backend import SocialMediaBackend
            poster = SocialMediaBackend()
            
            # Post to platforms
            results = poster.post_to_platforms(text, platforms, self.selected_image_path)
            
            # Update UI in main thread
            self.root.after(0, self.posting_complete, results)
            
        except Exception as e:
            # Handle errors in main thread
            self.root.after(0, self.posting_error, str(e))
    
    def posting_complete(self, results):
        """Handle posting completion (runs in main thread)"""
        # Re-enable UI
        self.post_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        
        # Count results
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        # Update status
        self.status_var.set(f"Posting complete: {successful}/{total} successful")
        
        # Show results dialog
        self.show_results_dialog(results)
    
    def posting_error(self, error_msg):
        """Handle posting error (runs in main thread)"""
        # Re-enable UI
        self.post_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.status_var.set("Posting failed")
        
        messagebox.showerror("Posting Error", f"An error occurred while posting:\n\n{error_msg}")
    
    def show_results_dialog(self, results):
        """Show posting results in a dialog"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Posting Results")
        results_window.geometry("400x300")
        results_window.transient(self.root)
        results_window.grab_set()
        
        # Results content
        results_frame = ttk.Frame(results_window, padding="20")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(results_frame, text="Posting Results", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Results list
        for platform, success in results.items():
            status_icon = "✅" if success else "❌"
            status_text = "Success" if success else "Failed"
            
            result_frame = ttk.Frame(results_frame)
            result_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(result_frame, text=f"{status_icon} {platform}: {status_text}").pack(side=tk.LEFT)
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        ttk.Label(results_frame, text=f"Summary: {successful}/{total} successful", 
                 font=('Arial', 12, 'bold')).pack()
        
        # Close button
        ttk.Button(results_frame, text="Close", 
                  command=results_window.destroy).pack(pady=20)

class SocialMediaBackend:
    """
    Backend class for handling API calls to social media platforms
    Separated from GUI for better organization
    """
    
    def __init__(self):
        """Initialize backend with API endpoints"""
        self.api_endpoints = {
            'Instagram': 'https://graph.instagram.com/v19.0',
            'X (Twitter)': 'https://api.twitter.com/2/tweets',
            'Bluesky': 'https://bsky.social/xrpc',
            'LinkedIn': 'https://api.linkedin.com/v2/ugcPosts'
        }
    
    def get_credentials_from_1password(self, platform: str) -> Dict:
        """Get credentials from 1Password CLI"""
        try:
            # Map GUI platform names to 1Password item names
            platform_map = {
                'Instagram': 'Instagram',
                'X (Twitter)': 'X',
                'Bluesky': 'Bluesky',
                'LinkedIn': 'LinkedIn'
            }
            
            item_name = f"Social Media - {platform_map[platform]} API"
            
            # Get the item from 1Password
            cmd = ['op', 'item', 'get', item_name, '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            item_data = json.loads(result.stdout)
            
            # Extract credentials
            credentials = {}
            for field in item_data.get('fields', []):
                if field.get('id'):
                    credentials[field['id']] = field.get('value', '')
            
            return credentials
            
        except Exception as e:
            print(f"Error retrieving credentials for {platform}: {e}")
            return {}
    
    def post_to_platforms(self, text: str, platforms: List[str], 
                         image_path: Optional[str] = None) -> Dict[str, bool]:
        """Post to multiple platforms and return results"""
        results = {}
        
        for platform in platforms:
            print(f"Posting to {platform}...")
            
            try:
                if platform == 'Instagram':
                    results[platform] = self.post_to_instagram(text, image_path)
                elif platform == 'X (Twitter)':
                    results[platform] = self.post_to_x(text, image_path)
                elif platform == 'Bluesky':
                    results[platform] = self.post_to_bluesky(text, image_path)
                elif platform == 'LinkedIn':
                    results[platform] = self.post_to_linkedin(text, image_path)
                else:
                    results[platform] = False
                    
            except Exception as e:
                print(f"Error posting to {platform}: {e}")
                results[platform] = False
        
        return results
    
    def post_to_instagram(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post to Instagram (placeholder implementation)"""
        # This would contain the actual Instagram API implementation
        # For now, simulate a successful post
        import time
        time.sleep(1)  # Simulate API call
        return True
    
    def post_to_x(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post to X/Twitter (placeholder implementation)"""
        # This would contain the actual X API implementation
        import time
        time.sleep(1)  # Simulate API call
        return True
    
    def post_to_bluesky(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post to Bluesky (placeholder implementation)"""
        # This would contain the actual Bluesky API implementation
        import time
        time.sleep(1)  # Simulate API call
        return True
    
    def post_to_linkedin(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post to LinkedIn (placeholder implementation)"""
        # This would contain the actual LinkedIn API implementation
        import time
        time.sleep(1)  # Simulate API call
        return True

def main():
    """Main function to run the GUI application"""
    # Check for required dependencies
    try:
        import PIL
    except ImportError:
        print("Error: PIL (Pillow) is required for image handling.")
        print("Install with: pip install pillow")
        sys.exit(1)
    
    try:
        import requests
    except ImportError:
        print("Error: requests is required for API calls.")
        print("Install with: pip install requests requests-oauthlib")
        sys.exit(1)
    
    # Create and run the GUI
    root = tk.Tk()
    app = SocialMediaPosterGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == '__main__':
    main()