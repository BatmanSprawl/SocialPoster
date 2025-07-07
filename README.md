# SocialPoster
Social Media Poster Script

~-~-~-~-~-~-SCRIPT~-~-~-~-~-~-~-~-

I've created a comprehensive Python script for posting to multiple social media platforms with secure 1Password integration. Here's what the script includes:
Key Features:

Multi-platform support: Instagram, X (Twitter), Bluesky, and LinkedIn
Secure credential management: Uses 1Password CLI to store API keys safely
Character limit checking: Warns you before posting if content exceeds platform limits
Image upload support: Handles image attachments for supported platforms
Flexible posting options: Post to individual platforms or all at once
Error handling: Comprehensive error handling with clear feedback

Setup Requirements:

Install dependencies:
bashpip install requests requests-oauthlib

Install 1Password CLI: Follow the guide at https://developer.1password.com/docs/cli/get-started/
Sign in to 1Password CLI:
bashop signin

Create API credential items in your 1Password vault with these exact names:

"Social Media - Instagram API"
"Social Media - X API"
"Social Media - Bluesky API"
"Social Media - LinkedIn API"


Configure API credentials for each platform in their respective 1Password items:

Instagram: access_token, instagram_account_id
X: consumer_key, consumer_secret, access_token, access_token_secret
Bluesky: identifier, password
LinkedIn: access_token, person_id



Usage Examples:
bash# Post to X only
python social_poster.py -p x -t "Hello world!"

# Post to multiple platforms
python social_poster.py -p x bluesky linkedin -t "Check out this cool project!"

# Post with an image
python social_poster.py -p instagram x -t "Beautiful sunset!" -i ./sunset.jpg

# Post to all platforms
python social_poster.py -p all -t "Big announcement coming soon!"

# Check character limits without posting
python social_poster.py -p x bluesky -t "This is a test message" --check-only
Important Notes:

Instagram API limitations: The Instagram Graph API requires a Facebook Page and Instagram Business Account, and doesn't support text-only posts.
API Setup: Each platform requires you to register for developer access and create API applications to get the necessary credentials.
Rate limits: Each platform has different rate limits. The script includes basic error handling for this.
Security: Never hardcode API credentials in your script. The 1Password integration ensures your sensitive data stays secure.

The script is extensively commented to help you understand each section and make modifications as needed. Each function explains what it does and what APIs it calls, making it easy to customize for your specific needs.

~-~-~-~-~-~-GUI~-~-~-~-~-~-~-~-

I've created a complete GUI application for your social media poster! Here's what the application includes:
Key Features:
🎯 User Interface

Platform Selection: Checkboxes for Instagram, X (Twitter), Bluesky, and LinkedIn
Text Input: Large text area with scroll support for your post content
Image Upload: Select and preview images with file dialog
Real-time Validation: Character count display with color-coded warnings
Action Buttons: Post, Clear All, and Settings buttons

📊 Smart Validation

Character Limits: Real-time checking against each platform's limits
Visual Feedback: Color-coded character counts (green/orange/red)
URL Detection: Automatically detects and counts URLs in your text
Over-limit Warnings: Warns before posting if you exceed character limits

🔒 Security Features

1Password Integration: Secure credential storage and retrieval
No Hardcoded Secrets: All API keys stored safely in 1Password
Settings Panel: Easy setup instructions and connection testing

🚀 Posting Features

Multi-platform Posting: Post to selected platforms simultaneously
Image Support: Upload and attach images to your posts
Progress Tracking: Visual progress bar during posting
Results Display: Detailed success/failure report after posting

Installation Requirements:
bash# Install required Python packages
pip install requests requests-oauthlib pillow

# Install 1Password CLI
# Visit: https://developer.1password.com/docs/cli/get-started/
Setup Instructions:

Install 1Password CLI and sign in with op signin
Create these items in your 1Password vault:

"Social Media - Instagram API" (fields: access_token, instagram_account_id)
"Social Media - X API" (fields: consumer_key, consumer_secret, access_token, access_token_secret)
"Social Media - Bluesky API" (fields: identifier, password)
"Social Media - LinkedIn API" (fields: access_token, person_id)


Run the application:
bashpython social_media_gui.py


How to Use:

Select Platforms: Check the boxes for platforms you want to post to
Enter Text: Type your post content in the text area
Add Image (optional): Click "Select Image" to upload a photo
Check Limits: Watch the character count display for warnings
Post: Click "📤 Post to Selected Platforms" to send your content
Review Results: See the success/failure report for each platform

Special Features:

Select All/Deselect All: Quickly toggle all platforms
Image Preview: See a thumbnail of your selected image
URL Detection: Automatically detects links in your text
Settings Panel: Test 1Password connection and view setup instructions
Threading: Posts run in background threads so the UI stays responsive
Error Handling: Comprehensive error handling with user-friendly messages

The application is designed to be intuitive and safe, with multiple validation layers to prevent posting mistakes. The real-time character counting helps you optimize your content for each platform's specific requirements.
To get started, just run the script and click the "⚙️ Settings" button for detailed setup instructions!