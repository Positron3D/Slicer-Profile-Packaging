"""
Generates a test PrusaSlicer bundle for testing the configuration wizard.

Usage: python3 PrusaSlicer/GenerateTestBundle.py
"""

import os
import tempfile
import zipfile
from PrusaSlicer import GenerateBundleFiles


def createZipArchive(sourcePath: str, targetPath: str, newFiles: dict[str, str]) -> None:
    """Creates a new zip file from an existing one with overridden files.

    :param sourcePath: Source zip file path to read from.
    :param targetPath: Target zip file path to write to.
    :param newFiles: Override files in the target zip file.
    """

    with zipfile.ZipFile(sourcePath, "r") as sourceArchive:
        with zipfile.ZipFile(targetPath, "w") as targetArchive:
            # Copy the existing files.
            for item in sourceArchive.infolist():
                if item.filename in newFiles.keys():
                    targetArchive.write(newFiles[item.filename], item.filename)
                else:
                    targetArchive.writestr(item, sourceArchive.read(item.filename))

            # Add new files.
            for fileName in newFiles.keys():
                if fileName not in sourceArchive.namelist():
                    targetArchive.write(newFiles[fileName], fileName)


def generateTestBundle() -> str:
    """Generates a test PrusaSlicer profile bundle for testing the configuration wizard.

    :return: Path of the test bundle.
    """

    # Create the bundle files.
    bundleFilesPath = GenerateBundleFiles.createPrusaSlicerFiles()

    # Download the offline profiles.
    offlineProfilesPath = GenerateBundleFiles.downloadFile("non-prusa-fff-offline.zip", "https://storage.googleapis.com/prusa3d-content-prod-14e8-preset-repo-api-public/non-prusa-fff/non-prusa-fff-offline.zip")

    # Create the indices archive.
    # The archive must be extracted before being modified.
    with tempfile.NamedTemporaryFile(mode="wb") as indicesSourceArchive:
        indicesTargetArchive = tempfile.NamedTemporaryFile(mode="wb")
        with zipfile.ZipFile(offlineProfilesPath, "r") as archive:
            # Read the indices file.
            indicesSourceArchive.write(archive.read("vendor_indices.zip"))

            # Create the new indices file.
            createZipArchive(indicesSourceArchive.name, indicesTargetArchive.name, {
                "Positron3D.idx": os.path.join(bundleFilesPath, "index.idx"),
            })

    # Create the test bundle archive.
    archivePath = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "non-prusa-fff-offline.zip"))
    newFiles = {
        "vendor_indices.zip": indicesTargetArchive.name,
    }
    for fileName in os.listdir(bundleFilesPath):
        newFiles["Positron3D/" + fileName] = os.path.join(bundleFilesPath, fileName)
    createZipArchive(offlineProfilesPath, archivePath, newFiles)

    # Close the new indices archive.
    indicesTargetArchive.close()

    # Return the archive path.
    print(f"Created test bundle at {archivePath}")
    return archivePath


if __name__ == '__main__':
    # Create the test bundle.
    generateTestBundle()
