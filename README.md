# GIMP Automation Scripts

A collection of Python scripts for GIMP 3.0 automation, designed to optimize workflows with batch image processing and panoramic project handling.

## Available Scripts

### 1. Image Export (`exportar_img_GIMP.py`)
Exports all open images in GIMP to various formats with an intuitive graphical interface.

### 2. Panorama Projection (`projecao_panorama.py`)
Applies "Panorama Projection" filter in batch to all open images, ideal for processing 360° images.

### 3. Panorama Reversion (`reverter_projecao_panorama.py`)
Reverts processed images back to equirectangular format (360° × 180°) using inverse transformation.

### 4. Save Projects (`salvar_projetos_GIMP.py`)
Saves all open projects in GIMP's native XCF format, preserving layers and effects.

## Requirements

- **GIMP 3.0** or higher
- **Python 3.x** (usually included with GIMP)
- **PyGObject** (GTK bindings for Python)

## Installation & Usage

### Python Fu Console Method

1. Open GIMP
2. Go to **Filters → Development → Console**
3. Copy and paste the desired script code
4. Press **Enter** to execute

This is the only supported method for running these scripts.

## User Manual

### Image Export

**Functionality**: Exports all open images in GIMP to common formats.

**How to use**:
1. Open multiple images in GIMP
2. Execute the script
3. Configure:
   - **Output folder**: Location to save images
   - **Format**: PNG, JPEG, BMP or TIFF
   - **Quality**: For JPEG (10-100%)
4. Click "Export"

**Supported formats**:
- **PNG**: Lossless, transparency support
- **JPEG**: Smaller size, configurable quality
- **BMP**: Uncompressed
- **TIFF**: High quality for printing

### Panorama Projection

**Functionality**: Applies panoramic projection in batch, transforming 360° images into specific views.

**How to use**:
1. Open equirectangular panoramic images
2. Execute the script
3. Configure:
   - **Tilt**: Vertical angle (-180° to 180°)
   - **Zoom**: Projection magnification (0.01 to 1000%)
   - **Sampler**: Resampling method
4. Adjust processing options
5. Click "Process All"

**Important settings**:
- **Tilt 90°**: "Looking up" view
- **Zoom 50%**: Moderate magnification
- **Preserve original**: Duplicates layer before applying

### Panorama Reversion

**Functionality**: Reverts panoramic projections back to equirectangular format.

**How to use**:
1. Select the layer with applied projection
2. Execute the script
3. **Use the same settings** from the previous script:
   - Same **Tilt** value
   - Same **Zoom** value
   - Same **Sampler**
4. Click "Apply Inverse Transform"

**Important**: Settings must be identical to those used in the original projection for correct results.

### Save Projects

**Functionality**: Saves all open projects in native XCF format.

**How to use**:
1. Have open projects with modifications
2. Execute the script
3. Configure:
   - **Output folder**: Location to save projects
   - **Overwrite**: Whether to replace existing files
   - **Mark as saved**: Removes asterisk (*) from title
4. Click "Save Projects"

**XCF advantages**:
- Preserves all layers
- Maintains non-destructive effects
- Saves filter history
- Optimized native format

## Troubleshooting

### Error: "No open images"
- **Cause**: Scripts need open images/projects
- **Solution**: Open at least one image before executing

### Error: "Selected drawable is not a layer"
- **Cause**: Selection of channel or mask instead of layer
- **Solution**: Select a valid layer in the layers palette

### Error: "Could not create folder"
- **Cause**: Insufficient permissions or invalid path
- **Solution**: Choose folder with write permissions

### Interface doesn't appear
- **Cause**: Issues with GTK or PyGObject
- **Solution**: Reinstall GIMP or check Python dependencies

### Panorama filter fails
- **Cause**: Layer without alpha channel or incompatible format
- **Solution**: Scripts automatically add alpha when necessary

## Recommended Workflow

### For Complete Panoramic Processing:

1. **Open panoramic images** (equirectangular format 360° × 180°)
2. **Execute panorama projection** with desired settings
3. **Edit projected views** as needed
4. **Execute panorama reversion** with same settings
5. **Save projects** in XCF to preserve work
6. **Export final images** in required formats

### For Simple Export:

1. **Open multiple images** for processing
2. **Make necessary edits** to each image
3. **Execute image export** to final format
4. **Optionally save projects** before closing

## Compatibility

- **GIMP**: Version 3.0 or higher
- **Python**: 3.6+
- **Systems**: Windows, macOS, Linux
- **Dependencies**: gi (PyGObject), GTK 3.0

## Technical Details

### API Used
Scripts utilize official GIMP 3.0 APIs:
- `Gimp.get_images()`: Getting open images
- `Gimp.DrawableFilter`: Applying GEGL filters
- `Gimp.file_save()`: Export and save operations
- `Gtk.Dialog`: Graphical user interface

### GEGL Filters
- **gegl:panorama-projection**: Panoramic transformation
- **Inverse transform**: Projection reversion
- **Sampler types**: nearest, linear, cubic, nohalo, lohalo

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Maintain compatibility with GIMP 3.0
- Document new features
- Test on different operating systems
- Follow Python code conventions (PEP 8)
- Include proper error handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

To report bugs or request features:
- Open an **Issue** on GitHub
- Include GIMP version and operating system
- Describe steps to reproduce the problem
- Attach error logs when applicable

## Changelog

### v1.0.0
- Initial release with 4 functional scripts
- Complete graphical interface for all scripts
- Support for multiple export formats
- Batch processing for panoramic projections
- Automatic XCF project saving

---

**Developed for the GIMP community** | **Tested on GIMP 3.0** | **Compatible with Python 3.6+**
