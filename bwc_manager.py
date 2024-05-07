import os
import csv
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from moviepy.editor import VideoFileClip

# Define the type hint for the video dictionary
VideoType = Dict[str, Any]


def export_playlists_and_related_data(videos: List[VideoType],
                                      output_csv: str):
    """Exports playlist and related data to the specified CSV file."""
    print("Exporting playlists and related data...")
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'file_name', 'first_name', 'last_name', 'case_number',
            'start_time', 'end_time', 'duration', 'group'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            writer.writerow({
                'file_name': video['file_name'],
                'first_name': video['first_name'],
                'last_name': video['last_name'],
                'case_number': video['case_number'],
                'start_time': str(video['start_time']),
                'end_time': str(video['end_time']),
                'duration': int(video['duration']),
                'group': int(video['group'])
            })
    print(f"Playlists and related data exported to {output_csv}")


def export_missing_time_chunks(missing_chunks: List[Dict[str, Any]],
                               output_csv: str):
    """Exports missing time chunks to the specified CSV file."""
    print("Exporting missing time chunks data...")
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['first_name',
                      'last_name',
                      'gap_start',
                      'gap_end',
                      'gap_duration_seconds']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for chunk in missing_chunks:
            writer.writerow(chunk)
    print(f"Missing time chunks data exported to {output_csv}")


def export_m3u_playlists(group_playlists: Dict[int, List[VideoType]],
                         directory: str):
    """Exports .m3u playlists for each concurrent group."""
    print("Exporting concurrent scene .m3u playlists...")
    for group_number, videos in group_playlists.items():
        case_number = videos[0]['case_number'] if videos else 'unknown_case'
        m3u_filename = f"{case_number}_concurrentScene-{group_number}.m3u"
        m3u_path = os.path.join(directory, m3u_filename)

        with open(m3u_path, 'w', encoding='utf-8') as m3u_file:
            m3u_file.write("#EXTM3U\n")
            for video in videos:
                video_path = os.path.join(directory, video['file_name'])
                m3u_file.write(
                    f"#EXTINF:{int(video['duration'])},{video['file_name']}\n"
                    f"{video_path}\n"
                )
        print(f".m3u playlist created: {m3u_path}")


# Prompt for the directory containing the video files
video_folder_msg = "Enter the directory containing the video files: "
video_folder = input(video_folder_msg).strip()
if not os.path.isdir(video_folder):
    print(f"Invalid directory: {video_folder}")
    exit(1)

# Prompt for a custom output directory (optional)
output_dir_msg = "Enter a custom output directory (leave blank to use input):"
output_dir = input(output_dir_msg).strip()
if output_dir and os.path.isdir(output_dir):
    print(f"Using custom output directory: {output_dir}")
else:
    output_dir = video_folder
    print(f"Using default output directory: {output_dir}")

# Set the output file paths to the output directory
output_csv = os.path.join(output_dir, 'video_data_with_groups.csv')
missing_chunks_csv = os.path.join(output_dir, 'missing_time_chunks.csv')

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
    (?P<case_number>.*)      # Case number, any remaining characters
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

        videos.append({
            'file_name': video_file,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'case_number': data['case_number'],
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
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

        gap = current_clip['start_time'] - prev_clip['end_time']
        if gap.total_seconds() > 0:
            missing_chunks.append({
                'first_name': prev_clip['first_name'],
                'last_name': prev_clip['last_name'],
                'gap_start': prev_clip['end_time'],
                'gap_end': current_clip['start_time'],
                'gap_duration_seconds': int(gap.total_seconds())
            })

# Menu options for exporting data
print("\nSelect an option:")
print("1. Export playlists and related data")
print("2. Export missing time chunks data")
print("3. Export both")
print("4. Export .m3u playlists only")

choice = input("\nEnter your choice (1, 2, 3, or 4): ").strip()

if choice == '1':
    export_playlists_and_related_data(videos, output_csv)
elif choice == '2':
    export_missing_time_chunks(missing_chunks, missing_chunks_csv)
elif choice == '3':
    export_playlists_and_related_data(videos, output_csv)
    export_missing_time_chunks(missing_chunks, missing_chunks_csv)
    export_m3u_playlists(group_playlists, output_dir)
elif choice == '4':
    export_m3u_playlists(group_playlists, output_dir)
else:
    print("Invalid choice. Exiting.")
