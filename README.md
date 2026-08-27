# Slicer-Profile-Packaging
Scripts for packaging 3D printer profiles for slicers.

## PrusaSlicer
### Creating Bundles
`GenerateBundleFiles.py` is used to generate bundle files for PrusaSlicer. When run, it will create the files to add/replace in `output/PrusaSlicer`.

```
cd scripts
python3 ./PrusaSlicer/GenerateBundleFiles.py
```

### Testing Bundles
There are 2 scripts used to help test bundles in PrusaSlicer before creating a pull request with the PrusaSlicer non-Prusa fff settings.
- `GenerateTestBundle.py` - Creates a zip file at `output/non-prusa-fff-offline.zip` to use in the configuration wizard as an offline source.
- `UseTestBundle.py` - Configures PrusaSlicer to use the test bundle.
  - **This clears the PrusaSlicer cache and may mess with stored profiles**. Keep a backup of the PrusaSlicer config directory.
  - This automatically calls `GenerateTestBundle.py`, so that script does not need to be run.

To only generate the test bundle:
```
cd scripts
python3 ./PrusaSlicer/GenerateTestBundle.py
```

To generate the test bundle and use it in PrusaSlicer:
```
cd scripts
python3 ./PrusaSlicer/UseTestBundle.py
```