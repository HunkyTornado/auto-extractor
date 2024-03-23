import os
import asyncio
import logging
import shutil
import patoolib
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

logging.basicConfig(filename='extraction.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class ArchiveHandler(FileSystemEventHandler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def on_created(self, event):
        if not event.is_directory:
            supported_formats = ['.zip', '.rar', '.7z', '.tar']  # Add more formats as needed
            for ext in supported_formats:
                if event.src_path.endswith(ext):
                    self.queue.put_nowait(event.src_path)

async def move_and_extract_archive(source_path, processing_path, extract_path):
    try:
        shutil.move(source_path, processing_path)
        os.makedirs(extract_path, exist_ok=True)
        patoolib.extract_archive(processing_path, outdir=extract_path)
        logging.info(f"Extracted {processing_path} to {extract_path}")
        os.remove(processing_path)
    except Exception as e:
        logging.error(f"Error processing {source_path}: {e}")

async def process_archives(queue, processing_folder, destination_folder):
    with ThreadPoolExecutor() as executor:
        while True:
            source_path = await queue.get()
            file_name = os.path.basename(source_path)
            processing_path = os.path.join(processing_folder, file_name)
            extract_path = os.path.join(destination_folder, os.path.splitext(file_name)[0])
            await asyncio.get_event_loop().run_in_executor(executor, move_and_extract_archive, source_path, processing_path, extract_path)

def setup_observer(source_folder, event_queue):
    event_handler = ArchiveHandler(event_queue)
    observer = Observer()
    observer.schedule(event_handler, source_folder, recursive=False)
    observer.start()
    return observer

async def main():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        source_folder = config['source_folder']
        processing_folder = config['processing_folder']
        destination_folder = config['destination_folder']
    else:
        source_folder = input("Enter path to compressed folder: ")
        processing_folder = input("Enter path to processing folder: ")
        destination_folder = input("Enter path to decompressed folder: ")
        config = {
            'source_folder': source_folder,
            'processing_folder': processing_folder,
            'destination_folder': destination_folder
        }
        with open(config_file, 'w') as f:
            json.dump(config, f)

    os.makedirs(processing_folder, exist_ok=True)
    os.makedirs(destination_folder, exist_ok=True)

    event_queue = asyncio.Queue()
    observer = setup_observer(source_folder, event_queue)

    workers = [asyncio.create_task(process_archives(event_queue, processing_folder, destination_folder)) for _ in range(4)]  # Adjust number of workers as needed

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    for worker in workers:
        worker.cancel()

if __name__ == "__main__":
    asyncio.run(main())
