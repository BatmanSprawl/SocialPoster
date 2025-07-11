# Social Media Poster

A comprehensive cross-platform social media posting tool that supports X (Twitter), Instagram, LinkedIn, Bluesky, and Mastodon. Works on both Windows and Linux with CLI and GUI interfaces.

## Features

- **Multi-platform support**: Post to X, Instagram, LinkedIn, Bluesky, and Mastodon
- **Character limit checking**: Automatically validates post length for each platform
- **Image support**: Attach images to posts (platform dependent)
- **Flexible authentication**: Use 1Password CLI or manual configuration
- **Cross-platform**: Works on Windows and Linux
- **Dual interface**: Command line and GUI modes
- **Hyperlink support**: Include links in your posts

## Installation

### Prerequisites

1. **Python 3.6 or higher**
2. **Required Python packages**:
   ```bash
   pip install requests
   ```

3. **Optional: 1Password CLI** (if using 1Password integration)
   - Download from: https://developer.1password.com/docs/cli/get-started/
   - Install and configure with `op signin`

### Setup

1. **Download the script**:
   ```bash
   curl -o social_poster.py [script_url]
   ```

2. **Make it executable (Linux/Mac)**:
   ```bash
   chmod +x social_poster.py
   ```

3. **Run initial setup**:
   ```bash
   python social_poster.py --text "test" --check-limits
   ```
   This will create a `social_config.json` template file.

## Configuration

### Method 1: Manual Configuration

Edit `social_config.json` and fill in your API credentials:

```json
{
  "use_1password": false,
  "twitter": {
    "bearer_token": "YOUR_TWITTER_BEARER_TOKEN"
  },
  "bluesky": {
    "handle": "your.handle.bsky.social",
    "password": "your-app-password"
  }
}
```

### Method 2: 1Password Integration

1. Store your API credentials in 1Password items
2. Configure `social_config.json`:
   ```json
   {
     "use_1password": true,
     "1password_vault": "Private",
     "twitter": {
       "op_item_name": "Twitter API"
     }
   }
   ```

## Platform-Specific Setup

### Twitter/X
1. Create a Twitter Developer account
2. Create a new app and generate Bearer Token
3. Add the Bearer Token to your config

### Instagram
- **Note**: Instagram posting requires a business account and complex media upload process
- This implementation provides the framework but requires additional development

### LinkedIn
1. Create a LinkedIn Developer account
2. Create an app with r_liteprofile and w_member_social permissions
3. Get your User ID and Access Token

### Bluesky
1. Create a Bluesky account
2. Generate an App Password in Settings
3. Use your handle and app password

### Mastodon
1. Go to your Mastodon instance → Settings → Development
2. Create a new application
3. Copy the Access Token

## Usage

### Command Line Interface

#### Basic usage:
```bash
# Post to all platforms
python social_poster.py --text "Hello, world!"

# Post to specific platforms
python social_poster.py --text "Hello, world!" --platforms twitter bluesky

# Include an image
python social_poster.py --text "Check out this image!" --image path/to/image.jpg

# Check character limits without posting
python social_poster.py --text "Long message here..." --check-limits
```

#### Advanced usage:
```bash
# Use custom config file
python social_poster.py --config my_config.json --text "Hello!"

# Post with hyperlinks
python social_poster.py --text "Check out this link: https://example.com"
```

### GUI Interface

Launch the GUI:
```bash
python social_poster.py --gui
```

The GUI provides:
- Text input area with live character count
- Platform selection checkboxes
- Image file browser
- Configuration status checker
- Post results display

## Character Limits

- **Twitter**: 280 characters
- **Instagram**: 2,200 characters (caption)
- **LinkedIn**: 3,000 characters
- **Bluesky**: 300 characters
- **Mastodon**: 500 characters (default, varies by instance)

## Troubleshooting

### Common Issues

1. **"Config file not found"**
   - Run the script once to generate the template
   - Fill in your credentials

2. **"Authentication failed"**
   - Verify your API keys/tokens are correct
   - Check if tokens have expired

3. **"GUI not available"**
   - Install tkinter: `sudo apt-get install python3-tk` (Linux)
   - tkinter is included with Python on Windows

4. **1Password CLI errors**
   - Ensure 1Password CLI is installed and signed in
   - Check vault name and item names are correct

### Platform-Specific Issues

- **Twitter**: Requires Bearer Token (not just API keys)
- **Instagram**: Complex