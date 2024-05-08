# BWC Scene Manager

The **BWC Scene Manager** is a Python script designed to help efficiently manage body-worn camera (BWC) footage. This tool is designed exclusively for the Colorado Public Defender's office but other public defenders offices are free to use it.  See the license for specific license information if you are not a public defender office.  The tool is meant to efficiencty manage body worn camera footage.   It  identifies overlapping video segments (concurrent scenes), exports data into groups/playlists, and detects missing time chunks.

## Features

- Groups videos into concurrent scenes based on overlapping timeframes.
- Generates `.m3u` playlists for each group of concurrent scenes in time series order.
- Exports Excel data with grouped video metadata.
- Detects and exports missing time chunks in an Excel worksheet.
- Optionally organizes video files into subfolders based on concurrent scene groups for subsequent discovery organization.

## Required Naming Convention

To work correctly, video files need to follow a strict naming format:

```officerFirstName_officerLastName_MM_DD_YYYY_HH_mm_ss_caseNumber.fileExtension```

- `officerFirstName`: The first name of the recording officer (e.g., "John").
- `officerLastName`: The last name of the recording officer (e.g., "Doe").
- `MM`: The two-digit month of the video recording.
- `DD`: The two-digit day of the video recording.
- `YYYY`: The four-digit year of the video recording.
- `HH`: The two-digit hour in 24-hour format.
- `mm`: The two-digit minute.
- `ss`: The two-digit second.
- `caseNumber`: An alphanumeric identifier for the associated case or incident.

*Got a different file naming convention than what the 4th District of Colorado is using and want it added to Body Warn Camera Scene Manager?  Post a new issue and I'll get it added for you as soon as I can.*

### Example

A valid filename following this format:

```John_Doe_05_15_2024_13_45_30_123456789.mp4```

## How to Use the Script

1. **Set Up Environment:**
   - Ensure you have Python installed (version 3.7+ recommended).
   - Install dependencies with:

     ```bash
     pip install moviepy openpyxl tqdm
     ```

2. **Run the Script:**
   - Execute the Python script using:

     ```bash
     python script_name.py
     ```

   - When prompted, enter the directory containing the video files.
   - Optionally, provide a custom output directory.  
   -- No original input files are moved or altered.
   -- Make sure you have enough space for the files written to the output directory.
   -- If the input directory is a network share, not specifying an output directory will write to the share.

3. **Select an Option:**
   - The script will present a menu with three options:
     1. Generate Report Data.
     2. Generate Playlists.
     3. Both (Generate Report Data and Playlists).

4. **Check the Output:**
   - Depending on your selection, the script will generate `.xlsx` (Excel) and `.m3u` files in the output directory.
   - Review the terminal output to confirm the paths to the generated files.

## Troubleshooting

- Ensure all filenames adhere to the required format.
- If errors occur with specific files, check the terminal output for error messages.

## Download and Installation

To download and install the **BWC Scene Manager**:

1. Navigate to the Releases tab of this repository.
2. Download the appropriate executable file:
3. Once downloaded, simply run the executable to start using the program.

## Build Instructions

To create a standalone executable using PyInstaller, follow these steps:

1. **Install PyInstaller:**
   - If you haven't already installed it, run:

     ```bash
     pip install pyinstaller
     ```

2. **Build with PyInstaller:**
   - Run PyInstaller with your script file to generate the executable:

     ```bash
     pyinstaller --onefile bwc-scene-manager.py
     ```

3. **Find the Executable:**
   - The executable will be created in the `dist` directory under your project folder.

4. **Test the Executable:**
   - Double-check the executable to ensure it works as expected.

## License

This script is provided under this [Custom License Agreement](LICENSE).
