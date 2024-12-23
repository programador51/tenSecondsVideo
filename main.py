import os
import subprocess
import random
from tkinter import Tk, filedialog
import shutil

def select_file(title="Select a file"):
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=title)
    return file_path

def select_folder(title="Select a folder"):
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title=title)
    return folder_path

def main():
    # Select input video file
    input_file = select_file("Select the input video file")
    if not input_file:
        print("No input file selected. Exiting.")
        return

    # Select output folder
    output_folder = select_folder("Select the output folder")
    if not output_folder:
        print("No output folder selected. Exiting.")
        return

    # Output file paths
    output_file = os.path.join(output_folder, "preview_video.mp4")

    # Parameters
    num_segments = 5
    segment_duration = 2

    # Get video duration using ffprobe
    try:
        ffprobe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_file
        ]
        duration_output = subprocess.check_output(ffprobe_cmd, text=True)
        video_duration = int(float(duration_output.strip()))
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return

    # Create temporary folder for segments
    temp_folder = os.path.join(output_folder, "temp_segments")
    os.makedirs(temp_folder, exist_ok=True)

    # Generate segments
    segments = []
    for i in range(1, num_segments + 1):
        start_time = random.randint(0, max(0, video_duration - segment_duration))
        segment_file = os.path.join(temp_folder, f"segment_{i}.mp4")
        ffmpeg_cmd = [
            "ffmpeg", "-ss", str(start_time), "-i", input_file, "-t", str(segment_duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", segment_file
        ]
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            segments.append(segment_file)
        except subprocess.CalledProcessError as e:
            print(f"Error generating segment {i}: {e}")
            return

    # Create concatenation file
    segments_list_file = os.path.join(temp_folder, "segments_list.txt")
    with open(segments_list_file, "w") as f:
        for segment in segments:
            f.write(f"file '{segment}'\n")

    # Concatenate segments
    try:
        ffmpeg_concat_cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", segments_list_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-shortest", output_file
        ]
        subprocess.run(ffmpeg_concat_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating segments: {e}")
        return

    # Clean up temporary files
    shutil.rmtree(temp_folder)

    # Open containing folder
    try:
        os.startfile(output_folder)  # Windows
    except AttributeError:
        subprocess.run(["open", output_folder])  # macOS/Linux

    print(f"Video preview created successfully at: {output_file}")

if __name__ == "__main__":
    main()
