import os
import sys
sys.path.append('.')

from app.core.config import settings

def test_directory_structure():
    """Test and create the upload directory structure"""
    print(f"Current working directory: {os.getcwd()}")
    print(f"Upload directory setting: {settings.UPLOAD_DIR}")
    
    # Check if uploads directory exists
    uploads_dir = settings.UPLOAD_DIR or "./uploads"
    print(f"Checking uploads directory: {uploads_dir}")
    
    if os.path.exists(uploads_dir):
        print(f"✅ Uploads directory exists: {uploads_dir}")
        print(f"Contents: {os.listdir(uploads_dir)}")
    else:
        print(f"❌ Uploads directory does not exist: {uploads_dir}")
        print("Creating uploads directory...")
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Check listings subdirectory
    listings_dir = os.path.join(uploads_dir, "listings")
    print(f"Checking listings directory: {listings_dir}")
    
    if os.path.exists(listings_dir):
        print(f"✅ Listings directory exists: {listings_dir}")
        print(f"Contents: {os.listdir(listings_dir)}")
    else:
        print(f"❌ Listings directory does not exist: {listings_dir}")
        print("Creating listings directory...")
        os.makedirs(listings_dir, exist_ok=True)
    
    # Test file creation
    test_file_path = os.path.join(listings_dir, "test_file.txt")
    print(f"Testing file creation at: {test_file_path}")
    
    try:
        with open(test_file_path, "w") as f:
            f.write("Test file content")
        print("✅ Test file created successfully")
        
        # Verify file exists
        if os.path.exists(test_file_path):
            print("✅ Test file verified to exist")
            # Clean up
            os.remove(test_file_path)
            print("✅ Test file cleaned up")
        else:
            print("❌ Test file was not found after creation")
            
    except Exception as e:
        print(f"❌ Error creating test file: {e}")

if __name__ == "__main__":
    test_directory_structure()
