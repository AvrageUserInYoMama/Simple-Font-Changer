import os
import shutil
import sys

def undo_font_replacement():
    """
    Restores original font files from the 'Fonts.old' backup folder
    to their original location, overwriting the replaced files.
    """
    print("--- Undo Font Replacement Script ---")
    print("This script will restore the original fonts from the 'Fonts.old' backup folder.\n")

    # Get user input for the target path where the original script was run
    target_folder = input("Enter the folder you want to fix: ")

    # Validate the target path provided by the user
    if not os.path.isdir(target_folder):
        print(f"\nError: The specified folder does not exist or is not a directory.")
        print(f"Path provided: {target_folder}")
        return

    # Define and validate the backup folder path
    backup_folder_path = os.path.join(target_folder, "Fonts.old")
    if not os.path.isdir(backup_folder_path):
        print(f"\nError: The backup folder 'Fonts.old' was not found in the specified directory.")
        print(f"Looked for it at: {backup_folder_path}")
        print("There are no changes to undo.")
        return

    # Find the font files to restore
    files_to_restore = [f for f in os.listdir(backup_folder_path) if os.path.isfile(os.path.join(backup_folder_path, f))]

    if not files_to_restore:
        print("\nFound the 'Fonts.old' folder, but it is empty. Nothing to restore.")
        return

    print("\n--- Confirmation ---")
    print(f"Target Folder: {target_folder}")
    print(f"Backup Folder: {backup_folder_path}")
    print(f"\nThis action will restore {len(files_to_restore)} file(s) from the backup folder, overwriting the current fonts.")
    
    confirm = input("To confirm this action, type 'YES' and press Enter: ")

    if confirm != 'YES':
        print("\nConfirmation not received. Script cancelled.")
        return

    print("\nStarting restoration process...")
    restored_count = 0

    try:
        # Iterate over every file in the backup folder
        for filename in files_to_restore:
            backup_file_path = os.path.join(backup_folder_path, filename)
            original_destination_path = os.path.join(target_folder, filename)
            
            # Move the file from 'Fonts.old' back to the parent directory
            shutil.move(backup_file_path, original_destination_path)
            print(f"  - Restored: {filename}")
            restored_count += 1

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("The process may have been interrupted. Please check the target folder.")
        return

    print("\n--- Restoration Complete ---")
    print(f"Successfully restored {restored_count} font file(s).")
    
    # Ask the user if they want to remove the now-empty backup folder
    try:
        if not os.listdir(backup_folder_path): # Check if the directory is empty
             cleanup_confirm = input("\nThe 'Fonts.old' folder is now empty. Would you like to remove it? (y/n): ")
             if cleanup_confirm.lower() == 'y':
                 os.rmdir(backup_folder_path)
                 print(f"Successfully removed the empty 'Fonts.old' folder.")
    except Exception as e:
        print(f"\nCould not remove the 'Fonts.old' folder. Error: {e}")


if __name__ == "__main__":
    undo_font_replacement()

