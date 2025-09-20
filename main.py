import os
import shutil
import sys
import ctypes

def replace_files_in_folder():
    """
    Moves existing font files to a 'Fonts.old' backup folder and then replaces them
    with a copy of a specified source file.
    """
    print("--- File Replacer Script ---")
    print("WARNING: This script will MOVE and REPLACE files.")
    print("Please back up your data before proceeding.\n")

    # --- Auto-detect the source file ---
    script_dir = ""
    try:
        # This is the most reliable way when the script is run as a file
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # This is a fallback for environments where __file__ is not defined
        try:
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        except (IndexError, AttributeError):
            # This catches cases where sys.argv is empty or argv[0] is problematic
            print("\n--- CRITICAL ERROR ---")
            print("Could not determine the script's directory.")
            print("This can happen when running in some specialized environments.")
            print("Please try running the script from a standard command line terminal.")
            return # Exit gracefully

    source_folder_name = "PLACE YOUR CUSTOM FONT HERE"
    source_folder_path = os.path.join(script_dir, source_folder_name)

    # Validate the source folder's existence. If it doesn't exist, create it.
    if not os.path.isdir(source_folder_path):
        print(f"\nSource folder '{source_folder_name}' not found. Creating it for you.")
        try:
            os.makedirs(source_folder_path)
            print(f"Successfully created folder: {source_folder_path}")

            # --- Display a message box to the user ---
            title = "Folder Created"
            message = "Made Font Folder. Please put ONE font file in the new folder and re-run the script."
            try:
                # Attempt to show a native Windows message box for a better user experience.
                # 0x40 is the style for MB_ICONINFORMATION.
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            except (AttributeError, NameError):
                # This is a fallback for non-Windows systems or environments where ctypes might fail.
                # It prints a formatted message to the console instead.
                print("\n" + "#" * (len(message) + 4))
                print(f"# {title.upper()} #")
                print(f"# {message} #")
                print("#" * (len(message) + 4))

        except Exception as e:
            print(f"\n--- CRITICAL ERROR ---")
            print(f"Failed to create the source folder due to an error.")
            print(f"Details: {e}")
        return # Exit the script so the user can add the required file.

    # Find all files in the source folder, ignoring subdirectories
    source_files = [f for f in os.listdir(source_folder_path) if os.path.isfile(os.path.join(source_folder_path, f))]

    if len(source_files) == 0:
        print(f"\nError: No file found inside the '{source_folder_name}' folder.")
        print(f"Please place the single file you want to duplicate into this folder.")
        return

    if len(source_files) > 1:
        print(f"\nError: Multiple files found inside the '{source_folder_name}' folder.")
        print("Please ensure there is only ONE file in this folder to be used as the source.")
        return

    # Successfully found exactly one source file
    source_file = os.path.join(source_folder_path, source_files[0])
    print(f"Source file automatically detected: {source_file}\n")

    # Get user input for the target path
    target_folder = input("Enter the full path to the folder containing files you want to replace: ")

    # Validate the target path provided by the user
    if not os.path.isdir(target_folder):
        print(f"\nError: The target folder path does not exist or is not a directory.")
        print(f"Path provided: {target_folder}")
        return
        
    # Check for write permissions in the target folder
    if not os.access(target_folder, os.W_OK):
        print(f"\nError: The script does not have permission to write to the target folder.")
        print(f"Please check the folder permissions for: {target_folder}")
        return

    # Get the absolute path of the currently running script to avoid self-replacement
    try:
        script_path = os.path.abspath(__file__)
    except NameError:
        # This handles cases where the script is run in an environment
        # where __file__ is not defined (e.g., some interactive shells).
        script_path = os.path.abspath(sys.argv[0])


    print("\n--- Confirmation ---")
    print(f"Target Folder: {target_folder}")
    print(f"Source File:   {source_file}")
    print("\nThis action will MOVE existing font files to a 'Fonts.old' subfolder and then replace them with a copy of the source file.")
    
    confirm = input("To confirm this action, type 'YES' and press Enter: ")

    if confirm != 'YES':
        print("\nConfirmation not received. Script cancelled.")
        return

    print("\nStarting replacement process...")
    replaced_count = 0
    skipped_count = 0
    # Define a tuple of common font file extensions (case-insensitive)
    font_extensions = ('.ttf', '.otf', '.woff', '.woff2', '.eot')

    try:
        # Create a backup folder for the old fonts if it doesn't exist
        backup_folder_path = os.path.join(target_folder, "Fonts.old")
        os.makedirs(backup_folder_path, exist_ok=True)
        print(f"Old font files will be moved to: {backup_folder_path}")

        # Iterate over every item in the target folder
        for filename in os.listdir(target_folder):
            original_file_path = os.path.join(target_folder, filename)

            # Check if the item is a file and not the script itself
            if os.path.isfile(original_file_path):
                if original_file_path == script_path:
                    print(f"  - Skipping script file: {filename}")
                    skipped_count += 1
                    continue
                
                # Check if the file has a font extension
                if filename.lower().endswith(font_extensions):
                    backup_file_path_dest = os.path.join(backup_folder_path, filename)
                    
                    print(f"\n  - Processing font file: {filename}")
                    print(f"    - Moving from: '{original_file_path}'")
                    print(f"    -          to: '{backup_file_path_dest}'")
                    shutil.move(original_file_path, backup_file_path_dest)

                    print(f"    - Copying from: '{source_file}'")
                    print(f"    -           to: '{original_file_path}'")
                    shutil.copy2(source_file, original_file_path)
                    
                    print(f"    - SUCCESS: Moved and replaced.")
                    replaced_count += 1
                else:
                    # If it's not a font file, skip it
                    print(f"  - Skipping non-font file: {filename}")
                    skipped_count += 1
            else:
                print(f"  - Skipping directory: {filename}")
                skipped_count += 1


    except Exception as e:
        print(f"\n--- AN ERROR OCCURRED ---")
        print(f"Python Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        print("\nThe process was interrupted. Please check the target folder and its permissions.")
        return

    print("\n--- Process Complete ---")
    print(f"Successfully moved and replaced {replaced_count} font file(s).")
    print(f"Skipped {skipped_count} item(s) (non-fonts, directories, or the script itself).")


if __name__ == "__main__":
    replace_files_in_folder()
    input("\nPress Enter to exit...")

