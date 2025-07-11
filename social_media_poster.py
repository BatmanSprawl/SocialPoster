#!/usr/bin/env python3
"""
Multi-Platform Social Media Posting Script
Supports: X (Twitter), Instagram, LinkedIn, Bluesky, Mastodon
Works on Windows and Linux with CLI and GUI modes
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import urllib.parse
from datetime import datetime

# GUI imports (optional)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

class SocialMediaPoster:
    """Main class for handling social media posts across platforms"""
    
    # Character limits for each platform
    CHAR_LIMITS = {
        'twitter': 280,
        'instagram': 2200,  # Caption limit
        'linkedin': 3000,
        'bluesky': 300,
        'mastodon': 500  # Default, can vary by instance
    }
    
    def __init__(self, config_file: str = 'social_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            print(f"Config file {self.config_file} not found. Creating template...")
            self.create_config_template()
            return {}
            
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.config_file}")
            return {}
    
    def create_config_template(self):
        """Create a template configuration file"""
        template = {
            "use_1password": False,
            "1password_vault": "Private",
            "twitter": {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": "",
                "bearer_token": "",
                "op_item_name": "Twitter API"
            },
            "instagram": {
                "access_token": "",
                "business_account_id": "",
                "op_item_name": "Instagram Basic Display"
            },
            "linkedin": {
                "access_token": "",
                "user_id": "",
                "op_item_name": "LinkedIn API"
            },
            "bluesky": {
                "handle": "",
                "password": "",
                "op_item_name": "Bluesky"
            },
            "mastodon": {
                "instance_url": "https://mastodon.social",
                "access_token": "",
                "op_item_name": "Mastodon"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Created config template at {self.config_file}")
        print("Please fill in your API credentials and tokens.")
    
    def get_1password_secret(self, item_name: str, field: str, vault: str = None) -> str:
        """Get secret from 1Password CLI"""
        try:
            vault_flag = f"--vault={vault}" if vault else ""
            cmd = f"op item get '{item_name}' --field={field} {vault_flag}".strip()
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"1Password CLI error: {result.stderr}")
                return ""
        except Exception as e:
            print(f"Error accessing 1Password: {e}")
            return ""
    
    def get_credentials(self, platform: str) -> Dict:
        """Get credentials for a platform, either from 1Password or config file"""
        if platform not in self.config:
            return {}
            
        platform_config = self.config[platform]
        
        if self.config.get('use_1password', False):
            # Get from 1Password
            op_item = platform_config.get('op_item_name', '')
            vault = self.config.get('1password_vault', 'Private')
            
            if op_item:
                credentials = {}
                for key, value in platform_config.items():
                    if key != 'op_item_name' and isinstance(value, str):
                        op_value = self.get_1password_secret(op_item, key, vault)
                        credentials[key] = op_value if op_value else value
                return credentials
        
        # Return from config file
        return {k: v for k, v in platform_config.items() if k != 'op_item_name'}
    
    def check_character_limit(self, text: str, platform: str) -> Tuple[bool, int, int]:
        """Check if text exceeds character limit for platform"""
        limit = self.CHAR_LIMITS.get(platform, 280)
        char_count = len(text)
        return char_count <= limit, char_count, limit
    
    def post_to_twitter(self, text: str, image_path: str = None) -> bool:
        """Post to Twitter/X using API v2"""
        creds = self.get_credentials('twitter')
        if not creds.get('bearer_token'):
            print("Twitter: Missing bearer token")
            return False
            
        # Check character limit
        valid, count, limit = self.check_character_limit(text, 'twitter')
        if not valid:
            print(f"Twitter: Text too long ({count}/{limit} characters)")
            return False
        
        headers = {
            'Authorization': f'Bearer {creds["bearer_token"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {'text': text}
        
        # TODO: Add image upload support for Twitter API v2
        if image_path:
            print("Twitter: Image upload not implemented in this version")
        
        try:
            response = requests.post(
                'https://api.twitter.com/2/tweets',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                print("Twitter: Posted successfully")
                return True
            else:
                print(f"Twitter: Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"Twitter: Error posting: {e}")
            return False
    
    def post_to_instagram(self, text: str, image_path: str = None) -> bool:
        """Post to Instagram (requires image)"""
        creds = self.get_credentials('instagram')
        if not creds.get('access_token') or not creds.get('business_account_id'):
            print("Instagram: Missing access token or business account ID")
            return False
        
        if not image_path:
            print("Instagram: Image required for posting")
            return False
            
        # Check character limit
        valid, count, limit = self.check_character_limit(text, 'instagram')
        if not valid:
            print(f"Instagram: Caption too long ({count}/{limit} characters)")
            return False
        
        # Instagram Graph API posting is complex and requires image upload
        # This is a simplified version - full implementation would need media upload
        print("Instagram: API posting not fully implemented - requires complex media upload flow")
        return False
    
    def post_to_linkedin(self, text: str, image_path: str = None) -> bool:
        """Post to LinkedIn"""
        creds = self.get_credentials('linkedin')
        if not creds.get('access_token') or not creds.get('user_id'):
            print("LinkedIn: Missing access token or user ID")
            return False
            
        # Check character limit
        valid, count, limit = self.check_character_limit(text, 'linkedin')
        if not valid:
            print(f"LinkedIn: Text too long ({count}/{limit} characters)")
            return False
        
        headers = {
            'Authorization': f'Bearer {creds["access_token"]}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        payload = {
            'author': f'urn:li:person:{creds["user_id"]}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        try:
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                print("LinkedIn: Posted successfully")
                return True
            else:
                print(f"LinkedIn: Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"LinkedIn: Error posting: {e}")
            return False
    
    def post_to_bluesky(self, text: str, image_path: str = None) -> bool:
        """Post to Bluesky"""
        creds = self.get_credentials('bluesky')
        if not creds.get('handle') or not creds.get('password'):
            print("Bluesky: Missing handle or password")
            return False
            
        # Check character limit
        valid, count, limit = self.check_character_limit(text, 'bluesky')
        if not valid:
            print(f"Bluesky: Text too long ({count}/{limit} characters)")
            return False
        
        try:
            # Create session
            session_data = {
                'identifier': creds['handle'],
                'password': creds['password']
            }
            
            session_response = requests.post(
                'https://bsky.social/xrpc/com.atproto.server.createSession',
                json=session_data
            )
            
            if session_response.status_code != 200:
                print(f"Bluesky: Authentication failed: {session_response.text}")
                return False
                
            session_info = session_response.json()
            access_token = session_info['accessJwt']
            
            # Create post
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            post_data = {
                'repo': session_info['did'],
                'collection': 'app.bsky.feed.post',
                'record': {
                    'text': text,
                    'createdAt': datetime.now().isoformat() + 'Z'
                }
            }
            
            post_response = requests.post(
                'https://bsky.social/xrpc/com.atproto.repo.createRecord',
                headers=headers,
                json=post_data
            )
            
            if post_response.status_code == 200:
                print("Bluesky: Posted successfully")
                return True
            else:
                print(f"Bluesky: Error {post_response.status_code}: {post_response.text}")
                return False
                
        except Exception as e:
            print(f"Bluesky: Error posting: {e}")
            return False
    
    def post_to_mastodon(self, text: str, image_path: str = None) -> bool:
        """Post to Mastodon"""
        creds = self.get_credentials('mastodon')
        if not creds.get('access_token') or not creds.get('instance_url'):
            print("Mastodon: Missing access token or instance URL")
            return False
            
        # Check character limit
        valid, count, limit = self.check_character_limit(text, 'mastodon')
        if not valid:
            print(f"Mastodon: Text too long ({count}/{limit} characters)")
            return False
        
        headers = {
            'Authorization': f'Bearer {creds["access_token"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'status': text,
            'visibility': 'public'
        }
        
        try:
            url = f"{creds['instance_url'].rstrip('/')}/api/v1/statuses"
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print("Mastodon: Posted successfully")
                return True
            else:
                print(f"Mastodon: Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"Mastodon: Error posting: {e}")
            return False
    
    def post_to_platforms(self, text: str, platforms: List[str], image_path: str = None) -> Dict[str, bool]:
        """Post to multiple platforms"""
        results = {}
        
        platform_methods = {
            'twitter': self.post_to_twitter,
            'instagram': self.post_to_instagram,
            'linkedin': self.post_to_linkedin,
            'bluesky': self.post_to_bluesky,
            'mastodon': self.post_to_mastodon
        }
        
        for platform in platforms:
            if platform in platform_methods:
                print(f"\n--- Posting to {platform.upper()} ---")
                results[platform] = platform_methods[platform](text, image_path)
            else:
                print(f"Unknown platform: {platform}")
                results[platform] = False
                
        return results

class SocialMediaGUI:
    """GUI interface for the social media poster"""
    
    def __init__(self, poster: SocialMediaPoster):
        self.poster = poster
        self.root = tk.Tk()
        self.root.title("Social Media Poster")
        self.root.geometry("800x600")
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text input
        ttk.Label(main_frame, text="Post Content:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.text_widget = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.text_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Character count display
        self.char_count_frame = ttk.Frame(main_frame)
        self.char_count_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.char_labels = {}
        for i, platform in enumerate(['twitter', 'instagram', 'linkedin', 'bluesky', 'mastodon']):
            label = ttk.Label(self.char_count_frame, text=f"{platform.title()}: 0/280")
            label.grid(row=i//3, column=i%3, padx=5, pady=2, sticky=tk.W)
            self.char_labels[platform] = label
        
        # Bind text change event
        self.text_widget.bind('<KeyRelease>', self.update_char_counts)
        
        # Image selection
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.image_path = tk.StringVar()
        ttk.Label(image_frame, text="Image (optional):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(image_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(image_frame, text="Browse", command=self.browse_image).grid(row=0, column=2, padx=(5, 0))
        
        # Platform selection
        platform_frame = ttk.LabelFrame(main_frame, text="Platforms", padding="5")
        platform_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.platform_vars = {}
        platforms = ['twitter', 'instagram', 'linkedin', 'bluesky', 'mastodon']
        for i, platform in enumerate(platforms):
            var = tk.BooleanVar()
            ttk.Checkbutton(platform_frame, text=platform.title(), variable=var).grid(
                row=i//3, column=i%3, sticky=tk.W, padx=5
            )
            self.platform_vars[platform] = var
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Post", command=self.post_content).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_content).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Check Config", command=self.check_config).grid(row=0, column=2, padx=5)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.status_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def update_char_counts(self, event=None):
        """Update character count displays"""
        text = self.text_widget.get("1.0", tk.END).strip()
        
        for platform, label in self.char_labels.items():
            valid, count, limit = self.poster.check_character_limit(text, platform)
            color = "green" if valid else "red"
            label.config(text=f"{platform.title()}: {count}/{limit}", foreground=color)
    
    def browse_image(self):
        """Browse for image file"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            self.image_path.set(filename)
    
    def post_content(self):
        """Post content to selected platforms"""
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some content to post.")
            return
        
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
        if not selected_platforms:
            messagebox.showwarning("Warning", "Please select at least one platform.")
            return
        
        image_path = self.image_path.get() if self.image_path.get() else None
        
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, "Posting...\n")
        self.root.update()
        
        results = self.poster.post_to_platforms(text, selected_platforms, image_path)
        
        self.status_text.insert(tk.END, "\n--- Results ---\n")
        for platform, success in results.items():
            status = "✓ Success" if success else "✗ Failed"
            self.status_text.insert(tk.END, f"{platform.title()}: {status}\n")
    
    def clear_content(self):
        """Clear all content"""
        self.text_widget.delete("1.0", tk.END)
        self.image_path.set("")
        self.status_text.delete("1.0", tk.END)
        for var in self.platform_vars.values():
            var.set(False)
    
    def check_config(self):
        """Check configuration status"""
        config_status = "Configuration Status:\n\n"
        
        for platform in ['twitter', 'instagram', 'linkedin', 'bluesky', 'mastodon']:
            creds = self.poster.get_credentials(platform)
            has_creds = bool(creds and any(creds.values()))
            status = "✓ Configured" if has_creds else "✗ Not configured"
            config_status += f"{platform.title()}: {status}\n"
        
        messagebox.showinfo("Configuration Status", config_status)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Multi-platform social media poster")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("--text", type=str, help="Text to post")
    parser.add_argument("--image", type=str, help="Path to image file")
    parser.add_argument("--platforms", nargs="+", 
                       choices=["twitter", "instagram", "linkedin", "bluesky", "mastodon", "all"],
                       default=["all"], help="Platforms to post to")
    parser.add_argument("--config", type=str, default="social_config.json", 
                       help="Configuration file path")
    parser.add_argument("--check-limits", action="store_true", 
                       help="Check character limits without posting")
    
    args = parser.parse_args()
    
    # Initialize poster
    poster = SocialMediaPoster(args.config)
    
    # Handle GUI mode
    if args.gui:
        if not GUI_AVAILABLE:
            print("GUI not available. Please install tkinter.")
            sys.exit(1)
        
        gui = SocialMediaGUI(poster)
        gui.run()
        return
    
    # Handle command line mode
    if not args.text:
        print("Error: --text is required for command line mode")
        sys.exit(1)
    
    platforms = args.platforms
    if "all" in platforms:
        platforms = ["twitter", "instagram", "linkedin", "bluesky", "mastodon"]
    
    # Check character limits
    if args.check_limits:
        print("Character limit check:")
        for platform in platforms:
            valid, count, limit = poster.check_character_limit(args.text, platform)
            status = "✓" if valid else "✗"
            print(f"{platform.title()}: {count}/{limit} {status}")
        return
    
    # Post to platforms
    results = poster.post_to_platforms(args.text, platforms, args.image)
    
    print("\n--- Final Results ---")
    for platform, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"{platform.title()}: {status}")

if __name__ == "__main__":
    main()
