import subprocess
import sys

# List of required packages
REQUIRED_PACKAGES = ["requests", "beautifulsoup4"]

def check_and_install_packages(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"The package '{package}' is not installed. Installing it now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Verify and install dependencies
check_and_install_packages(REQUIRED_PACKAGES)

import csv
import requests
from bs4 import BeautifulSoup

# URL of the Google Cloud documentation on resource types
GCP_ASSET_TYPES_URL = "https://cloud.google.com/asset-inventory/docs/supported-asset-types"

def fetch_asset_type_mapping():
    # Make a GET request to the documentation URL
    response = requests.get(GCP_ASSET_TYPES_URL)
    response.raise_for_status()  # Raise an error if the request was unsuccessful

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all asset types and their descriptions on the page
    asset_type_mapping = {}
    for section in soup.select('div.devsite-article-body h2'):
        asset_type = section.get_text().strip()
        description = section.find_next_sibling('p').get_text().strip()
        asset_type_mapping[asset_type] = description

    return asset_type_mapping

# Get the updated asset type mapping
asset_type_mapping = fetch_asset_type_mapping()

# Function to translate the asset type
def translate_asset_type(asset_type):
    return asset_type_mapping.get(asset_type, asset_type)  # Return the friendly name or the original type if no mapping

# Read the projects from a text file
with open('projects.txt') as f:
    projects = f.read().splitlines()

# CSV file header
fields = ["asset_type", "display_name", "location", "project_id", "status"]
rows = []

# Iterate over each project and list the assets
for project in projects:
    print(f"Listing assets for project: {project}")
    try:
        # Run the gcloud command and get the output in CSV format
        result = subprocess.run(
            ["gcloud", "asset", "search-all-resources", f"--scope=projects/{project}", "--format=csv(assetType, displayName, location, project, state)"],
            capture_output=True, text=True, check=True
        )
        # Read the gcloud results and add them to the rows
        output = result.stdout.splitlines()[1:]  # Skip the first line (header)
        for line in output:
            fields_values = line.split(",")
            fields_values[0] = translate_asset_type(fields_values[0])  # Translate the asset type
            rows.append(fields_values)
    except subprocess.CalledProcessError as e:
        print(f"Error listing assets for project {project}: {e}")

# Write the results to a CSV file
with open('all_projects_assets.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)  # Write the header
    csvwriter.writerows(rows)   # Write the rows

print("Inventory completed and saved to all_projects_assets.csv")

