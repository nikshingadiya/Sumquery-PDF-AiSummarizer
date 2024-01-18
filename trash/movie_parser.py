import re
import json

def extract_information(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        script_text = file.read()

    # Regular expressions for extracting information
    scene_headings_pattern = re.compile(r'^\s*(INT\.|EXT\.)\s+[A-Z\s-]+ - [A-Z]+\s*$', re.MULTILINE)
    action_lines_pattern = re.compile(r'^\s*([A-Z][A-Z\s]+)\n(.+?)(?=\n[A-Z]+|\Z)', re.MULTILINE | re.DOTALL)
    dialogue_pattern = re.compile(r'^\s*([A-Z]+)\n\s*\((.+?)\)\n(.+?)(?=\n[A-Z]+|\Z)', re.MULTILINE | re.DOTALL)
    transition_pattern = re.compile(r'^\s*(CUT TO:|FADE TO BLACK:|DISSOLVE TO:)\s*$', re.MULTILINE)
    subheaders_pattern = re.compile(r'^\s*(FLASHBACK|MONTAGE)\s*$', re.MULTILINE)
    dual_dialog_pattern = re.compile(r'^\s*\((O\.S\.|V\.O\.)\)\s*$', re.MULTILINE)
    extensions_pattern = re.compile(r'^\s*([A-Z]+)\s*\(CONT\'D\)\s*$', re.MULTILINE)
    parenthetical_extensions_pattern = re.compile(r'^\s*([A-Z]+)\s*\(MORE\)\s*$', re.MULTILINE)
    time_of_day_pattern = re.compile(r'^\s*[A-Z\s-]+ - (DAY|NIGHT)\s*$', re.MULTILINE)

    # Extract information using regular expressions
    scene_headings = re.findall(scene_headings_pattern, script_text)
    action_lines = re.findall(action_lines_pattern, script_text)
    dialogue_lines = re.findall(dialogue_pattern, script_text)
    transitions = list(re.finditer(transition_pattern, script_text))
    subheaders = re.findall(subheaders_pattern, script_text)
    dual_dialog = re.findall(dual_dialog_pattern, script_text)
    extensions = re.findall(extensions_pattern, script_text)
    parenthetical_extensions = re.findall(parenthetical_extensions_pattern, script_text)
    time_of_day = re.findall(time_of_day_pattern, script_text)

    # Organize the extracted data with transitions numbered as keys
    extracted_data = {}

    for idx, transition in enumerate(transitions, start=1):
        transition_number = f'Transition_{idx}'
        transition_data = {'Type': transition.group(1)}

        # Extract information for the current transition using regular expressions
        next_scene_start = transitions[idx].start() if idx < len(transitions) else None
        action_lines_in_transition = re.findall(r'^\s*([A-Z][A-Z\s]+)\n(.+?)(?=\n[A-Z]+|\Z)', script_text[transition.end():next_scene_start], re.MULTILINE | re.DOTALL)
        dialogue_lines_in_transition = re.findall(r'^\s*([A-Z]+)\n\s*\((.+?)\)\n(.+?)(?=\n[A-Z]+|\Z)', script_text[transition.end():next_scene_start], re.MULTILINE | re.DOTALL)

        transition_data['ActionLines'] = [{'Character': char, 'Action': action} for char, action in action_lines_in_transition]
        transition_data['Dialogues'] = [{'Character': char, 'Parenthetical': paren, 'Line': line} for char, paren, line in dialogue_lines_in_transition]

        # Include TimeOfDay information
        time_of_day_in_transition = re.search(time_of_day_pattern, script_text[transition.end():next_scene_start])
        if time_of_day_in_transition:
            transition_data['TimeOfDay'] = time_of_day_in_transition.group(1)

        extracted_data[transition_number] = transition_data

    # Save the extracted data to a JSON file
    with open('extracted_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

# Replace 'AVATAR_JamesCameron.txt' with the path to your movie script text file
extract_information('AVATAR_JamesCameron.txt')
