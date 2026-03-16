import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from utils.google_drive import check_drive_connection, TOKEN_FILE, OAUTH_CREDENTIALS_FILE
except ImportError:
    print("❌ Error: Could not find project utilities. Please run this script from the project root.")
    sys.exit(1)

def main():
    print("="*70)
    print("🔐 JHOM EXIM - GOOGLE DRIVE AUTHENTICATION SETUP")
    print("="*70)
    
    if not os.path.exists(OAUTH_CREDENTIALS_FILE):
        print(f"❌ Error: {OAUTH_CREDENTIALS_FILE} not found in project root.")
        print("Please ensure you have the OAuth credentials file from Google Cloud Console.")
        return

    if os.path.exists(TOKEN_FILE):
        print(f"💡 Removing existing token: {TOKEN_FILE}")
        try:
            os.remove(TOKEN_FILE)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove token file: {e}")

    print("\n🚀 Starting authentication...")
    print("A browser window will open shortly. Please follow the instructions to log in.\n")
    
    try:
        result = check_drive_connection()
        
        print("\n" + "="*70)
        if result['status'] == 'success':
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print(f"   Email Account: {result['user']}")
            print(f"   Storage Usage: {result['storage_used_gb']}GB / {result['storage_total_gb']}GB")
            print("\n   Folder Status:")
            for entity, status in result.get('folders', {}).items():
                print(f"   - {entity.capitalize()}: {status}")
            print("\n   You can now restart your server and use File Uploads!")
        else:
            print("❌ AUTHENTICATION FAILED")
            print(f"   Reason: {result['message']}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    
    print("="*70)
    input("\nPress ENTER to close this window...")

if __name__ == "__main__":
    main()
