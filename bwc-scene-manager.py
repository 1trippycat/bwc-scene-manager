import os
import re
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from moviepy.editor import VideoFileClip
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import openpyxl
import sys

# Define the type hint for the video dictionary
VideoType = Dict[str, Any]


# Function to get a secure resource path
def resource_path(relative_path):
    # Get the absolute path to a resource,
    # compatible with PyInstaller or development.
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


# Function to read and print the ASCII art banner
def display_ascii_art():
    banner_path = resource_path(os.path.join("assets", "banner.txt"))
    if os.path.exists(banner_path) and os.path.isfile(banner_path):
        with open(banner_path, 'r', encoding='utf-8') as file:
            ascii_art = file.read()
        print(ascii_art)
    else:
        print("Banner not found!")


# Display the banner before menu selection
display_ascii_art()


# Function to get the file size
def get_file_size(file_path: str) -> int:
    """Get the file size of a video file in bytes."""
    return os.path.getsize(file_path)


# Function to export playlist and related data
def export_playlists_and_related_data(videos: List[VideoType], worksheet):
    """Export playlist and related data to the specified Excel worksheet."""
    print("Exporting playlists and related data...")
    fieldnames = ['file_name', 'first_name', 'last_name', 'case_number',
                  'start_time', 'end_time', 'duration', 'file_size', 'group']
    worksheet.append(fieldnames)  # Write the header

    for video in videos:
        worksheet.append([
            video['file_name'], video['first_name'], video['last_name'],
            video['case_number'], str(video['start_time']),
            str(video['end_time']), int(video['duration']),
            int(video['file_size']), int(video['group'])
        ])
    print("Playlists and related data exported.")


# Function to export missing time chunks
def export_missing_time_chunks(missing_chunks: List[Dict[str, Any]],
                               worksheet):
    """Export missing time chunks to the specified Excel worksheet."""
    print("Exporting missing time chunks data...")
    fieldnames = ['first_name', 'last_name', 'gap_start', 'gap_end',
                  'gap_duration_seconds']
    worksheet.append(fieldnames)  # Write the header

    for chunk in missing_chunks:
        worksheet.append([
            chunk['first_name'], chunk['last_name'],
            str(chunk['gap_start']), str(chunk['gap_end']),
            int(chunk['gap_duration_seconds'])
        ])
    print("Missing time chunks data exported.")


# Function to copy files concurrently
def copy_file(src_path: str, dest_path: str):
    """Copy a file from src_path to dest_path using shutil."""
    shutil.copy2(src_path, dest_path)


# Function to export .m3u playlists
def export_m3u_playlists(group_playlists: Dict[int, List[Dict[str, str]]],
                         input_directory: str,
                         output_directory: str,
                         organize_files: bool = False):
    # Export .m3u playlists for each concurrent group and optionally organize
    # files into subfolders.
    print("Exporting concurrent scene .m3u playlists...")
    for group_number, videos in group_playlists.items():
        case_number = videos[0]['case_number'] if videos else 'unknown_case'
        m3u_filename = f"{case_number}_concurrentScene-{group_number}.m3u"
        m3u_path = os.path.join(output_directory, m3u_filename)

        # Write the .m3u playlist file
        with open(m3u_path, 'w', encoding='utf-8') as m3u_file:
            m3u_file.write("#EXTM3U\n")
            for video in videos:
                video_path = os.path.join(input_directory, video['file_name'])
                m3u_file.write(
                    f"#EXTINF:{int(video['duration'])},{video['file_name']}\n"
                    f"{video_path}\n"
                )

        print(f".m3u playlist created: {m3u_path}")

        # If organizing files, copy them to subfolders
        if organize_files:
            subfolder = os.path.join(output_directory,
                                     os.path.splitext(m3u_filename)[0])
            os.makedirs(subfolder, exist_ok=True)

            print(f"Copying files for group {group_number} to: {subfolder}")

            # Create a thread pool and monitor progress
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                progress_bar = tqdm(total=len(videos),
                                    desc=f"Group {group_number}")

                # Submit all copying tasks
                for video in videos:
                    src_path = os.path.join(input_directory,
                                            video['file_name'])
                    dest_path = os.path.join(subfolder,
                                             video['file_name'])
                    futures.append(executor.submit(copy_file,
                                                   src_path,
                                                   dest_path))

                # Monitor completion of futures
                for future in futures:
                    future.result()  # Ensure task completes
                    progress_bar.update(1)  # Update progress bar

                progress_bar.close()


# Menu options for exporting data
print("\nSelect an option:")
print("1. Generate Report Data")
print("2. Generate Playlists")
print("3. Both (Generate Report Data and Playlists)")

# Read user choice
choice = input("\nEnter your choice (1, 2, or 3): ").strip()

# Prompt for the directory containing the video files after menu selection
video_folder_msg = "Enter the directory containing the clips: "
video_folder = input(video_folder_msg).strip()
if not os.path.isdir(video_folder):
    print(f"Invalid directory: {video_folder}")
    exit(1)

# Prompt for a custom output directory (optional)
output_dir_msg = "Enter a custom output directory (leave blank to use input): "
output_dir = input(output_dir_msg).strip()
if output_dir and not os.path.isdir(output_dir):
    os.makedirs(output_dir, exist_ok=True)

if not output_dir:
    output_dir = video_folder
    print(f"Using default output directory: {output_dir}")
else:
    print(f"Using custom output directory: {output_dir}")

# Ask the user if they want to organize files into subfolders
organize_files_msg = "Move concurrent scene files into subfolders (y/n)?: "
organize_files = input(organize_files_msg).strip().lower() == 'y'

# Generate a timestamp in the format YYYYMMDD_HHMMSS
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set the output file path for the Excel workbook, incorporating the timestamp
output_excel = os.path.join(output_dir, f'bwc_metadata_{timestamp}.xlsx')
workbook = openpyxl.Workbook()

# Ensure the active worksheet is not None before modifying
playlist_ws = workbook.active
if playlist_ws is not None:
    playlist_ws.title = "Metadata"
else:
    print("Error: Failed to create the 'Metadata' worksheet.")

# Create the "Missing Time Chunks" worksheet and verify it's not None
missing_chunks_ws = workbook.create_sheet("Missing Time Chunks")
if missing_chunks_ws is not None:
    print("Successfully created 'Missing Time Chunks' worksheet.")
else:
    print("Error: Failed to create the 'Missing Time Chunks' worksheet.")

# Regular expression pattern to match and capture data from the filename
pattern = re.compile(
    r"""
    (?P<first_name>[^_]+)    # First name, non-underscore characters
    _                        # Underscore separator
    (?P<last_name>[^_]+)     # Last name, non-underscore characters
    _                        # Underscore separator
    (?P<month>\d{2})         # Month, two digits
    _                        # Underscore separator
    (?P<day>\d{2})           # Day, two digits
    _                        # Underscore separator
    (?P<year>\d{4})          # Year, four digits
    _                        # Underscore separator
    (?P<hour>\d{2})          # Hour, two digits
    _                        # Underscore separator
    (?P<minute>\d{2})        # Minute, two digits
    _                        # Underscore separator
    (?P<second>\d{2})        # Second, two digits
    _                        # Underscore separator
    (?P<case_number>[^.]+)   # Case number, all characters until the period
    \.[a-zA-Z0-9]+           # File extension after the period
    """,
    re.VERBOSE
)

# Structure to hold video information
videos: List[VideoType] = []

# Read video files and parse their metadata
print("Reading video files and collecting data...")
for video_file in os.listdir(video_folder):
    video_path = os.path.join(video_folder, video_file)

    if not os.path.isfile(video_path):
        continue

    # Match the filename against the pattern and extract data
    match = pattern.match(video_file)
    if match:
        data = match.groupdict()

        # Construct the start time
        start_time_str = (
            f"{data['year']}-{data['month']}-{data['day']} "
            f"{data['hour']}:{data['minute']}:{data['second']}"
        )
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

        # Load video file to determine its duration
        try:
            with VideoFileClip(video_path) as video:
                duration = int(video.duration)  # Cast to int explicitly
        except Exception as e:
            print(f"Error processing {video_file}: {e}")
            continue

        # Calculate the end time and ensure it's a `datetime` object
        end_time = start_time + timedelta(seconds=duration)

        # Obtain file size
        file_size = get_file_size(video_path)

        videos.append({
            'file_name': video_file,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'case_number': data['case_number'],
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'file_size': file_size,
            'group': None  # Will be assigned later
        })

# Sort videos by `start_time`, explicitly cast to `datetime` if needed
videos.sort(key=lambda x: x['start_time'])

# Assign group numbers to overlapping videos
current_group = 1
for i, current in enumerate(videos):
    if i == 0:
        current['group'] = current_group
        continue

    previous = videos[i - 1]

    # Check for overlap with the previous video in sorted order
    if current['start_time'] <= previous['end_time']:
        current['group'] = previous['group']
    else:
        current_group += 1
        current['group'] = current_group

# Create a dictionary to hold video groups
group_playlists: Dict[int, List[VideoType]] = {}
for video in videos:
    group = video['group']
    if group not in group_playlists:
        group_playlists[group] = []
    group_playlists[group].append(video)

# Identify missing chunks per officer
officer_videos: Dict[str, List[VideoType]] = {}
for video in videos:
    officer_key = f"{video['first_name']}_{video['last_name']}"
    if officer_key not in officer_videos:
        officer_videos[officer_key] = []
    officer_videos[officer_key].append(video)


missing_chunks: List[Dict[str, Any]] = []
for officer_key, officer_clips in officer_videos.items():
    for i in range(1, len(officer_clips)):
        prev_clip = officer_clips[i - 1]
        current_clip = officer_clips[i]

        # Calculate the time gap between consecutive clips
        gap = current_clip['start_time'] - prev_clip['end_time']
        if gap.total_seconds() > 0:
            missing_chunks.append({
                'first_name': prev_clip['first_name'],
                'last_name': prev_clip['last_name'],
                'gap_start': prev_clip['end_time'],
                'gap_end': current_clip['start_time'],
                'gap_duration_seconds': int(gap.total_seconds())
            })

# Perform the selected operation based on the user's choice
if choice == '1':
    export_playlists_and_related_data(videos, playlist_ws)
    export_missing_time_chunks(missing_chunks, missing_chunks_ws)
elif choice == '2':
    export_m3u_playlists(group_playlists,
                         video_folder,
                         output_dir,
                         organize_files)
elif choice == '3':
    export_playlists_and_related_data(videos, playlist_ws)
    export_missing_time_chunks(missing_chunks, missing_chunks_ws)
    export_m3u_playlists(group_playlists,
                         video_folder,
                         output_dir,
                         organize_files)
else:
    print("Invalid choice. Exiting.")

# Save the Excel workbook with the exported data
workbook.save(output_excel)
print(f"Data exported to {output_excel}.")
