# -*- coding: utf-8 -*-

"""
The loc-sal-tools Pythong script is designed for the Library of Congress Statutes at Large metadata 
project, specifically the auditing and conversion of data found in Excel files
`LoC_1-50` and `LoC_51-71`. In addition, it is meant for use with a single Excel.

Worksheets in the master Excel files will need to be saved as a new Excel file for processing.
"""

# === Imports ===
import os
import re
import sys
from pathlib import Path

# Third-party library imports
import pandas as pd
import yaml

# === Constants/Globals ===
# Initialize CONSTANTS to be loaded from the user-config
CONGRESS: None
CONGRESS_START_DATE: None
CONGRESS_END_DATE: None
PUBLIC_PDF_URL: None
PRIVATE_PDF_URL: None


EXCEL_FILE: None
START_ROWS: None
OUTPUT_FILE: None

EXCEL_DIR: None
HTML_DIR: None
TMP_DIR: None
IN_PROCESS_PREFIX: None
AUDITED_PREFIX: None


# === Utility Functions ===
def clear_screen():
    """Clear the terminal or command prompt screen."""
    os.system("cls" if os.name == "nt" else "clear")


def load_yaml(file_name):
    """Load a YAML file and return its content."""
    with open(file_name, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error loading {file_name}: {exc}")
            return None


def load_config(file_name):
    """Load configuration from a YAML file."""
    return load_yaml(file_name)


def map_headers(header):
    """
    Map the given header to its standardized format.

    Args:
    - header (str): The header to be mapped.

    Returns:
    - str: The standardized header, or the original header if no mapping is found.
    """
    # Look up the given header in the header_mappings dictionary.
    # If a mapping is found, return the standardized header.
    # If no mapping is found, return the original header.

    return header_mappings.get(header, header)


def map_statute_type(statute_type):
    """
    Map the given statute type to its standardized format.

    Args:
    - statute_type (str): The statute type to be mapped.

    Returns:
    - str: The standardized statute type, or the original statute type if no mapping is found.
    """
    # Look up the given statute type in the statute_mappings dictionary.
    # If a mapping is found, return the standardized statute type.
    # If no mapping is found, return the original statute type.
    return statute_mappings.get(statute_type, statute_type)


def map_html_generators(statute_type):
    """
    Map the given statute type to its corresponding HTML generator function.

    Args:
    - statute_type (str): The statute type to be mapped.

    Returns:
    - function: The HTML generator function associated with the statute type, or None if no mapping is found.
    """
    # Look up the given statute type in the html_generator_mappings dictionary.
    # If a mapping is found, return the corresponding HTML generator function.
    # If no mapping is found, return None.
    return html_generator_mappings.get(statute_type, None)


def arabic_to_roman(num):
    """
    Convert Arabic numerals to Roman numerals.

    Args:
    - num (int): The Arabic numeral to be converted.

    Returns:
    - str: The Roman numeral representation of the input Arabic numeral.
    """
    # Create a dictionary that maps Arabic numerals to Roman numeral symbols.
    numeral_map = {
        1000: "M",
        900: "CM",
        500: "D",
        400: "CD",
        100: "C",
        90: "XC",
        50: "L",
        40: "XL",
        10: "X",
        9: "IX",
        5: "V",
        4: "IV",
        1: "I",
    }
    # Initialize an empty string to store the Roman numeral.
    roman_numeral = ""
    # Iterate through the values in the numeral_map.
    for value in numeral_map:
        while num >= value:
            roman_numeral += numeral_map[value]
            num -= value
    return roman_numeral


def html_for_law(pdf_link, statute_type, title, date, public_private, number_chapter):
    return f"""
                    <tr>
                        <td><a target="_blank" href="{pdf_link}">{number_chapter}</a></td>
                        <td>{public_private}</td>
                        <td>{title}</td>
                        <td>{date}</td>
                    </tr>"""


def html_for_act_resolution_appendix(
    pdf_link, statute_type, title, date, public_private, number_chapter
):
    digit_match = re.search(r"\d+", number_chapter)
    matched_digits = digit_match.group()
    number = int(matched_digits)
    title = arabic_to_roman(number) + ". " + title
    return f"""
                    <tr>
                        <td><a target="_blank" href="{pdf_link}">{statute_type}</a></td>
                        <td>{public_private}</td>
                        <td>{title}</td>
                        <td>{date}</td>
                    </tr>"""


def generic_html_generator(
    pdf_link, statute_type, title, date, public_private, number_chapter
):
    return f"""
                    <tr>
                        <td><a target="_blank" href="{pdf_link}">{statute_type}</a></td>
                        <td></td>
                        <td>{title}</td>
                        <td>{date}</td>
                    </tr>"""


def html_for_articles_ordinance(
    pdf_link, statute_type, title, date, public_private, number_chapter
):
    return f"""
                    <tr>
                        <td><a target="_blank" href="{pdf_link}">{statute_type}</a></td>
                        <td></td>
                        <td>{title}</td>
                        <td></td>
                    </tr>"""


def html_for_special_pages(
    pdf_link, statute_type, title, date, public_private, number_chapter
):
    return f"""
                    <tr>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                    </tr>
    
                    <tr>
                        <td><a target="_blank" href="{pdf_link}">{statute_type}</a></td>
                        <td></td>
                        <td>{title}</td>
                        <td></td>
                    </tr>"""


def html_with_empty_cells(
    pdf_link, statute_type, title, date, public_private, number_chapter
):
    return f"""
                    <tr>
                        <td type="empty"><a target="_blank" href="{pdf_link}">{statute_type}</a></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>"""


# === Initialization/Setup ===
# Load User config
user_config = load_config("user-config.yaml")

# Load mappings
header_mappings = load_yaml("maps/header-map.yaml")
statute_mappings = load_yaml("maps/statute-map.yaml")
html_generator_mappings = load_yaml("maps/html-generators-map.yaml")


# === Main Functions/Classes ===
def load_excel_file(config, file_name, skip_rows):
    """
    Load and preprocess the given Excel file.

    Args:
    - config (dict): Dictionary containing configuration settings.
    - file_name (str): The name of the Excel file to load.
    - skip_rows (int): The number of rows to skip while reading the Excel file.

    Returns:
    - pd.DataFrame: A DataFrame containing the loaded and preprocessed data.
    """

    # Construct the full path to the Excel file using the provided directory and file name.
    excel_path = Path(config["EXCEL_DIR"]) / file_name

    # Adjust the skip_rows value to account for the difference in indexing between Excel and Python
    skip_rows = range(1, config["START_ROW"] - 1)

    # Attempt to read the Excel file into a DataFrame, specifying the header row and skiprows.
    try:
        data_frame = pd.read_excel(excel_path, header=0, skiprows=skip_rows)
    except FileNotFoundError:
        print(f"Error: File '{excel_path}' not found. Please check path and filename.")
        exit()
    except pd.errors.EmptyDataError:
        print(f"Error: File '{excel_path}' is empty or lacks data.")
        exit()
    except Exception as e:
        print(f"Error reading '{excel_path}': {e}. Ensure it's a valid Excel file.")
        exit()

    # Standardize column headers and statute types
    data_frame.columns = [map_headers(col) for col in data_frame.columns]
    if "Type" in data_frame.columns:
        data_frame["Type"] = data_frame["Type"].apply(map_statute_type)

    return data_frame


def get_last_audited_row(config, file_name: Path):
    """
    Retrieve the last audited row from a checkpoint file based on the filename.

    Args:
    - config (dict): Dictionary containing configuration loaded from YAML.
    - file_name (Path): The name of the Excel file for which to find the last audited row.

    Returns:
    - int: The last audited row number. Returns 0 if not found.
    """
    checkpoint_file_path = (
        Path(config["TMP_DIR"]) / f"audit-checkpoint-{Path(file_name).stem}.txt"
    )

    if checkpoint_file_path.exists():
        with checkpoint_file_path.open("r") as checkpoint_file:
            content = checkpoint_file.read().strip()
            return int(content) if content else 0
    return 0


def audit_process(config, df, last_audited_row):
    """
    Interactively audit the data in the provided DataFrame starting from the last audited row.

    Args:
    - config (dict): Dictionary containing configuration loaded from YAML.
    - df (pd.DataFrame): The data to be audited.
    - last_audited_row (int): The last row that was audited.

    Returns:
    - bool: True if the audit process was completed without interruption; False otherwise.
    """

    skip_rows = config.get("SKIP_ROWS", [])
    checkpoint_file_path = (
        Path(config["TMP_DIR"])
        / f"audit-checkpoint-{Path(config['EXCEL_FILE']).stem}.txt"
    )

    for idx, row in df.iterrows():
        if idx < last_audited_row:
            continue

        while True:
            clear_screen()
            user_input = input(
                f"\nIs the PDF Start for:\n\n{row['Session']}\n\n{row['Number/Chapter']} - {row['Title']}\n\nPDF Page: {row['PDF Start']}\n\nCorrect? Yes (Y) or No (N) - (Enter 'exit' to stop):"
            )

            if user_input.lower() == "exit":
                print(
                    f"\nAudit process paused at row {int(idx) + 2 + len(skip_rows)} of {len(df.index)}."
                )
                with checkpoint_file_path.open("w") as checkpoint_file:
                    checkpoint_file.write(str(idx))
                return False

            elif user_input.lower() == "y":
                break

            elif user_input.lower() == "n":
                correct_pdf_start = input(
                    f"\nWhat is the correct PDF Start for {row['Title']}, {row['Session']}-{row['Number/Chapter']}? (Enter 'exit' to stop) "
                )

                if correct_pdf_start.lower() == "exit":
                    print(
                        f"\nAudit process paused at row {int(idx) + 2 + len(skip_rows)} of {len(df.index)}."
                    )
                    with checkpoint_file_path.open("w") as checkpoint_file:
                        checkpoint_file.write(str(idx))
                    return False

                try:
                    correct_pdf_start = int(correct_pdf_start)
                    df.at[idx, "PDF Start"] = correct_pdf_start
                    break
                except ValueError:
                    print(
                        "Invalid input. Please enter a valid PDF Start value (an integer)."
                    )

            else:
                print("Invalid input. Please enter 'Y', 'N', or 'exit'.")

    return True


def generate_pdf_link(config, statute_type, public_private, pdf_start):
    """
    Generate the appropriate PDF link based on statute type and public/private status.

    Args:
    - config (dict): Dictionary containing configuration loaded from YAML.
    - statute_type (str): The type of the statute (e.g., "Law").
    - public_private (str): Indicates if the statute is public or private.
    - pdf_start (int): The starting page number for the PDF.

    Returns:
    - str: The generated PDF link.
    """
    if statute_type == "Law" and public_private == "Private":
        return f"{config['PRIVATE_PDF_URL']}#page={pdf_start}"
    else:
        return f"{config['PUBLIC_PDF_URL']}#page={pdf_start}"


def generate_html(df, config):
    """
    Generate HTML content for displaying law information based on the provided DataFrame and configuration.

    Args:
    - df (pd.DataFrame): The DataFrame containing law information.
    - config (dict): Dictionary containing configuration settings.

    Returns:
    - str: HTML content for displaying law information.
    """

    # Initialize the HTML content and previous session variables.
    html_content = ""
    previous_session = ""

    # Start building the HTML content with a template.
    html_content = f"""
    <!-- Begin HTML-->
    <a name="{config['CONGRESS_START_DATE']}" id="{config['CONGRESS_END_DATE']}"></a>
    <h3 class="js-expandmore" data-hideshow-prefix-class="light">{config['CONGRESS']} ({config['CONGRESS_START_DATE']}-{config['CONGRESS_END_DATE']})</h3>
    <div class="js-to_expand">"""

    for _, row in df.iterrows():
        try:
            session = str(row["Session"])
            statute_type = str(row["Type"])
        except ValueError:
            print(
                f"Error: Unexpected or missing data in row {_}. Please review the entries in '{excel_path}' for completeness and correctness."
            )
            continue

        # Extract relevant data from the row
        session = str(row["Session"])
        statute_type = str(row["Type"]).strip()
        public_private = str(row.get("Public/Private", ""))
        title = str(row["Title"]) if not pd.isna(row["Title"]) else ""
        date = str(row["Date"])
        number_chapter = str(row["Number/Chapter"])
        pdf_start = str(row["PDF Start"])

        # If the current session differs from the previous one, create a new header and table.
        if (
            not pd.isna(session) and session != previous_session
        ):  # start a new session only if it's not nan and different from the previous
            if previous_session:  # If there was a previous session, close its table.
                html_content += f"""
                </tbody>
            </table>"""

            # Open a new table for the new session (if session is not empty)
            if session:
                html_content += f"""
        <h4>{session}</h4>
            <table class="table-bordered table-padded table-full-width">
                <tbody>"""

            previous_session = session

        # Determine the correct PDF link based on the type and public/private
        pdf_link = generate_pdf_link(config, statute_type, public_private, pdf_start)

        # Use the correct HTML generator based on the statute type
        generator_function_name = map_html_generators(statute_type)
        generator = globals().get(generator_function_name, None)

        if generator:
            # Call the selected generator function
            html_segment = generator(
                pdf_link, statute_type, title, date, public_private, number_chapter
            )
            html_content += html_segment
        else:
            # Default to empty cells if no generator is found for the given statute type
            print(f"No generator found for statute_type: '{statute_type}'")
            html_content += html_with_empty_cells(
                pdf_link, statute_type, title, date, public_private, number_chapter
            )

    # Close the last table (if any) at the end of the loop.
    if previous_session:
        html_content += "</tbody></table>"

    return html_content


def main():
    # Define global variables for directory paths and prefixes
    global EXCEL_DIR, HTML_DIR, TMP_DIR, IN_PROCESS_PREFIX, AUDITED_PREFIX

    # Load user configuration settings from a YAML file
    config = load_config("user-config.yaml")

    if not config:
        print("Failed to load configuration.")
        sys.exit()

    # Assign configuration values to global variables for easy access
    EXCEL_DIR = Path(config["EXCEL_DIR"])
    HTML_DIR = Path(config["HTML_DIR"])
    TMP_DIR = Path(config["TMP_DIR"])
    IN_PROCESS_PREFIX = config["IN_PROCESS_PREFIX"]
    AUDITED_PREFIX = config["AUDITED_PREFIX"]

    # Define file paths for audited and HTML output files
    audited_file_path = EXCEL_DIR / f"{AUDITED_PREFIX}{config['EXCEL_FILE']}"
    html_output_path = HTML_DIR / config["OUTPUT_FILE"]

    # Check for an existing audited file
    if audited_file_path.exists():
        print(f"\nAudited file '{audited_file_path}' already exists.\n")

        # If there's no existing HTML file, generate one from the audited file
        if not html_output_path.exists():
            print("No corresponding HTML found. Generating HTML...")
            df = pd.read_excel(audited_file_path)  # Load the audited file
            completed = True  # Since it's an audited file
        else:
            print(
                f"\nHTML output '{html_output_path}' already exists. If you wish to regenerate, please delete or backup the existing file.\n"
            )
            sys.exit()

    else:  # Audit is not yet complete
        # Load and preprocess the Excel file
        df = load_excel_file(config, config["EXCEL_FILE"], config["START_ROW"])
        last_audited_row = get_last_audited_row(config, config["EXCEL_FILE"])

        # Perform the audit process and check if it's completed
        completed = audit_process(config, df, last_audited_row)

        if completed:
            # Save the completed audit as an audited file
            df.to_excel(audited_file_path, index=False)
            print(f"Completed audit saved to '{audited_file_path}'\n.")
        else:
            # Save the in-process Excel file with a different name
            in_process_file_path = EXCEL_DIR / (
                IN_PROCESS_PREFIX + config["EXCEL_FILE"]
            )

            df.to_excel(in_process_file_path, index=False)
            print(f"\nIn-process data saved to '{in_process_file_path}'.\n")
            sys.exit()

    # Generate the HTML content and save it
    html_content = generate_html(df, config)
    with open(html_output_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    print(f"Generated HTML saved to '{html_output_path}'.")


# === Conditional Script Execution ===
if __name__ == "__main__":
    main()
