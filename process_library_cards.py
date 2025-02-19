import sys
import re
from pathlib import Path

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def parse_library_entries(content):
    lines = content.strip().split('\n')
    entries = {}
    
    def clean_library_name(name):
        # Remove special characters and normalize whitespace
        cleaned = re.sub(r'[^\w\s]', ' ', name)
        return ' '.join(cleaned.split())
    
    def is_library_card(text):
        return bool(re.match(r'^[A-Z0-9]{6,}$', text) or 
                re.match(r'^PACREG\d+$', text) or 
                re.match(r'^\d{10,}$', text))
        
    def is_username(text):
        return bool(re.search(r'[@.]', text) or 
                re.match(r'^[a-zA-Z0-9_]{3,}$', text))
        
    def is_password(text):
        return bool(re.match(r'^\d{4,}$', text) or
                len(text) >= 4 and not is_username(text) and not is_library_card(text))
    
    current_library = None
    current_entry = {'card': None, 'username': None, 'password': None}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_library and any(current_entry.values()):
                if current_library not in entries:
                    entries[current_library] = []
                entries[current_library].append(dict(current_entry))
                current_entry = {'card': None, 'username': None, 'password': None}
            continue
        
        # Identify the type of information
        if is_library_card(line):
            if current_entry['card'] and current_library:
                # Start new entry for same library
                if current_library not in entries:
                    entries[current_library] = []
                entries[current_library].append(dict(current_entry))
                current_entry = {'card': None, 'username': None, 'password': None}
            current_entry['card'] = line
        elif not current_library and len(line.split()) <= 3 and not is_username(line):
            if current_library and any(current_entry.values()):
                if current_library not in entries:
                    entries[current_library] = []
                entries[current_library].append(dict(current_entry))
                current_entry = {'card': None, 'username': None, 'password': None}
            current_library = clean_library_name(line)
        elif is_username(line):
            current_entry['username'] = line
        elif is_password(line):
            current_entry['password'] = line
    
    # Add the last entry
    if current_library and any(current_entry.values()):
        if current_library not in entries:
            entries[current_library] = []
        entries[current_library].append(dict(current_entry))
    
    return entries

def main():
    # File paths
    file1 = Path("/Users/cerinawithasea/Documents/notes/Unclutter Note 2024-08-10 08.10.09.txt")
    file2 = Path("/Users/cerinawithasea/Documents/notes/Unclutter Note 2025-01-27 15.28.54.txt")
    
    # Read and combine content from both files
    content1 = read_file(file1)
    content2 = read_file(file2)
    
    # Parse entries from both files
    try:
        entries = {}
        if content1:
            entries1 = parse_library_entries(content1)
            for lib, items in entries1.items():
                if lib not in entries:
                    entries[lib] = []
                entries[lib].extend(items)
        
        if content2:
            entries2 = parse_library_entries(content2)
            for lib, items in entries2.items():
                if lib not in entries:
                    entries[lib] = []
                entries[lib].extend(items)
    except Exception as e:
        print(f"Error processing entries: {e}")
        return
    
    # Sort entries by library name
    sorted_entries = dict(sorted(entries.items()))
    
    # Print and save formatted output
    output_lines = []
    for library, entries in sorted_entries.items():
        for entry in entries:
            output_lines.append(f"Library: {library}")
            if entry['card']:
                output_lines.append(f"Card: {entry['card']}")
            if entry['username']:
                output_lines.append(f"Username: {entry['username']}")
            if entry['password']:
                output_lines.append(f"Password: {entry['password']}")
            output_lines.append("")

    # Print to console
    print("\n".join(output_lines))

    # Save to file
    with open('library_cards_output.txt', 'w') as f:
        f.write("\n".join(output_lines))

if __name__ == "__main__":
    main()

