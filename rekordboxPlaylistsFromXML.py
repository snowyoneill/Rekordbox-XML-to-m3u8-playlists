import xml.etree.ElementTree as ET
import os
import urllib.parse
import sys

# Check if the XML file name is provided as a command-line argument
if len(sys.argv) != 4:
    print("Usage: python rekordboxPlaylistsFromXML.py <XML_file_name> <src_path> <dst_path>")
    sys.exit(1)

src_path = 'file://localhost/E:/'
dst_path = 'primary/Music/'

# Get the XML file name from the command-line argument
xml_file_name = sys.argv[1]
src_path = sys.argv[2]
dst_path = sys.argv[3]

# Parse the XML file
tree = ET.parse(xml_file_name)
root = tree.getroot()

# Create a dictionary to store track information
tracks = {}

# Iterate through the <COLLECTION> section to extract track information
for track_elem in root.find(".//COLLECTION").iter('TRACK'):
    track_id = track_elem.get('TrackID')
    track_name = track_elem.get('Name')
    track_artist = track_elem.get('Artist')
    location = track_elem.get('Location')

    location = urllib.parse.unquote(location)

    # Store track information in the dictionary
    tracks[track_id] = {
        'name': track_name,
        'artist': track_artist,
        'location': location
    }


# Create a function to recursively create subfolders
def create_subfolders(node, current_path=''):
    for child in node:
        if child.tag == 'NODE':
            node_type = int(child.get('Type', 0))
            node_name = child.get('Name', 'Untitled')

            if node_type == 0:
                # Create a folder subdirectory
                subfolder_path = os.path.join(current_path, node_name)
                os.makedirs(subfolder_path, exist_ok=True)
                create_subfolders(child, current_path=subfolder_path)
            elif node_type == 1:
                # Create an M3U8 file for the playlist
                m3u8_filename = f'{node_name}.m3u8'
                # Remove any forward slashes from playlist names. Cannot write to disk without doing this.
                m3u8_filename = m3u8_filename.replace('/', '_')
                m3u8_path = os.path.join(current_path, m3u8_filename)
                print(m3u8_path)
                with open(m3u8_path, 'w') as m3u8_file:
                    for track_key_elem in child.iter('TRACK'):
                        track_key = track_key_elem.get('Key')
                        # print("track_key" + track_key)
                        if track_key in tracks:
                            # Write the track information to the M3U8 file
                            track_info = tracks[track_key]
                            # Update the location to work for android file system
                            track_location = track_info['location'].replace(src_path, dst_path)
                            m3u8_file.write(f'#EXTINF:-1,{track_info["artist"]} - {track_info["name"]}\n')
                            m3u8_file.write(f'{track_location}\n')

# Find the root node for PLAYLISTS
playlists_node = root.find(".//PLAYLISTS")

# Start creating subfolders and M3U8 files
create_subfolders(playlists_node)

print("M3U8 files and subfolders created successfully!")