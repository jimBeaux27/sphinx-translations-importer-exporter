import sqlite3
import fnmatch
import os
import pprint

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
        if row and translations[key] != None:
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

def create_xml_from_strings(strings_dict):
    xml = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    for name, translation in strings_dict.items():
        xml += f'    <string name="{name}">{translation}</string>\n'
    xml += '</resources>'
    return xml

import pprint

def translate_each_android_file():
    output_file = open("no_translation.txt", "a")
    
    for dirpath, dirnames, filenames in os.walk("/Users/jamescarucci/Documents/GitLab/sphinx-kotlin/sphinx/"):
        for filename in [f for f in filenames if f.endswith("strings.xml")]:
            newPath = os.path.join(dirpath, filename)
            if("values-b+fil" in newPath):
                print(newPath)
                try:
                    with open(newPath, "r+") as f:
                        fileContents = f.read()
                        strings = extract_strings_from_xml(fileContents)
                        filipino, no_translation = translate_to_filipino(strings)
                        
                        if no_translation or filipino == None:
                            output_file.write(f"\n{newPath}:\n")
                            pprint.pprint(no_translation, stream=output_file, width=180)
                            output_file.write("-"*15)
                        xml = create_xml_from_strings(filipino)
                        f.seek(0)
                        f.write(xml)
                        f.truncate()
                        
                    print("Translated strings written to file:", newPath)
                    print("~"*10)
                    
                except Exception as e:
                    print(f"Error processing file: {newPath}. {e}")
                    
    output_file.close()

import xml.etree.ElementTree as ET

#pulls key value pairs from translated tagalog txt file
def update_android_translations():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()

    with open('no_translations_android.txt', 'w') as output_file:
        for dirpath, dirnames, filenames in os.walk('/Users/jamescarucci/Documents/GitLab/sphinx-kotlin/sphinx/'):
            for filename in [f for f in filenames if f.endswith('.xml')]:
                if 'values-b+fil' in dirpath:
                    xml_path = os.path.join(dirpath, filename)
                    print(f"Processing {xml_path}")
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        for string_element in root.findall("./string"):
                            key = string_element.get("name")
                            value = string_element.text

                            c.execute('SELECT id FROM translations WHERE translation_id=?', (key,))
                            row = c.fetchone()
                            if row is not None:
                                translation_id = row[0]
                                c.execute('UPDATE translations SET fil=? WHERE id=?', (value, translation_id))
                                print(f"Updated translation for {key}")
                            else:
                                output_file.write(f"No translation found for {key} in {xml_path}\n")
                                print(f"No translation found for {key} in {xml_path}")
                    except Exception as e:
                        print(f"Error processing file {xml_path}: {e}")
    conn.commit()
    conn.close()


def scan_and_populate_db_from_ios_ui_files(lang_code):
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()

    for dirpath, dirnames, filenames in os.walk("/Users/jamescarucci/Documents/GitLab/sphinx-ios/sphinx"):
        for filename in [f for f in filenames if f.endswith(".strings") and lang_code in dirpath]:
            with open(os.path.join(dirpath, filename)) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('"') and '=' in line:
                        try:
                            translation_id, value = line.split('=')
                            translation_id = translation_id.strip('"').replace('"',"")
                            value = value.strip().strip('"').replace('";','')

                            # Check if the translation_id already exists in the database
                            c.execute("SELECT * FROM translations WHERE translation_id=?", (translation_id,))
                            row = c.fetchone()

                            if row:
                                # Update the existing row with the new translation
                                if lang_code == "en.lproj":
                                    c.execute("UPDATE translations SET en=? WHERE id=?", (value, row[0]))
                                elif lang_code == "es.lproj":
                                    c.execute("UPDATE translations SET es=? WHERE id=?", (value, row[0]))
                                elif lang_code == "fil.lproj":
                                    c.execute("UPDATE translations SET fil=? WHERE id=?", (value, row[0]))
                            else:
                                # Insert a new row with the translation
                                if lang_code == "en.lproj":
                                    c.execute("INSERT INTO translations (translation_id, en) VALUES (?, ?)", (translation_id, value))
                                elif lang_code == "es.lproj":
                                    c.execute("INSERT INTO translations (translation_id, es) VALUES (?, ?)", (translation_id, value))
                                elif lang_code == "fil.lproj":
                                    c.execute("INSERT INTO translations (translation_id, fil) VALUES (?, ?)", (translation_id, value))
                        except ValueError:
                            print(f"Error processing line: {line}")

    conn.commit()
    conn.close()


def translate_mac_main_localization_file_to_filipino():
    print('translate_mac_file_to_filipino')
    # Connect to the database
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    # Define the file to read
    filename = '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/fil.lproj/Localizable.strings'

    # Read the file contents
    with open(filename) as f:
        content = f.readlines()
    pass_count = 0
    iterations = 0
    # Process each line of the file
    for line in content:
        # Check if the line contains a string to be translated
        if '=' in line:
            # Split the line into key-value pairs
            key, value = line.strip().split('=')
            key = key.strip('"')
            value = value.strip().strip(';').strip('"')

            # Look up the Filipino translation in the database
            c.execute('SELECT fil FROM translations WHERE en = ?', (value,))
            result = c.fetchone()

            if result is None:
                c.execute('SELECT fil FROM translations WHERE translation_id = ?', (key,))
                result = c.fetchone()
            # If a Filipino translation is found, replace the English value with it
            if result is not None:
                filipino = result[0]
                new_line = f'"{key} = "{filipino}";\n'
                content[content.index(line)] = new_line
                pass_count += 1
            iterations+=1
    # Write the modified contents back to the file
    with open(filename, 'w') as f:
         f.writelines(content)
    pprint.pprint(content)
    print(f"Number of iterations: {iterations}")
    print(f"Number of passes: {pass_count}")
    # Close the database connection
    conn.close()

# def translate_swift_files_to_filipino():
#     # Connect to the database
#     conn = sqlite3.connect('translations.db')
#     c = conn.cursor()

#     # Scan for files to translate
#     for dirpath, dirnames, filenames in os.walk("/Users/jamescarucci/Documents/GitLab/sphinx-mac"):
#         print(filenames)
#         for filename in [f for f in filenames if f.endswith(".strings") and "fil.lproj" in dirpath]:
#             filepath = os.path.join(dirpath, filename)

#             # Read the file contents
#             with open(filepath) as f:
#                 content = f.readlines()

#             # Process each line of the file
#             for i, line in enumerate(content):
#                 # Check if the line contains a string to be translated
#                 if '=' in line:
#                     # Split the line into key-value pairs
#                     key, value = line.strip().split('=', 1)
#                     key = key.strip('"')
#                     value = value.strip().strip(';').strip('"')

#                     # Look up the English translation in the database
#                     c.execute('SELECT en FROM translations WHERE fil = ?', (value,))
#                     result = c.fetchone()

#                     # If an English translation is found, replace the Filipino value with it
#                     if result is not None:
#                         english = result[0]
#                         new_line = f'"{key}" = "{english}";\n'
#                         content[i] = new_line

#             # Write the modified contents back to the file
#             # with open(filepath, 'w') as f:
#             #     f.writelines(content)
#             pprint.pprint(content)
#     # Close the database connection
#     conn.close()

import os
import re
import string

def translate_swift_files_to_filipino():
    # Connect to the database
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()

    # Define the path to search for Swift files
    path = '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop'
    file_paths = [
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Pin/fil.lproj/Pin.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Pin/Views/fil.lproj/PinView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/fil.lproj/Signup.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/FriendMessageView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/WelcomeView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/NamePinView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/ProfileImageView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/ConnectingView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Signup/Custom Views/fil.lproj/SphinxReady.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Contacts/fil.lproj/Contacts.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Contacts/Custom View/fil.lproj/GroupPinView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Groups/fil.lproj/Groups.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Groups/Views/fil.lproj/TribeMemberInfoView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Groups/Views/fil.lproj/GroupMembersView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Dashboard/WebApps/Views/fil.lproj/AuthorizeAppView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Dashboard/Payments/Views/fil.lproj/CommonPaymentView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Dashboard/Payments/Views/fil.lproj/PaymentTemplatesView.strings',
        '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop/Scenes/Dashboard/Chat/Collection View Items/Received/fil.lproj/ExpiredInvoiceReceivedCollectionViewItem.strings'
        ]
    # Define the regular expression to match localized strings
    localized_string_regex = re.compile(r'(?<=\")(.*?)(?=\"\s*=\s*\")(.*?)(?=\";)')
    no_translation = ""
    # Walk through the directory tree and find all Swift files
    #for dirpath, dirnames, filenames in os.walk(path):
    for filename in file_paths:
        with open(os.path.join(filename)) as f:
            content = f.read()

        # Find all the localized strings in the file using the regular expression
        matches = re.findall(localized_string_regex, content)

        # Loop through the matches and translate each string
        for key, value in matches:
            # Look up the Filipino translation in the database
            if(len(value.split('" = "'))>1):
                value = value.split('" = "')[1]
            c.execute('SELECT fil FROM translations WHERE en = ?', (value,))
            result = c.fetchone()

            # If a Filipino translation is found, replace the English value with it
            if result is not None:
                filipino = result[0]
                if filipino is not None:
                    content = content.replace(f'"{key}" = "{value}"', f'"{key}" = "{filipino}"')
                    print(f'replacing {key} = {value} with {filipino}')
            else:
                # Exclude the equals sign and double quotes before the string value
                print(f"no translation for: {value}")
                print(f"at filename:{filename}")
                no_translation+=(value)
                no_translation+=("\n")
                #no_translation+=("(" + dirpath + ")")
                no_translation+=("\n")
                no_translation+=("------")
                no_translation+=("\n")

        # Write the modified contents back to the file
        with open(os.path.join(filename), 'w') as f:
            f.write(content)

        with open(os.path.join("/Users/jamescarucci/Documents/GitLab/sphinx-translations-importer-exporter/Translations Database", "mac_no_translations.txt"), 'w') as f:
            f.write(no_translation)

    # Close the database connection
    conn.close()


import ast

def sanitize_string(s):
    """Sanitizes a string by removing any non-printable characters"""
    return ''.join(filter(lambda x: x in string.printable, s))

def read_mac_no_translations_file(file_path):
    with open(file_path, 'r') as file:
        no_translations_text = file.read()
        no_translations_array = no_translations_text.split('------\n')
    return no_translations_array

def parse_mac_no_translations_entry(entry):
    lines = entry.split('\n')

    # Extract the second line and the line before it
    translation_id = lines[1]
    en_text = lines[0].strip()

    return (translation_id, en_text)


def insert_filipino_translations(tuples):
    with sqlite3.connect('translations.db') as conn:
        c = conn.cursor()

        for tuple in tuples:
            en, fil = tuple[1], tuple[2]
            c.execute('''INSERT INTO translations (en, fil)
                         VALUES (?, ?)''', (en, fil))
            print(f'Inserted pair {(en,fil)} into db')

        conn.commit()



####Start recover translations for mac##

# no_translations_array = read_mac_no_translations_file('original_english_flie.txt')
# translations_array = read_mac_no_translations_file('new_filipino_file.txt')

# tuples = []
# filipino_tuples = []
# for entry in no_translations_array:
#     if entry:
#         parsed_entry = parse_mac_no_translations_entry(entry)
#         tuples.append(parsed_entry)

# for entry in translations_array:
#     if entry:
#         parsed_entry = parse_mac_no_translations_entry(entry)
#         filipino_tuples.append(parsed_entry)

# pprint.pprint(tuples)
# pprint.pprint(filipino_tuples)

# print(len(tuples))
# print(len(filipino_tuples))

# combined_tuples = []

# for i in range(0,len(filipino_tuples) - 1):
#     new_tuple = (tuples[i][0],tuples[i][1],filipino_tuples[i][1])
#     combined_tuples.append(new_tuple)

# print(combined_tuples)

# insert_filipino_translations(combined_tuples)
####END recover translations for mac##



# init_db()
# localization_files = find_localization_files('./')
# # for file_path in localization_files:
# #     print(file_path)

# add_localization_to_database('./en.lproj/Localizable.strings', 'en')
# add_localization_to_database('./es.lproj/Localizable.strings', 'es')
# add_localization_to_database('./fil.lproj/Localizable.strings', 'fil')

# scan_and_populate_db_from_ios_ui_files("en.lproj")
# scan_and_populate_db_from_ios_ui_files("es.lproj")
# scan_and_populate_db_from_ios_ui_files("fil.lproj")

#print_table_values('translations')


# db = sqlite3.connect('translations.db')
# join_mac_translations_insert_into_db('translations.db', 'mac_no_translations copy.txt', 'mac_filipino_translations.txt')



#insert_mac_english_translations('translations.db', 'mac_no_translations copy.txt')

# translate_each_android_file()

#translate_mac_main_localization_file_to_filipino()

translate_swift_files_to_filipino()


#import_dictionary_based_translations_to_db()


# update_android_translations()
# translate_each_android_file()

#import_dictionary_based_translations_to_db()

#translate_swift_files_to_filipino()

# path = '/Users/jamescarucci/Documents/GitLab/sphinx-mac/com.stakwork.sphinx.desktop'


# for root, dirs, files in os.walk(path):
#     for file in files:
#         if 'fil.lproj' in root:
#             filepath = os.path.join(root, file)
#             print(filepath)


