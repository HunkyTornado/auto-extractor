import os
import shutil
import time
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import patoolib

# Define directories
config_file = 'config.json'
dirs = ['Compressed', 'Processing', 'Decompressed', 'Completed']
default_dir = r'K:\D'
directories = {}

# Check if config file exists and load directories if it does
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        directories = json.load(f)

# Ask user for directories if not in config file
for dir_name in dirs:
    if dir_name not in directories:
        directories[dir_name] = input(f"Enter the path for '{dir_name}' directory (default: {default_dir}): ") or default_dir

    # Create directory if it doesn't exist
    os.makedirs(directories[dir_name], exist_ok=True)

# Save directories to config file
with open(config_file, 'w') as f:
    json.dump(directories, f, indent=4)

# Define log file path
log_file = os.path.join(directories['Completed'], 'autounzipper.log')

# Clear previous log file or create a new one
with open(log_file, 'w') as f:
    f.write(f'Autounzipper Log - {datetime.now()}\n\n')

# Function to handle file system events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the event is a file creation and the file is an archive
        if event.is_directory == False and any(event.src_path.lower().endswith(ext) for ext in ('.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2')):
            filename = os.path.basename(event.src_path)
            source_file = os.path.join(directories['Compressed'], filename)
            destination_folder = os.path.join(directories['Decompressed'], os.path.splitext(filename)[0])
            # Move archive file to processing directory
            shutil.move(source_file, directories['Processing'])
            try:
                # Extract archive file
                patoolib.extract_archive(os.path.join(directories['Processing'], filename), outdir=destination_folder)
                # Move archive file to completed directory
                shutil.move(os.path.join(directories['Processing'], filename), directories['Completed'])
                # Log successful extraction
                with open(log_file, 'a') as f:
                    f.write(f'Successfully extracted {filename} to {destination_folder}\n')
            except Exception as e:
                # Log extraction failure
                with open(log_file, 'a') as f:
                    f.write(f'Error extracting {filename}: {str(e)}\n')

# Start watching directory for new archive files
if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directories['Compressed'], recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
