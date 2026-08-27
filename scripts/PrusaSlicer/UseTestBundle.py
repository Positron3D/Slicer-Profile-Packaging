"""
Sets up the test bundle in PrusaSlicer.
PrusaSlicer may need to be closed when running. The configuration wizard must be closed.
THIS IS DESTRUCTIVE. Back up the PrusaSlicer config directory.
Make sure to revert the offline source in the configuration wizard when done.

Usage: python3 PrusaSlicer/UseTestBundle.py
"""

import os
import json
import shutil
from PrusaSlicer import GenerateTestBundle

# Paths for the PrusaSlicer configuration directories.
configurationDirectories = [
    os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "PrusaSlicer"), # Windows
    os.path.join(os.path.expanduser("~"), ".config", "PrusaSlicer"), # Linux native
    os.path.join(os.path.expanduser("~"), ".var", "app", "com.prusa3d.PrusaSlicer", "config", "PrusaSlicer"), # Linux Flatpak
]


def getConfigurationDirectory() -> str:
    """Returns the PrusaSlicer configuration directory for the current system.

    :return: The PrusaSlicer configuration directory for the current system.
    """

    for path in configurationDirectories:
        if os.path.exists(path):
            return path
    raise Exception("Could not find PrusaSlicer configuration directory")


def useTestBundle() -> None:
    """Sets up PrusaSlicer to use the test bundle.
    """

    # Create the test bundle.
    testBundlePath = GenerateTestBundle.generateTestBundle()

    # Modify the repositories to use the offline version.
    configurationDirectory = getConfigurationDirectory()
    archiveRepositoryManifestPath = os.path.join(configurationDirectory, "ArchiveRepositoryManifest.json")
    with open(archiveRepositoryManifestPath, encoding="utf8") as archiveRepositoryManifestFile:
        # Parse the file.
        archiveRepositoryManifest = json.load(archiveRepositoryManifestFile)

        # Disable Other FFF.
        for entry in archiveRepositoryManifest:
            if "name" in entry.keys() and entry["name"] == "Other FFF":
                entry["selected"] = 0

        # Add the source path if it doesn't exist.
        entryExists = False
        for entry in archiveRepositoryManifest:
            if "source_path" in entry.keys() and entry["source_path"] == testBundlePath:
                entryExists = True
                entry["selected"] = 1
                break
        if not entryExists:
            archiveRepositoryManifest.append({
                "source_path": testBundlePath,
                "selected": 1,
                "has_installed_printers": 0,
            })

    with open(archiveRepositoryManifestPath, "w", encoding="utf8") as archiveRepositoryManifestFile:
        archiveRepositoryManifestFile.write(json.dumps(archiveRepositoryManifest))
    print("Enabled test bundle.")

    # Clear the cache.
    cachePaths = [
        os.path.join(configurationDirectory, "cache", "Positron3D"),
        os.path.join(configurationDirectory, "cache", "Positron3D.idx"),
        os.path.join(configurationDirectory, "cache", "vendor_indices.zip"),
        os.path.join(configurationDirectory, "cache", "vendor", "Positron3D.idx"),
        os.path.join(configurationDirectory, "vendor", "Positron3D"),
        os.path.join(configurationDirectory, "vendor", "Positron3D.ini"),
        os.path.join(configurationDirectory, "vendor", "Positron3D.idx"),
    ]
    for cachePath in cachePaths:
        if os.path.exists(cachePath):
            if os.path.isdir(cachePath):
                shutil.rmtree(cachePath)
            else:
                os.remove(cachePath)
    print("Cleared bundle cache.")


if __name__ == '__main__':
    # Use the test bundle.
    useTestBundle()
