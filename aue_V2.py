import os
import shutil
import time
import logging
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import patoolib
from zipfile import ZipFile, BadZipFile

# Define directories
dirA = r'K:\Compressed'
dirB = r'K:\Processing'
dirC = r'K:\Decompressed'
dirD = r'K:\Completed'

# Configure logging
log_file = os.path.join(dirD, 'autounzipper.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

def wait_for_file_stability(file_path, check_interval=5, stable_period=10):
    """Wait until file size remains constant for specified period."""
    logger.info(f"Monitoring file stability: {file_path}")
    last_size = -1
    stable_time = 0
    while stable_time < stable_period:
        try:
            current_size = os.path.getsize(file_path)
            if current_size == last_size:
                stable_time += check_interval
            else:
                last_size = current_size
                stable_time = 0
            time.sleep(check_interval)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
    return True

def is_archive_complete(file_path):
    """Check if archive file is complete and valid."""
    if file_path.lower().endswith('.zip'):
        try:
            with ZipFile(file_path) as zf:
                if zf.testzip() is not None:
                    logger.error(f"ZIP file contains errors: {file_path}")
                    return False
            return True
        except BadZipFile:
            logger.error(f"Invalid ZIP file: {file_path}")
            return False
    # For other formats, rely on extraction to validate
    return True

class ArchiveHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and self.is_archive_file(event.src_path):
            logger.info(f"New archive detected: {event.src_path}")
            threading.Thread(target=self.process_archive, args=(event.src_path,)).start()

    def is_archive_file(self, path):
        return any(path.lower().endswith(ext) for ext in (
            '.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2'
        ))

    def process_archive(self, src_path):
        try:
            # Wait until file transfer completes
            if not wait_for_file_stability(src_path):
                return

            # Move to processing directory
            filename = os.path.basename(src_path)
            processing_path = os.path.join(dirB, filename)
            shutil.move(src_path, processing_path)
            logger.info(f"Moved to processing: {processing_path}")

            # Validate archive integrity
            if not is_archive_complete(processing_path):
                logger.error(f"Skipping incomplete archive: {processing_path}")
                return

            # Create output directory
            output_dir = os.path.join(dirC, os.path.splitext(filename)[0])
            os.makedirs(output_dir, exist_ok=True)

            # Extract archive
            patoolib.extract_archive(processing_path, outdir=output_dir)
            logger.info(f"Successfully extracted to: {output_dir}")

            # Move to completed directory
            completed_path = os.path.join(dirD, filename)
            shutil.move(processing_path, completed_path)
            logger.info(f"Moved to completed: {completed_path}")

        except Exception as e:
            logger.error(f"Error processing {src_path}: {str(e)}", exc_info=True)

def main():
    # Ensure directories exist
    for dir in [dirA, dirB, dirC, dirD]:
        os.makedirs(dir, exist_ok=True)

    event_handler = ArchiveHandler()
    observer = Observer()
    observer.schedule(event_handler, path=dirA, recursive=False)
    observer.start()
    logger.info("Started monitoring directory: " + dirA)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopped monitoring due to keyboard interrupt")
    observer.join()

if __name__ == "__main__":
    main()