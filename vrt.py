#!/usr/bin/env python3
"""
SRTM VIRTUAL MOSAIC BUILDER
Creates a virtual mosaic (VRT) from downloaded SRTM tiles
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import glob
import time
from datetime import datetime

# Change to your specific directory
os.chdir("/home/benjamin/Documents/Benjamin/srtm/Africa/srtm_africa/africa_srtm_complete")

def check_gdal_installed():
    """Check if GDAL is available"""
    try:
        subprocess.run(["gdalbuildvrt", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def find_srtm_tiles(directory="."):
    """Find all SRTM tile files in directory"""
    # Common SRTM file patterns
    patterns = [
        "*.tif",                    # GeoTIFF files
        "*.tiff",
        "N*E*.hgt",                 # SRTM HGT format
        "N*W*.hgt",
        "S*E*.hgt",
        "S*W*.hgt",
        "srtm_*.tif",              # AWS format
        "*.dem",                    # DEM files
    ]
    
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(os.path.join(directory, pattern)))
    
    # Filter for SRTM-like files (look for coordinate patterns in names)
    srtm_files = []
    for f in all_files:
        filename = os.path.basename(f)
        # Check if it looks like an SRTM tile
        if (("N" in filename or "S" in filename) and 
            ("E" in filename or "W" in filename)) or \
           filename.startswith("srtm_"):
            srtm_files.append(f)
    
    # Remove duplicates
    srtm_files = list(set(srtm_files))
    
    return sorted(srtm_files)

def create_vrt_mosaic(input_dir=None, output_vrt="africa_srtm.vrt", 
                      tile_list_file=None, recursive=False):
    """
    Create VRT mosaic from SRTM tiles
    
    Args:
        input_dir: Directory containing SRTM tiles
        output_vrt: Output VRT filename
        tile_list_file: Text file with list of tiles (one per line)
        recursive: Search subdirectories recursively
    """
    
    print("=" * 80)
    print("SRTM VIRTUAL MOSAIC BUILDER")
    print("=" * 80)
    
    # Check GDAL installation
    if not check_gdal_installed():
        print("\n❌ ERROR: GDAL is not installed or not in PATH")
        print("Please install GDAL:")
        print("  Ubuntu/Debian: sudo apt install gdal-bin")
        print("  macOS: brew install gdal")
        print("  Windows: Download from OSGeo4W or Conda")
        print("\nYou can also build VRT manually:")
        print("  gdalbuildvrt africa_srtm.vrt path/to/*.tif")
        return False
    
    # Get tiles
    tiles = []
    
    if tile_list_file and os.path.exists(tile_list_file):
        # Read from tile list file
        print(f"Reading tile list from: {tile_list_file}")
        with open(tile_list_file, 'r') as f:
            for line in f:
                tile = line.strip()
                if tile and os.path.exists(tile):
                    tiles.append(tile)
    else:
        # Search for tiles in directory
        search_dir = input_dir if input_dir else "."
        print(f"Searching for SRTM tiles in: {os.path.abspath(search_dir)}")
        
        if recursive:
            # Recursive search
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in ['.tif', '.tiff', '.hgt', '.dem']):
                        full_path = os.path.join(root, file)
                        tiles.append(full_path)
        else:
            # Non-recursive search
            tiles = find_srtm_tiles(search_dir)
    
    if not tiles:
        print("\n❌ ERROR: No SRTM tiles found!")
        print("Make sure you have downloaded SRTM files with names like:")
        print("  N00E006.tif, N01E007.hgt, srtm_30_e020_n40.tif, etc.")
        print("Or provide a tile list file with: --tile-list tiles.txt")
        return False
    
    print(f"\n✅ Found {len(tiles)} SRTM tile(s)")
    
    # Show first few tiles
    print("\nFirst 10 tiles:")
    for i, tile in enumerate(tiles[:10]):
        size_mb = os.path.getsize(tile) / (1024 * 1024) if os.path.exists(tile) else 0
        print(f"  {i+1:3d}. {os.path.basename(tile)} ({size_mb:.1f} MB)")
    
    if len(tiles) > 10:
        print(f"  ... and {len(tiles) - 10} more")
    
    # Create VRT
    print(f"\nCreating VRT mosaic: {output_vrt}")
    print(f"This may take a while for {len(tiles)} tiles...")
    
    start_time = time.time()
    
    # Build GDAL command
    cmd = ["gdalbuildvrt", output_vrt]
    
    # Add optional parameters
    cmd.extend(["-input_file_list", "tile_list.txt"])
    
    # Create temporary tile list file
    with open("tile_list.txt", "w") as f:
        for tile in tiles:
            f.write(f"{tile}\n")
    
    try:
        # Execute GDAL command
        print(f"\nExecuting: {' '.join(cmd[:3])} ... [truncated]")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Get VRT information
            vrt_size = os.path.getsize(output_vrt) / 1024  # KB
            elapsed = time.time() - start_time
            
            print(f"\n✅ Successfully created VRT: {output_vrt}")
            print(f"   Size: {vrt_size:.1f} KB")
            print(f"   Time: {elapsed:.1f} seconds")
            print(f"   Tiles: {len(tiles)}")
            
            # Get spatial info
            print(f"\n📊 VRT Information:")
            info_cmd = ["gdalinfo", output_vrt]
            info_result = subprocess.run(info_cmd, capture_output=True, text=True)
            
            # Extract key info
            info_lines = info_result.stdout.split('\n')
            for line in info_lines[:15]:  # Show first 15 lines
                if "Size is" in line or "Coordinate System" in line or "Upper Left" in line or "Lower Right" in line:
                    print(f"   {line}")
            
            # Show commands for next steps
            print(f"\n🎯 NEXT STEPS:")
            print(f"1. View VRT (small file, references all tiles):")
            print(f"   gdalinfo {output_vrt}")
            print(f"   qgis {output_vrt}  # Open in QGIS")
            
            print(f"\n2. Create single GeoTIFF (LARGE FILE - 15-20GB):")
            print(f"   gdal_translate {output_vrt} africa_srtm_complete.tif \\")
            print(f"     -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS")
            
            print(f"\n3. Create smaller overview (pyramid for faster display):")
            print(f"   gdaladdo -r average {output_vrt} 2 4 8 16")
            
            print(f"\n4. Reproject to different CRS (e.g., Africa Albers):")
            print(f"   gdalwarp {output_vrt} africa_srtm_aea.tif \\")
            print(f"     -t_srs '+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25' \\")
            print(f"     -co COMPRESS=LZW")
            
            # Clean up temp file
            if os.path.exists("tile_list.txt"):
                os.remove("tile_list.txt")
            
            return True
            
        else:
            print(f"\n❌ ERROR creating VRT:")
            print(f"GDAL Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def create_geotiff_from_vrt(vrt_file, output_tif="africa_srtm.tif", 
                           compress=True, resample=None):
    """
    Convert VRT to single GeoTIFF
    """
    print(f"\nConverting VRT to GeoTIFF: {output_tif}")
    
    cmd = ["gdal_translate", vrt_file, output_tif]
    
    if compress:
        cmd.extend(["-co", "COMPRESS=LZW", "-co", "PREDICTOR=2"])
    
    cmd.extend(["-co", "TILED=YES", "-co", "BIGTIFF=YES"])
    cmd.extend(["-co", "NUM_THREADS=ALL_CPUS"])
    
    if resample:
        cmd.extend(["-r", resample])
    
    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            size_gb = os.path.getsize(output_tif) / (1024**3)
            print(f"\n✅ Created GeoTIFF: {output_tif}")
            print(f"   Size: {size_gb:.2f} GB")
            return True
        else:
            print(f"\n❌ ERROR: {result.stderr}")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Build VRT mosaic from SRTM tiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                            # Find tiles in current directory
  %(prog)s --input /path/to/tiles     # Specify tiles directory
  %(prog)s --tile-list tiles.txt      # Use list of tile files
  %(prog)s --output africa.vrt        # Specify output filename
  %(prog)s --recursive                # Search subdirectories
  %(prog)s --create-tif               # Also create single GeoTIFF
  
  # After creating VRT, you can manually run:
  gdal_translate africa_srtm.vrt africa.tif -co COMPRESS=LZW -co BIGTIFF=YES
        """
    )
    
    parser.add_argument("--input", "-i", 
                       help="Directory containing SRTM tiles (default: current)")
    parser.add_argument("--output", "-o", default="africa_srtm.vrt",
                       help="Output VRT filename (default: africa_srtm.vrt)")
    parser.add_argument("--tile-list", "-t",
                       help="Text file with list of tile files (one per line)")
    parser.add_argument("--recursive", "-r", action="store_true",
                       help="Search subdirectories recursively")
    parser.add_argument("--create-tif", action="store_true",
                       help="Also create single GeoTIFF (warning: large file!)")
    parser.add_argument("--compress", action="store_true", default=True,
                       help="Use LZW compression for GeoTIFF (default: True)")
    parser.add_argument("--resample", choices=["average", "bilinear", "cubic"],
                       help="Resampling method for GeoTIFF")
    
    args = parser.parse_args()
    
    # Create VRT
    success = create_vrt_mosaic(
        input_dir=args.input,
        output_vrt=args.output,
        tile_list_file=args.tile_list,
        recursive=args.recursive
    )
    
    # Optionally create GeoTIFF
    if success and args.create_tif and os.path.exists(args.output):
        # Generate GeoTIFF filename from VRT name
        tif_name = args.output.replace('.vrt', '.tif')
        if tif_name == args.output:  # If no .vrt extension
            tif_name = args.output + '.tif'
        
        print(f"\n{'='*80}")
        print("CREATING SINGLE GEOTIFF FILE")
        print(f"{'='*80}")
        print("⚠️  WARNING: This will create a VERY LARGE file (15-20 GB)")
        print("   Make sure you have enough disk space!")
        print(f"   Output file: {tif_name}")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() in ['y', 'yes']:
            create_geotiff_from_vrt(
                vrt_file=args.output,
                output_tif=tif_name,
                compress=args.compress,
                resample=args.resample
            )
        else:
            print("Skipping GeoTIFF creation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())