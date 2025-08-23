import os
import sys
import uuid
sys.path.append('.')

from app.core.config import settings

def manual_file_save_test():
    """Manually test the file saving logic"""
    print("=== Manual File Save Test ===")
    
    # Simulate the save_upload logic
    subdir = "listings"
    filename = "test_image.jpg"
    
    # Generate key like in save_upload
    ext = filename.rsplit(".", 1)[-1].lower()
    key = f"{subdir}/{uuid.uuid4()}.{ext}"
    print(f"Generated key: {key}")
    
    # Build path
    base = settings.UPLOAD_DIR or "./uploads"
    abs_path = os.path.join(base, key)
    print(f"Full file path: {abs_path}")
    
    # Create directory
    dir_path = os.path.dirname(abs_path)
    print(f"Creating directory: {dir_path}")
    os.makedirs(dir_path, exist_ok=True)
    
    # Create test file content
    test_content = b"This is a test image file content"
    
    # Save file
    try:
        with open(abs_path, "wb") as f:
            f.write(test_content)
        print(f"✅ File written to: {abs_path}")
        
        # Verify file exists and has content
        if os.path.exists(abs_path):
            file_size = os.path.getsize(abs_path)
            print(f"✅ File exists with size: {file_size} bytes")
            
            # Read back content to verify
            with open(abs_path, "rb") as f:
                read_content = f.read()
            
            if read_content == test_content:
                print("✅ File content verified successfully")
            else:
                print("❌ File content does not match")
                
            # Clean up
            os.remove(abs_path)
            print("✅ Test file cleaned up")
        else:
            print("❌ File does not exist after writing")
            
    except Exception as e:
        print(f"❌ Error during file operations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_file_save_test()
