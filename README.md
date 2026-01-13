# SRTM Africa

A Python toolkit for downloading, processing, and mosaicking SRTM (Shuttle Radar Topography Mission) elevation data tiles covering the African continent.

## Overview

This repository provides automated scripts to download all SRTM tiles that cover Africa, convert them to GeoTIFF format, and create seamless mosaics of the elevation data. SRTM data provides digital elevation models at various resolutions and is widely used in geographic information systems for terrain analysis, hydrological modeling, and geospatial applications.

## Features

- **Automated Download**: Batch download of all SRTM tiles covering Africa
- **Format Conversion**: Convert downloaded tiles to GeoTIFF format
- **Mosaic Creation**: Build virtual rasters (VRT) for seamless data access
- **Simple Configuration**: Easy-to-use Python scripts with minimal setup

## Requirements

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

## Scripts

### 1. `download1.py`
Downloads SRTM tiles covering the African continent from online repositories.

**Usage:**
```bash
python download1.py
```

### 2. `tif1.py`
Converts downloaded SRTM tiles to GeoTIFF format for easier processing and compatibility with GIS software.

**Usage:**
```bash
python tif1.py
```

### 3. `vrt.py`
Creates a Virtual Raster (VRT) file that mosaics all individual tiles into a single seamless dataset without duplicating data.

**Usage:**
```bash
python vrt.py
```

## Workflow

Follow these steps to download and process SRTM data for Africa:

1. **Download tiles:**
   ```bash
   python download1.py
   ```

2. **Convert to GeoTIFF:**
   ```bash
   python tif1.py
   ```

3. **Create mosaic:**
   ```bash
   python vrt.py
   ```

## About SRTM Data

The Shuttle Radar Topography Mission (SRTM) obtained elevation data on a near-global scale to generate the most complete high-resolution digital topographic database of Earth. The mission was flown on Space Shuttle Endeavour in February 2000.

**Key characteristics:**
- Coverage: 56°S to 60°N latitude (covers all of Africa)
- Resolution: Available in 30m (1 arc-second) and 90m (3 arc-second) versions
- Format: Typically distributed as .hgt files in 1°×1° tiles
- Coordinate System: WGS84 (EPSG:4326)

## Data Sources

SRTM data can be obtained from:
- [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- [NASA SRTM](https://www2.jpl.nasa.gov/srtm/)
- [OpenTopography](https://opentopography.org/)

## Output

The scripts will generate:
- Individual SRTM tile files (`.hgt` format)
- Converted GeoTIFF files (`.tif` format)
- A Virtual Raster mosaic file (`.vrt` format)

## Use Cases

This dataset is valuable for:
- Topographic mapping and analysis
- Watershed and hydrological modeling
- Viewshed and line-of-sight analysis
- 3D terrain visualization
- Infrastructure planning
- Environmental studies
- Climate and weather modeling

## Notes

- Ensure you have sufficient disk space as SRTM data for Africa will require several gigabytes
- Download times will vary depending on your internet connection
- Some tiles may contain data voids in areas of steep terrain or water bodies
- Always verify the data coverage and quality for your specific area of interest

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Please refer to the USGS/NASA SRTM data usage policies for the elevation data. The scripts in this repository are provided as-is for educational and research purposes.

## Acknowledgments

- NASA and the National Geospatial-Intelligence Agency (NGA) for the SRTM mission
- USGS for providing free access to SRTM data
- The geospatial open-source community

## Support

For issues, questions, or suggestions, please open an issue on this repository.

---

**Disclaimer**: This is an independent project and is not affiliated with or endorsed by NASA, USGS, or any official SRTM data provider.