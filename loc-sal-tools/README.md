# ReadMe for loc-sal-tools

## Overview
The `loc-sal-tools.py` is a Python script designed for the Library of Congress Statutes at Large metadata project, specifically the auditing and conversion of data found in Excel files `LoC_1-50` and `LoC_51-71`. In addition, it is meant for use with a single Excel. Worksheets in the master Excel files will need to be saved as a new Excel file for processing.

## Structure
```
loc-sal-tools/
│
├── .gitignore
├── README.md
├── LICENSE
├── loc-sal-tools.py
├── user-config.yaml
├── requirements.txt
│
├── excel-files/   # Directory to hold Excel input files
│
├── html-files/    # Directory to hold generated HTML output files
│
├── maps/          # Directory to hold Python dictionaries in yaml
│
└── tmp/           # Directory for temporary files, like audit checkpoints
```

## Quick Start
1. **Setup**: Ensure you have Python 3.11.5 or newer installed. Not sure? [Here's how to check your Python version.](link_to_a_guide)
2. **Install Required Libraries**: Open your terminal or command prompt and navigate to the directory containing this toolset. Then, run the following command to install the required libraries:. Then run `pip install -r requirements.txt`.
3. **Edit Variables**: Open `user-config.yaml`
4. **Run the Script**: Once variables are set, follow the **Getting Started** steps for each script.
5. **Copy code to Word Doc**: When you have finished and completed writing the code for the individual Congress, you will copy all the code into a Word document.  
6. **Need Help?**: Refer to the troubleshooting sections below.

## Prerequisites

Before running the `loc-sal-tools.py` script, ensure you have the following prerequisites installed:

- Python 3.x: You can download Python from the [official Python website](https://www.python.org/downloads/).
- Pandas: This script utilizes the Pandas library for data manipulation. Install it using pip:
\```bash
pip install pandas
\```

- PyYAML: PyYAML is used for reading configuration files in YAML format. Install it using pip:
\```bash
pip install PyYAML
\```


## Getting Started

### 1. **Preparing Your Excel File**
Ensure your Excel file's name matches the `EXCEL_FILE` variable and is in the `excel-files` directory.

### 2. **Setting User Configuration Variables**
The `user-config.yaml` file contains essential variables that you'll need to customize before running the script. These variables include:

- `CONGRESS`: Specify the name of the Congress you are working on. For example, you can set it to "55th Congress."

- `EXCEL_FILE`: Indicate the name and path of the Excel file you want to process. Make sure to replace the default value, `congress-55.xlsx`, with the actual name of your input Excel file.

- `START_ROW`: Adjust this variable to skip initial rows in your Excel file, such as headers or introductory information. Set it to the row number where the first occurrence of "Session 1" appears under the "Session" column.

- `PUBLIC_PDF_URL` & `PRIVATE_PDF_URL`: You will need to provide the URLs to the PDF files associated with your Congress. To obtain these URLs, visit the [Library of Congress Statutes at Large collection](https://www.loc.gov/collections/united-states-statutes-at-large/articles-and-essays/acts-of-congress/) in your web browser. Extract the relevant URLs from this collection and replace the default values with the correct links.

- `CONGRESS_START_DATE` & `CONGRESS_END_DATE`: Define the date range that corresponds to your Congress. Update these variables with the appropriate start and end dates for your Congress.

- `OUTPUT_FILE`: This variable determines the name of the generated HTML file. The default value is `statutes_at_large_Congress_55.html`. Customize it by replacing "Congress_55" with the appropriate Congress number for your project.

### 3. Script Details

The `loc-sal-tools.py` script is designed for the Library of Congress Statutes at Large metadata project, specifically for the auditing and conversion of data found in Excel files `LoC_1-50` and `LoC_51-71`. The code is heavily commented in order to give non-coders a better understanding of the functionality

### Variables and Constants:

- `user_config`: Contains user-configurable variables loaded from the `user-config.yaml` file, including information about the specific Congress being processed, Excel file names, and other project-related details.

- `header_mappings` and `statute_mappings`: These dictionaries store mappings used to standardize column headers and statute types within the Excel data.

- `EXCEL_DIR`, `HTML_DIR`, `TMP_DIR`, `IN_PROCESS_PREFIX`, and `AUDITED_PREFIX`: These constants define the directory paths and prefixes used for organizing Excel and HTML files and temporary checkpoints during the data processing.

### Utility Functions
The `loc-sal-tools` script includes several utility functions that enhance its functionality:

- `clear_screen()`: Clears the terminal or command prompt screen. This function is used during the auditing process to maintain a clear display.
- `load_yaml(file_name)`: Loads a YAML file and returns its content. It's used for reading configuration files.
- `load_config(file_name)`: Loads configuration settings from a YAML file using the `load_yaml` function.
- `map_headers(header)`: Maps headers to standardized formats in the Excel data.
- `map_statute_type(statute_type)`: Maps statute types to standardized formats.
- `map_html_generators(statute_type)`: Maps statute types to corresponding HTML generator functions.
- `arabic_to_roman(num)`: Converts Arabic numerals to Roman numerals for specific formatting needs.
- HTML Generator Functions: These functions generate HTML content for different types of statutes. They take input parameters and format the content accordingly.


### Main Execution:

The `main()` function serves as the entry point to the script. It performs the following steps:

1. Loads the user-configurable variables from the `user-config.yaml` file.
2. Loads various mapping dictionaries, configuration settings, and file paths.
3. Checks for the existence of audited and HTML files to determine whether the auditing or HTML generation process is required.
4. If auditing is necessary, it loads and preprocesses the Excel data, and the user interacts with the data to verify and correct PDF start page numbers.
5. After auditing or when HTML generation is required, it constructs the HTML content using the `generate_html()` function and saves it to the specified output file.