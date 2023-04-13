import sqlite3
import fnmatch
import os

def find_localization_files(root_dir):
    """
    Returns a list of full paths to all Localization.strings files
    found in subdirectories of the given root directory.
    """
    localization_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, 'Localizable.strings'):
            localization_files.append(os.path.join(dirpath, filename))
    return localization_files

def add_localization_to_database(path, lang_code):
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    if os.path.isfile(path):
        with open(path, 'r') as f:
            for line in f:
                print("line:")
                print(line)
                parts = line.strip().split(' = ')
                print("parts: ")
                print(parts)
                try:
                    translation_id = parts[0].strip('"')
                    translation = parts[1].strip('"').rstrip('"')  # remove the last double quote
                    translation = translation.replace('";', '')
                    c.execute("SELECT * FROM translations WHERE translation_id = ?", (translation_id,))
                    row = c.fetchone()
                    if row:
                        c.execute("UPDATE translations SET {} = ? WHERE translation_id = ?".format(lang_code), (translation, translation_id))
                    else:
                        c.execute("INSERT INTO translations (translation_id, {}) VALUES (?, ?)".format(lang_code), (translation_id, translation))
                except:
                    pass
    conn.commit()
    conn.close()

def print_table_values(table_name):
    # Open a connection to the database
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()

    # Select all rows from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Print the values of each row
    for row in rows:
        print(row)
        print(f"Translation ID: {row[1]}")
        print(f"English: {row[2]}")
        print(f"Spanish: {row[3]}")
        print(f"Filipino: {row[4]}")
        print("")

# Create SQLite database
def init_db():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE translations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, translation_id TEXT, en TEXT, es TEXT, fil TEXT)''')
    conn.commit()

    # Iterate over data in the format "id" = "english"
    data = '''"generic.error.message" = "There was an error. Please try again later.";
              "generic.contact-support" = "Please contact support at support@stakwork.com";
              "confirm" = "Confirm";'''

    for line in data.split('\n'):
        if line.strip():
            # Parse the translation ID and English translation
            translation_id, en = line.strip().split(' = ')
            translation_id = translation_id.strip('"')
            en = en.strip('"')

            # Insert into SQLite database
            c.execute('''INSERT INTO translations (translation_id, en)
                         VALUES (?, ?)''', (translation_id, en))

    # Commit changes and close database connection
    conn.commit()
    conn.close()


def translate_to_filipino(data):
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()

    translations = {}
    no_translation = {}
    for key, value in data.items():
        c.execute("SELECT fil FROM translations WHERE en=?", (value,))
        row = c.fetchone()
        if row:
            translations[key] = row[0]
        else:
            translations[key] = value
            no_translation[key] = value

    conn.close()

    return (translations,no_translation)


import xml.etree.ElementTree as ET

def extract_strings_from_xml(xml_string):
    root = ET.fromstring(xml_string)
    result = {}
    for string_elem in root.findall('string'):
        name = string_elem.get('name')
        value = string_elem.text
        result[name] = value
    return result

localization_files = find_localization_files('./')
for file_path in localization_files:
    print(file_path)

# add_localization_to_database('./en.lproj/Localizable.strings', 'en')
# add_localization_to_database('./es.lproj/Localizable.strings', 'es')
# add_localization_to_database('./fil.lproj/Localizable.strings', 'fil')

print_table_values('translations')

xml_string = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="add_member_header_name">ADD TRIBE MEMBER</string>\n    <string name="add_member">Add Member</string>\n    <string name="member_alias">Alias *</string>\n    <string name="member_image">Tribe member image</string>\n    <string name="member_public_key">Public Key *</string>\n    <string name="member_route_hint">Route Hint</string>\n    <string name="member_contact_key">Contact Key *</string>\n    <string name="bottom_menu_member_pic_header_text">Member Picture</string>\n    <string name="member_info_required">Alias, Public Key and Contact Key are required</string>\n    <string name="invalid_public_key">Invalid Public Key</string>\n    <string name="invalid_route_hint">Invalid Route Hint</string>\n    <string name="failed_to_add_member">Failed to add member</string>\n    <string name="failed_to_process_image">Failed to process image</string>\n</resources>'
strings = extract_strings_from_xml(xml_string)
print(strings)

filipino,no_translation = translate_to_filipino(strings)
print(filipino)
print(no_translation)
