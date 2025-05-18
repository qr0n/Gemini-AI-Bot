import os
import shutil


def delete_pycache(directory):
    """Recursively deletes all __pycache__ directories in the given directory."""
    for root, dirs, files in os.walk(directory, topdown=False):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            print(f"Found: {pycache_path}")  # Debugging print
            try:
                shutil.rmtree(pycache_path)
                print(f"Deleted: {pycache_path}")
            except Exception as e:
                print(f"Error deleting {pycache_path}: {e}")


# Example usage
delete_pycache(os.getcwd())
