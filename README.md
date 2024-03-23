# Auto Extractor

The Auto Extractor is a Python script designed to automate the extraction of compressed archive files in the background as a Windows service. It monitors a specified folder for newly created archive files, extracts their contents, and moves the extracted files to a destination folder. Supported archive formats include ZIP, RAR, 7Z, and TAR, making it versatile for various compression needs.

## Motive

Many tasks require extracting compressed files continuously in the background, such as processing incoming data or managing archived content. The Archive Extractor simplifies this process by running as a Windows service, ensuring continuous operation without manual intervention.

## Key Features

- **Background Service:** Runs as a Windows service, allowing continuous extraction of compressed files without user intervention.
- **Automatic Extraction:** Monitors a designated folder for new archive files and automatically extracts them upon detection.
- **Multi-format Support:** Supports popular archive formats including ZIP, RAR, 7Z, and TAR, providing flexibility for different compression requirements.
- **Parallel Processing:** Utilizes asynchronous and parallel processing techniques to efficiently handle multiple archive extractions simultaneously, enhancing performance.
- **Configuration Management:** Offers user-friendly configuration setup through a JSON file, allowing users to specify the source, processing, and destination folders for seamless integration into existing workflows.
- **Logging and Error Handling:** Implements comprehensive logging functionality to track extraction operations and handle errors gracefully, ensuring smooth execution and easy troubleshooting.

## Usage

1. Clone the repository:
```git clone https://github.com/hunkytornado/auto-extractor.git```

2. Navigate to the project directory:
```cd auto-extractor```

3. Install dependencies:
```pip install -r requirements.txt```

4. Install NSSM (Non-Sucking Service Manager):

- Download NSSM from the [NSSM releases page](https://nssm.cc/download) and extract the zip file.
- Open a command prompt window and navigate to the directory where NSSM was extracted.

5. Install the Python script as a Windows service using NSSM:
```nssm install "name-of-your-service" "directory-to-the.py"```

Replace `"name-of-your-service"` with the desired name for your service and `"directory-to-the.py"` with the path to your Python script file.

## Configuration

The script uses a `config.json` file for configuration. On the first launch, the script prompts the user to input the paths to the compressed, processing, and decompressed folders. These paths are then stored in the `config.json` file for future use.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- This project uses the [watchdog](https://pypi.org/project/watchdog/) library for monitoring file system events.
- Thanks to the [patool](https://pypi.org/project/patool/) library for handling archive extraction.

## Authors

- [HunkyTornado](https://github.com/HunkyTornado)




