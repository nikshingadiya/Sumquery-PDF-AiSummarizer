import re
import json

def parse_movie_script(script_text):
    parsed_data = {
        "SceneHeadings": [],
        "ActionLines": [],
        "Characters": [],
        "Dialogue": [],
        "Parentheticals": [],
        "Transitions": [],
        "Subheaders": [],
        "DualDialog": [],
        "Extensions": [],
        "ParentheticalExtensions": [],
        "TimeOfDay": [],
        "SceneNumbers": [],
        "ShotDescriptions": [],
        "ToneAndStyle": [],
        "AdvancedTechniques": [],
        "SymbolicElements": [],
        "ComplexDialogueStructures": [],
        "UniqueFormattingStyles": [],
    }

    scene_heading_pattern = re.compile(r'^\s*(INT\.|EXT\.)\s*\S.*-.*$', re.MULTILINE)
    action_line_pattern = re.compile(r'^\s*([^A-Z\n]+.*)$', re.MULTILINE)
    character_pattern = re.compile(r'^\s*([A-Z]+)\s*.*$', re.MULTILINE)
    dialogue_pattern = re.compile(r'^\s*([A-Z]+)\s*.*\n([\s\S]*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    parenthetical_pattern = re.compile(r'^\s*([A-Z]+)\s*\((.*?)\)\s*.*\n([\s\S]*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    transition_pattern = re.compile(r'^\s*CUT TO:|FADE (?:IN|OUT)\s*$', re.MULTILINE)
    subheader_pattern = re.compile(r'^\s*([A-Z]+)\s*\n(.*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    dual_dialog_pattern = re.compile(r'^\s*([A-Z]+)\s*\((O\.S\.|V\.O\.)\)\s*.*$', re.MULTILINE)
    extension_pattern = re.compile(r'^\s*([A-Z]+)\s*\(CONT\'D\)\s*.*$', re.MULTILINE)
    parenthetical_extension_pattern = re.compile(r'^\s*([A-Z]+)\s*\((CONT\'D)\)\s*.*\n([\s\S]*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    time_of_day_pattern = re.compile(r'^\s*(INT\.|EXT\.)\s*\S.*-\s*(DAY|NIGHT)\s*$', re.MULTILINE)
    scene_number_pattern = re.compile(r'^\s*Scene\s+(\d+)\s*$', re.MULTILINE)
    shot_description_pattern = re.compile(r'^\s*([A-Z]+)\s*.*\n([\s\S]*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    tone_and_style_pattern = re.compile(r'^\s*(.*?)\s*$', re.MULTILINE)
    advanced_techniques_pattern = re.compile(r'(non-linear storytelling|nested flashbacks|unreliable narrators)', re.MULTILINE)
    symbolic_elements_pattern = re.compile(r'(symbolic element.*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    complex_dialogue_structures_pattern = re.compile(r'(complex dialogue structure.*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)
    unique_formatting_styles_pattern = re.compile(r'(unique formatting style.*?)(?=\n[A-Z]+|\Z)', re.MULTILINE)

    # Parse Scene Headings
    parsed_data["SceneHeadings"] = scene_heading_pattern.findall(script_text)

    # Parse Action Lines
    parsed_data["ActionLines"] = action_line_pattern.findall(script_text)

    # Parse Characters
    parsed_data["Characters"] = character_pattern.findall(script_text)

    # Parse Dialogue
    dialogue_matches = dialogue_pattern.findall(script_text)
    for match in dialogue_matches:
        character_name, dialogue = match
        parsed_data["Dialogue"].append({"Character": character_name, "Lines": dialogue.strip()})

    # Parse Parentheticals
    parenthetical_matches = parenthetical_pattern.findall(script_text)
    for match in parenthetical_matches:
        character_name, parenthetical, dialogue = match
        parsed_data["Parentheticals"].append({"Character": character_name, "Parenthetical": parenthetical.strip(), "Lines": dialogue.strip()})

    # Parse Transitions
    parsed_data["Transitions"] = transition_pattern.findall(script_text)

    # Parse Subheaders
    subheader_matches = subheader_pattern.findall(script_text)
    for match in subheader_matches:
        subheader, content = match
        parsed_data["Subheaders"].append({"Subheader": subheader, "Content": content.strip()})

    # Parse Dual Dialog
    dual_dialog_matches = dual_dialog_pattern.findall(script_text)
    for match in dual_dialog_matches:
        character_name, dialog_type = match
        parsed_data["DualDialog"].append({"Character": character_name, "Type": dialog_type})

    # Parse Extensions
    parsed_data["Extensions"] = extension_pattern.findall(script_text)

    # Parse Parenthetical Extensions
    parenthetical_extension_matches = parenthetical_extension_pattern.findall(script_text)
    for match in parenthetical_extension_matches:
        character_name, extension_type, lines = match
        parsed_data["ParentheticalExtensions"].append({"Character": character_name, "ExtensionType": extension_type, "Lines": lines.strip()})

    # Parse Time of Day
    time_of_day_matches = time_of_day_pattern.findall(script_text)
    for match in time_of_day_matches:
        scene_heading, time_of_day = match
        parsed_data["TimeOfDay"].append({"SceneHeading": scene_heading, "TimeOfDay": time_of_day})

    # Parse Scene Numbers
    scene_number_matches = scene_number_pattern.findall(script_text)
    parsed_data["SceneNumbers"] = [{"SceneNumber": int(scene_number)} for scene_number in scene_number_matches]

    # Parse Shot Descriptions
    shot_description_matches = shot_description_pattern.findall(script_text)
    for match in shot_description_matches:
        character_name, description = match
        parsed_data["ShotDescriptions"].append({"Character": character_name, "Description": description.strip()})

    # Parse Tone and Style
    tone_and_style_matches = tone_and_style_pattern.findall(script_text)
    parsed_data["ToneAndStyle"] = [{"ToneAndStyle": tone_and_style} for tone_and_style in tone_and_style_matches]

    # Parse Advanced Techniques
    advanced_techniques_matches = advanced_techniques_pattern.findall(script_text)
    parsed_data["AdvancedTechniques"] = [{"AdvancedTechnique": technique} for technique in advanced_techniques_matches]

    # Parse Symbolic Elements
    symbolic_elements_matches = symbolic_elements_pattern.findall(script_text)
    parsed_data["SymbolicElements"] = [{"SymbolicElement": element} for element in symbolic_elements_matches]

    # Parse Complex Dialogue Structures
    complex_dialogue_structures_matches = complex_dialogue_structures_pattern.findall(script_text)
    parsed_data["ComplexDialogueStructures"] = [{"ComplexDialogueStructure": structure} for structure in complex_dialogue_structures_matches]

    # Parse Unique Formatting Styles
    unique_formatting_styles_matches = unique_formatting_styles_pattern.findall(script_text)
    parsed_data["UniqueFormattingStyles"] = [{"UniqueFormattingStyle": style} for style in unique_formatting_styles_matches]

    return parsed_data

# Example usage:
with open('AVATAR_JamesCameron.txt', 'r', encoding='utf-8') as file:
    movie_script_text = file.read()

parsed_movie_script = parse_movie_script(movie_script_text)

# Save parsed data to a JSON file
with open('parsed_movie_script.json', 'w', encoding='utf-8') as json_file:
    json.dump(parsed_movie_script, json_file, ensure_ascii=False, indent=2)
