# BWC Scene Manager version .01

The **BWC Scene Manager** is a Python script designed to help efficiently manage body-worn camera (BWC) footage.  Designed exclusively for usage by the brave souls defending justice in Public Defender's offices all over the world.  The script identifies overlapping video segments (concurrent scenes), exports data into groups/playlists, and detects missing time chunks.

## Features

- Groups videos into concurrent scenes based on overlapping timeframes.
- Generates `.m3u` playlists for each group of concurrent scenes in time series order.
- Exports CSV data with grouped video metadata.
- Detects and exports missing time chunks in CSV format.
- Allows users to choose specific export options through a menu.

## Required Naming Convention

To work correctly, video files need to follow a strict naming format:

```officerFirstName_officerLastName_MM_DD_YYYY_HH_mm_ss_caseNumber.extension```

- `officerFirstName`: The first name of the recording officer (e.g., "John").
- `officerLastName`: The last name of the recording officer (e.g., "Doe").
- `MM`: The two-digit month of the video recording.
- `DD`: The two-digit day of the video recording.
- `YYYY`: The four-digit year of the video recording.
- `HH`: The two-digit hour in 24-hour format.
- `mm`: The two-digit minute.
- `ss`: The two-digit second.
- `caseNumber`: An alphanumeric identifier for the associated case or incident.

### Example

A valid filename following this format:

```John_Doe_05_15_2024_13_45_30_123456789.mp4```

## How to Use the Script

1. **Set Up Environment:**
   - Ensure you have Python installed (version 3.7+ recommended).
   - Install dependencies with:
     ```bash
     pip install moviepy
     ```

2. **Run the Script:**
   - Execute the Python script using:
     ```bash
     python script_name.py
     ```
   - When prompted, enter the directory containing the video files.
   - When prompted, enter an output directory if you choose to.  
   -- Keep in mind that if the input directory is a share, not selecting an output directory will write to the share.  

3. **Select an Option:**
   - The script will present a menu with four options:
     1. Export playlists and related data.
     2. Export missing time chunks data.
     3. Export both playlists and missing chunks data.
     4. Export only `.m3u` playlists.

4. **Check the Output:**
   - Depending on the chosen option, the script will generate `.csv` and `.m3u` files in the directory containing the video files.
   - Review the terminal output to confirm the paths to the generated files.

## Troubleshooting

- Ensure all filenames adhere to the required format.
- If there are errors processing specific files, check the terminal output for error messages.

## Download and Installation

To download and install the executable version of the **BWC Scene Manager**:

1. Navigate to the `distros` directory in this repository.
   - [Direct Link to distros](./distros)

2. Download the appropriate executable file:
   - **Windows:** `bwc_manager.exe`
   - **macOS/Linux:** Please ensure compatibility by testing the script directly via Python.

3. Once downloaded, simply run the executable to start using the program.

## License

This script is provided under this [Custom License Agreement](LICENSE)..  
