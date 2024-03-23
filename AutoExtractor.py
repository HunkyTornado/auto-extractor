import os
import shutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import patoolib

# Define directories
dirA = r'K:\Compressed'
dirB = r'K:\Processing'
dirC = r'K:\Decompressed'
dirD = r'K:\Completed'

# Define log file path
log_file = os.path.join(dirD, 'autounzipper.log')

# Clear previous log file or create a new one
with open(log_file, 'w') as f:
    f.write(f'Autounzipper Log - {datetime.now()}\n\n')

# Function to handle file system events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the event is a file creation and the file is an archive
        if event.is_directory == False and any(event.src_path.lower().endswith(ext) for ext in ('.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2')):
            filename = os.path.basename(event.src_path)
            source_file = os.path.join(dirA, filename)
            destination_folder = os.path.join(dirC, os.path.splitext(filename)[0])
            # Move archive file to processing directory
            shutil.move(source_file, dirB)
            try:
                # Extract archive file
                patoolib.extract_archive(os.path.join(dirB, filename), outdir=destination_folder)
                # Move archive file to completed directory
                shutil.move(os.path.join(dirB, filename), dirD)
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
    observer.schedule(event_handler, path=dirA, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
