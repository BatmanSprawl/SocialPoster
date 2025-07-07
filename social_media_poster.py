#!/usr/bin/env python3
"""
Multi-Platform Social Media Poster
A secure Python script for posting to Instagram, X (Twitter), Bluesky, and LinkedIn
Uses 1Password CLI for secure credential management
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple
import requests
from requests_oauthlib import OAuth1Session
import base64
from pathlib import Path

class SocialMediaPoster:
    """
    Main class for handling social media posts across multiple platforms
    Integrates with 1Password CLI for secure credential management
    """
    
    def __init__(self):
        """Initialize the poster with platform-specific character limits"""
        # Character limits for each platform (as of 2025)
        self.character_limits = {
            'instagram': 2200,  # Instagram caption limit
            'x': 280,           # X (Twitter) standard limit
            'bluesky': 300,     # Bluesky character limit
            'linkedin': 3000    # LinkedIn post limit
        }
        
        # Store credentials retrieved from 1Password
        self.credentials = {}
        
        # API endpoints for each platform
        self.api_endpoints = {
            'x': 'https://api.twitter.com/2/tweets',
            'bluesky': 'https://bsky.social/xrpc',
            'linkedin': 'https://api.linkedin.com/v2/ugcPosts',
            'instagram': 'https://graph.instagram.com/v19.0'
        }

    def get_credentials_from_1password(self, platform: str) -> Dict:
        """
        Retrieve credentials from 1Password using the CLI
        
        Args:
            platform: The social media platform name
            
        Returns:
            Dictionary containing the credentials for the platform
            
        Note: You'll need to store your API credentials in 1Password with these item names:
        - "Social Media - Instagram API"
        - "Social Media - X API" 
        - "Social Media - Bluesky API"
        - "Social Media - LinkedIn API"
        
        Each item should contain the necessary fields (tokens, secrets, etc.)
        """
        try:
            # 1Password CLI command to get credentials
            # Replace 'your-vault-name' with your actual 1Password vault name
            item_name = f"Social Media - {platform.title()} API"
            
            # Get the item from 1Password in JSON format
            cmd = ['op', 'item', 'get', item_name, '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the JSON response from 1Password
            item_data = json.loads(result.stdout)
            
            # Extract credentials from the 1Password item fields
            credentials = {}
            for field in item_data.get('fields', []):
                if field.get('id'):
                    credentials[field['id']] = field.get('value', '')
            
            return credentials
            
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving credentials from 1Password: {e}")
            print("Make sure you're logged into 1Password CLI with 'op signin'")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing 1Password response: {e}")
            return {}

    def check_character_limit(self, text: str, platforms: List[str]) -> Tuple[bool, Dict[str, int]]:
        """
        Check if text exceeds character limits for specified platforms
        
        Args:
            text: The text content to check
            platforms: List of platform names to check against
            
        Returns:
            Tuple of (is_valid, platform_status) where platform_status shows
            character count vs limit for each platform
        """
        text_length = len(text)
        platform_status = {}
        is_valid = True
        
        for platform in platforms:
            if platform in self.character_limits:
                limit = self.character_limits[platform]
                platform_status[platform] = {
                    'length': text_length,
                    'limit': limit,
                    'over_limit': text_length > limit,
                    'remaining': limit - text_length
                }
                
                if text_length > limit:
                    is_valid = False
        
        return is_valid, platform_status

    def post_to_instagram(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Post to Instagram using the Instagram Graph API
        
        Args:
            text: Caption text for the post
            image_path: Optional path to image file
            
        Returns:
            True if successful, False otherwise
            
        Note: Instagram Graph API requires a Facebook Page and Instagram Business Account
        You'll need: access_token, instagram_account_id in your 1Password item
        """
        try:
            creds = self.get_credentials_from_1password('instagram')
            if not creds:
                print("Failed to retrieve Instagram credentials")
                return False
            
            access_token = creds.get('access_token')
            instagram_account_id = creds.get('instagram_account_id')
            
            if not access_token or not instagram_account_id:
                print("Missing required Instagram credentials")
                return False
            
            # Instagram requires a two-step process: create media, then publish
            
            # Step 1: Create media object
            if image_path and os.path.exists(image_path):
                # For image posts
                media_url = f"{self.api_endpoints['instagram']}/{instagram_account_id}/media"
                media_data = {
                    'image_url': image_path,  # Note: Instagram API requires publicly accessible URLs
                    'caption': text,
                    'access_token': access_token
                }
            else:
                # For text-only posts (requires image for Instagram API)
                print("Instagram API requires an image. Text-only posts not supported via API.")
                return False
            
            # Make the media creation request
            response = requests.post(media_url, data=media_data)
            
            if response.status_code != 200:
                print(f"Failed to create Instagram media: {response.text}")
                return False
            
            media_id = response.json().get('id')
            
            # Step 2: Publish the media
            publish_url = f"{self.api_endpoints['instagram']}/{instagram_account_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            
            if publish_response.status_code == 200:
                print("✓ Successfully posted to Instagram")
                return True
            else:
                print(f"Failed to publish to Instagram: {publish_response.text}")
                return False
                
        except Exception as e:
            print(f"Error posting to Instagram: {e}")
            return False

    def post_to_x(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Post to X (Twitter) using the Twitter API v2
        
        Args:
            text: Tweet text
            image_path: Optional path to image file
            
        Returns:
            True if successful, False otherwise
            
        Note: You'll need these credentials in your 1Password item:
        - consumer_key, consumer_secret, access_token, access_token_secret
        """
        try:
            creds = self.get_credentials_from_1password('x')
            if not creds:
                print("Failed to retrieve X credentials")
                return False
            
            # Set up OAuth1 session for Twitter API
            auth = OAuth1Session(
                creds.get('consumer_key'),
                client_secret=creds.get('consumer_secret'),
                resource_owner_key=creds.get('access_token'),
                resource_owner_secret=creds.get('access_token_secret')
            )
            
            # Handle image upload if provided
            media_ids = []
            if image_path and os.path.exists(image_path):
                # Upload media first
                media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
                
                with open(image_path, 'rb') as f:
                    files = {'media': f}
                    media_response = auth.post(media_upload_url, files=files)
                
                if media_response.status_code == 200:
                    media_id = media_response.json()['media_id_string']
                    media_ids.append(media_id)
                else:
                    print(f"Failed to upload image to X: {media_response.text}")
                    return False
            
            # Prepare tweet data
            tweet_data = {'text': text}
            if media_ids:
                tweet_data['media'] = {'media_ids': media_ids}
            
            # Post the tweet
            response = auth.post(self.api_endpoints['x'], json=tweet_data)
            
            if response.status_code == 201:
                print("✓ Successfully posted to X")
                return True
            else:
                print(f"Failed to post to X: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error posting to X: {e}")
            return False

    def post_to_bluesky(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Post to Bluesky using the AT Protocol
        
        Args:
            text: Post text
            image_path: Optional path to image file
            
        Returns:
            True if successful, False otherwise
            
        Note: You'll need these credentials in your 1Password item:
        - identifier (your handle), password (app password)
        """
        try:
            creds = self.get_credentials_from_1password('bluesky')
            if not creds:
                print("Failed to retrieve Bluesky credentials")
                return False
            
            identifier = creds.get('identifier')
            password = creds.get('password')
            
            # Step 1: Create session (authenticate)
            session_url = f"{self.api_endpoints['bluesky']}/com.atproto.server.createSession"
            session_data = {
                'identifier': identifier,
                'password': password
            }
            
            session_response = requests.post(session_url, json=session_data)
            
            if session_response.status_code != 200:
                print(f"Failed to authenticate with Bluesky: {session_response.text}")
                return False
            
            session_info = session_response.json()
            access_jwt = session_info.get('accessJwt')
            did = session_info.get('did')
            
            # Prepare headers for authenticated requests
            headers = {
                'Authorization': f'Bearer {access_jwt}',
                'Content-Type': 'application/json'
            }
            
            # Step 2: Handle image upload if provided
            embed = None
            if image_path and os.path.exists(image_path):
                # Upload blob
                upload_url = f"{self.api_endpoints['bluesky']}/com.atproto.repo.uploadBlob"
                
                with open(image_path, 'rb') as f:
                    upload_headers = {
                        'Authorization': f'Bearer {access_jwt}',
                        'Content-Type': 'image/jpeg'  # Adjust based on image type
                    }
                    upload_response = requests.post(upload_url, headers=upload_headers, data=f)
                
                if upload_response.status_code == 200:
                    blob_data = upload_response.json()['blob']
                    embed = {
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'image': blob_data,
                            'alt': 'Image'
                        }]
                    }
                else:
                    print(f"Failed to upload image to Bluesky: {upload_response.text}")
                    return False
            
            # Step 3: Create the post
            post_url = f"{self.api_endpoints['bluesky']}/com.atproto.repo.createRecord"
            
            post_data = {
                'repo': did,
                'collection': 'app.bsky.feed.post',
                'record': {
                    '$type': 'app.bsky.feed.post',
                    'text': text,
                    'createdAt': requests.utils.default_headers()['User-Agent']  # Use current timestamp
                }
            }
            
            if embed:
                post_data['record']['embed'] = embed
            
            post_response = requests.post(post_url, headers=headers, json=post_data)
            
            if post_response.status_code == 200:
                print("✓ Successfully posted to Bluesky")
                return True
            else:
                print(f"Failed to post to Bluesky: {post_response.text}")
                return False
                
        except Exception as e:
            print(f"Error posting to Bluesky: {e}")
            return False

    def post_to_linkedin(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Post to LinkedIn using the LinkedIn API
        
        Args:
            text: Post text
            image_path: Optional path to image file
            
        Returns:
            True if successful, False otherwise
            
        Note: You'll need these credentials in your 1Password item:
        - access_token, person_id (your LinkedIn person ID)
        """
        try:
            creds = self.get_credentials_from_1password('linkedin')
            if not creds:
                print("Failed to retrieve LinkedIn credentials")
                return False
            
            access_token = creds.get('access_token')
            person_id = creds.get('person_id')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare post data
            post_data = {
                'author': f'urn:li:person:{person_id}',
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
            
            # Handle image upload if provided
            if image_path and os.path.exists(image_path):
                # LinkedIn image upload is complex and requires multiple steps
                # For now, we'll post text-only and mention the limitation
                print("Note: LinkedIn image upload requires additional setup. Posting text only.")
            
            # Make the post request
            response = requests.post(self.api_endpoints['linkedin'], 
                                   headers=headers, json=post_data)
            
            if response.status_code == 201:
                print("✓ Successfully posted to LinkedIn")
                return True
            else:
                print(f"Failed to post to LinkedIn: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error posting to LinkedIn: {e}")
            return False

    def post_to_platforms(self, text: str, platforms: List[str], 
                         image_path: Optional[str] = None) -> Dict[str, bool]:
        """
        Post to multiple platforms
        
        Args:
            text: Post text
            platforms: List of platform names to post to
            image_path: Optional path to image file
            
        Returns:
            Dictionary mapping platform names to success status
        """
        results = {}
        
        # Check character limits first
        is_valid, status = self.check_character_limit(text, platforms)
        
        if not is_valid:
            print("\n⚠️  Character limit warnings:")
            for platform, info in status.items():
                if info['over_limit']:
                    print(f"  {platform}: {info['length']}/{info['limit']} characters "
                          f"({info['length'] - info['limit']} over limit)")
            
            response = input("\nContinue posting anyway? (y/N): ")
            if response.lower() != 'y':
                print("Posting cancelled.")
                return {platform: False for platform in platforms}
        
        # Post to each platform
        for platform in platforms:
            print(f"\nPosting to {platform}...")
            
            if platform == 'instagram':
                results[platform] = self.post_to_instagram(text, image_path)
            elif platform == 'x':
                results[platform] = self.post_to_x(text, image_path)
            elif platform == 'bluesky':
                results[platform] = self.post_to_bluesky(text, image_path)
            elif platform == 'linkedin':
                results[platform] = self.post_to_linkedin(text, image_path)
            else:
                print(f"Unknown platform: {platform}")
                results[platform] = False
        
        return results

def main():
    """
    Main function to handle command line arguments and execute posting
    """
    parser = argparse.ArgumentParser(
        description='Post to multiple social media platforms securely',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Post to X only
  python social_poster.py -p x -t "Hello world!"
  
  # Post to multiple platforms
  python social_poster.py -p x bluesky linkedin -t "Check out this cool project!"
  
  # Post with an image
  python social_poster.py -p instagram x -t "Beautiful sunset!" -i ./sunset.jpg
  
  # Post to all platforms
  python social_poster.py -p all -t "Big announcement coming soon!"
  
  # Check character limits without posting
  python social_poster.py -p x bluesky -t "This is a test message" --check-only

Setup Instructions:
1. Install required packages: pip install requests requests-oauthlib
2. Install 1Password CLI: https://developer.1password.com/docs/cli/get-started/
3. Sign in to 1Password CLI: op signin
4. Create API credential items in 1Password with names like "Social Media - X API"
5. Configure your API credentials for each platform in 1Password
        """
    )
    
    parser.add_argument('-p', '--platforms', nargs='+', 
                       choices=['instagram', 'x', 'bluesky', 'linkedin', 'all'],
                       required=True,
                       help='Platforms to post to (or "all" for all platforms)')
    
    parser.add_argument('-t', '--text', required=True,
                       help='Text content to post')
    
    parser.add_argument('-i', '--image', 
                       help='Path to image file to upload')
    
    parser.add_argument('--check-only', action='store_true',
                       help='Only check character limits without posting')
    
    args = parser.parse_args()
    
    # Handle "all" platform option
    if 'all' in args.platforms:
        platforms = ['instagram', 'x', 'bluesky', 'linkedin']
    else:
        platforms = args.platforms
    
    # Initialize the poster
    poster = SocialMediaPoster()
    
    # Check if image file exists
    if args.image and not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)
    
    # Check character limits
    is_valid, status = poster.check_character_limit(args.text, platforms)
    
    print("Character limit check:")
    print("-" * 40)
    for platform, info in status.items():
        status_icon = "✓" if not info['over_limit'] else "✗"
        print(f"{status_icon} {platform}: {info['length']}/{info['limit']} characters "
              f"({info['remaining']} remaining)")
    
    if args.check_only:
        sys.exit(0)
    
    # Proceed with posting
    print(f"\nPosting to platforms: {', '.join(platforms)}")
    if args.image:
        print(f"Including image: {args.image}")
    
    results = poster.post_to_platforms(args.text, platforms, args.image)
    
    # Display results
    print("\n" + "=" * 50)
    print("POSTING RESULTS")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for platform, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{platform}: {status}")
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"\nSummary: {successful} successful, {failed} failed")
    
    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
