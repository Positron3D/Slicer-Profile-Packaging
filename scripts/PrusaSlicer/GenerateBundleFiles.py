"""
Generates a PrusaSlicer profile bundle file for the Positron 3D printers.

Usage: python3 PrusaSlicer/GenerateBundleFiles.py
"""

# Version of the bundle.
version = "2.0.0"

# Block that is put at the top of the profiles file, including comments and the vendor block.
headerBlock = f"""
# Printer profiles for Positron 3D printers.
# Source: https://github.com/Positron3D/PrusaSlicer-settings-non-prusa-fff
# Generation scripts: https://github.com/Positron3D/Slicer-Profile-Packaging

[vendor]
repo_id = non-prusa-fff
# Vendor name will be shown by the Config Wizard.
name = Positron 3D
# Configuration version of this file. Config file will only be installed, if the config_version differs.
# This means, the server may force the PrusaSlicer configuration to be downgraded.
config_version = {version}
# Where to get the updates from?
config_update_url = https://files.prusa3d.com/wp-content/uploads/repository/PrusaSlicer-settings-master/live/Positron3D/
"""

# Sections of the printers to add.
printers = [
    {
        "name": "Positron",
        "url": "https://raw.githubusercontent.com/Positron3D/Positron/main/Software%20%26%20Calibration/Slicer%20Profiles/Prusa%20Slicer/Positron_config_bundle.ini",
        "lines": [
            "This is maintained in the Positron repository: https://github.com/Positron3D/Positron/blob/main/Software%20%26%20Calibration/Slicer%20Profiles/Prusa%20Slicer/Positron_config_bundle.ini"
        ],
        "files": {
            "bedmodel_positron.stl": "https://raw.githubusercontent.com/Positron3D/Positron/refs/heads/main/Software%20%26%20Calibration/Slicer%20Profiles/Slicer%20Profile%20Plate%20Model/180x180%20Positron%20V3-2%20Model_Simple.stl",
            "bedtexture_positron.svg": "https://raw.githubusercontent.com/Positron3D/Positron/refs/heads/main/Software%20%26%20Calibration/Slicer%20Profiles/Slicer%20Profile%20Plate%20Model/180x180%20Positron%20V3-2%20Texture.svg",
        },
        "replace": {
            "Positron_bed.stl": "bedmodel_positron.stl",
            "ThePositron_bed_texture.svg": "bedtexture_positron.svg",
        },
    },
    {
        "name": "Prusawire",
        "url": "https://raw.githubusercontent.com/Positron3D/Prusawire/refs/heads/main/Slicer%20Profiles/PrusaSlicer/prusaslicer_config_bundle.ini",
        "lines": {
            "This is generated from the Voron Switchwire profiles with a few changes.",
            "Source Voron Switchwire profiles: https://raw.githubusercontent.com/prusa3d/PrusaSlicer-settings-non-prusa-fff/refs/heads/main/Voron/3.0.0.ini",
        },
        "files": {
            "bedmodel_prusawire.stl": "https://raw.githubusercontent.com/Positron3D/Prusawire/refs/heads/main/Slicer%20Profiles/prusawire_build_plate.stl",
            "bedtexture_prusawire.svg": "https://raw.githubusercontent.com/Positron3D/Prusawire/refs/heads/main/Slicer%20Profiles/prusawire_texture.svg",
        },
        "replace": {
            "prusawire_build_plate.stl": "bedmodel_prusawire.stl",
            "prusawire_texture.svg": "bedtexture_prusawire.svg",
        },
    },
]


import os
import shutil
import urllib.request


downloadPath = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "download"))
outputPath = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "PrusaSlicer"))
resources = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "PrusaSlicer"))


def downloadFile(fileName: str, url: str) -> str:
    """Downloads a file.

    :param fileName: Name of the file.
    :param url: URL to download from.
    :return: Path of the file.
    """

    # Create the download directory.
    if not os.path.exists(downloadPath):
        os.makedirs(downloadPath)

    # Download the file if it doesn't exist.
    filePath = os.path.join(downloadPath, fileName)
    if not os.path.exists(filePath):
        print(f"Downloading {url} to {filePath}")
        request = urllib.request.Request(url)
        sourceProfilesData = urllib.request.urlopen(request).read() # Fetched before opening file to avoid creating an empty file on error.
        with open(filePath, "wb") as file:
            file.write(sourceProfilesData)
    else:
        print(f"Already downloaded {filePath}")

    # Return the file path.
    return filePath


def buildPrusaSlicerBundle() -> str:
    """Builds the PrusaSlicer bundle file.

    :return: Path of the file.
    """

    # Create the output directory.
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # Build the sections.
    sections = []
    for printer in printers:
        # Create the header.
        printerHeader = f"##################################################\n# {printer["name"]}"
        for line in printer["lines"]:
            printerHeader += f"\n# {line}"
        printerHeader += f"\n##################################################"

        # Download the slicer profile bundle.
        bundlePath = downloadFile(f"{printer["name"]}.ini", printer["url"])
        with open(bundlePath, encoding="utf8") as file:
            bundleContent = file.read()
            for replaceKey in printer["replace"]:
                bundleContent = bundleContent.replace(replaceKey, printer["replace"][replaceKey])

        # Add the section.
        sections.append(f"{printerHeader}\n\n{bundleContent.strip()}")

    # Write the bundle.
    bundlePath = os.path.join(outputPath, f"{version}.ini")
    with open(bundlePath, "w", encoding="utf8") as file:
        file.write(headerBlock)
        file.write("\n\n\n")
        file.write("\n\n\n\n".join(sections))

    # Return the bundle path.
    return bundlePath


def createPrusaSlicerFiles() -> str:
    """Prepares the files for the PrusaSlicer bundle.

    :return: Path of the directory containing the files to bundle.
    """

    # Build the PrusaSlicer bundle file.
    bundlePath = buildPrusaSlicerBundle()

    # Download and copy the files for the printers.
    for printer in printers:
        for fileName in printer["files"]:
            downloadPath = downloadFile(fileName, printer["files"][fileName])
            shutil.copy(downloadPath, os.path.join(outputPath, fileName))

    # Copy the resources.
    for fileName in os.listdir(resources):
        shutil.copy(os.path.join(resources, fileName), os.path.join(outputPath, fileName))

    # Return the output directory.
    print(f"Created PrusaSlicer bundle files at {outputPath}")
    return outputPath


if __name__ == '__main__':
    # Create the files.
    createPrusaSlicerFiles()
