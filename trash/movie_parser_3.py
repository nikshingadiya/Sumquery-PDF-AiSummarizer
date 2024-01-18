import re
import json

def extract_information(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        script_text = file.read()

    # Regular expressions for extracting information
    title_page_pattern = re.compile(r'^Title:(.+?)(?=(?:\n[A-Z\s]+:|\Z))', re.MULTILINE | re.DOTALL)
    scene_pattern = re.compile(r'^\s*(INT\.|EXT\.)\s+([A-Z\s-]+ - [A-Z]+)\s*(DAY|NIGHT|Optional)?\s*$(.*?)^(?=\s*(INT\.|EXT\.)|\Z)', re.MULTILINE | re.DOTALL)

    # Extract information using regular expressions
    title_page_match = re.search(title_page_pattern, script_text)
    scenes = re.finditer(scene_pattern, script_text)

    # Organize the extracted data following the provided hierarchy
    extracted_data = {
        "Title Page": {
            "Title": title_page_match.group(1).strip() if title_page_match else "Untitled",
            "Writer": "Your Name",
            "Contact Information": "Your Contact Information",
        },
        "Scenes": []
    }

    for scene_match in scenes:
        scene_data = {
            "Type": scene_match.group(1),
            "Location": scene_match.group(2).strip() if scene_match.group(2) else "Unknown Location",
            "Time of Day": scene_match.group(3),
            "Action Description": scene_match.group(4).strip(),
            "Character Cues": {},
            "Dialogue": {},
            "Transitions": None,
            "Extensions": None,
        }

        # Check if group(5) is not None before applying regular expressions
        if scene_match.group(5) is not None:
            # Extract character cues
            character_cues_pattern = re.compile(r'^\s*([A-Z]+)\s*(\([^)]+\))?\s*$', re.MULTILINE)
            character_cues = re.findall(character_cues_pattern, scene_match.group(5))

            for character, parenthetical in character_cues:
                scene_data["Character Cues"][character] = parenthetical

            # Extract dialogue
            dialogue_pattern = re.compile(r'^\s*([A-Z]+)\s*(\([^)]+\))?\n\s*(.+?)(?=\s*[A-Z]+\s*\(|\Z)', re.MULTILINE | re.DOTALL)
            dialogues = re.findall(dialogue_pattern, scene_match.group(5))

            for character, parenthetical, line in dialogues:
                scene_data["Dialogue"][character] = {
                    "Lines": line.strip(),
                    "Parentheticals": parenthetical,
                }

            # Extract transitions and extensions
            transitions_pattern = re.compile(r'^\s*(CUT TO:|FADE (?:IN|OUT):|DISSOLVE TO:|CUT BACK TO:)\s*$', re.MULTILINE)
            extensions_pattern = re.compile(r'^\s*([A-Z]+)\s*\(CONT\'D\)\s*$', re.MULTILINE)

            transitions = re.search(transitions_pattern, scene_match.group(5))
            extensions = re.search(extensions_pattern, scene_match.group(5))

            scene_data["Transitions"] = transitions.group(1) if transitions else None
            scene_data["Extensions"] = extensions.group(1) if extensions else None

        extracted_data["Scenes"].append(scene_data)

    # Save the extracted data to a JSON file
    with open('extracted_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

# Replace 'AVATAR_JamesCameron.txt' with the path to your movie script text file
extract_information('AVATAR_JamesCameron.txt')
