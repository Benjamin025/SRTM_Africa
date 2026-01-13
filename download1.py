#!/usr/bin/env python3
"""
COMPLETE Africa SRTM Download - All available tiles
"""

import os
import requests
import time
from tqdm import tqdm
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_all_africa_tiles():
    """Generate ALL possible Africa tile coordinates"""
    tiles = []
    
    # Africa bounding box: -26°W to 60°E, -37°S to 37°N
    # Convert to tile coordinates
    
    # Northern Hemisphere (0°N to 37°N)
    for lat in range(0, 38):  # 0 to 37 degrees North
        # West of Greenwich (-26°W to -1°W)
        for lon in range(1, 27):  # 1 to 26 degrees West
            tiles.append(f"N{lat:02d}W{lon:03d}")
        # East of Greenwich (0°E to 60°E)
        for lon in range(0, 61):  # 0 to 60 degrees East
            tiles.append(f"N{lat:02d}E{lon:03d}")
    
    # Southern Hemisphere (1°S to 37°S)
    for lat in range(1, 38):  # 1 to 37 degrees South
        # West of Greenwich
        for lon in range(1, 27):
            tiles.append(f"S{lat:02d}W{lon:03d}")
        # East of Greenwich
        for lon in range(0, 61):
            tiles.append(f"S{lat:02d}E{lon:03d}")
    
    print(f"Generated {len(tiles)} total tile coordinates for Africa")
    return tiles

def check_tile_exists(tile, base_url, timeout=10):
    """Check if a tile exists on the server"""
    # Try with leading zeros first
    url = f"{base_url}/{tile}.tif"
    
    try:
        response = requests.head(url, timeout=timeout)
        if response.status_code == 200:
            return tile, True
        elif response.status_code == 404:
            # Try without leading zeros
            # Convert N00E006 to N0E6
            import re
            match = re.match(r'([NS])(\d{2})([EW])(\d{3})', tile)
            if match:
                lat_dir = match.group(1)
                lat_num = int(match.group(2))
                lon_dir = match.group(3)
                lon_num = int(match.group(4))
                
                alt_tile = f"{lat_dir}{lat_num}{lon_dir}{lon_num}"
                alt_url = f"{base_url}/{alt_tile}.tif"
                
                alt_response = requests.head(alt_url, timeout=timeout)
                if alt_response.status_code == 200:
                    return alt_tile, True
    except:
        pass
    
    return tile, False

def download_complete_africa():
    """Download ALL available Africa SRTM tiles"""
    
    output_dir = "africa_srtm_complete"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    
    print("=" * 80)
    print("COMPLETE AFRICA SRTM 30m DOWNLOAD")
    print("Downloading ALL available tiles for Africa")
    print("=" * 80)
    
    # Generate all possible tiles
    all_tiles = generate_all_africa_tiles()
    
    # Base URL
    base_url = "https://opentopography.s3.sdsc.edu/raster/SRTM_GL1/SRTM_GL1_srtm"
    
    # Step 1: Discover which tiles actually exist
    print(f"\nStep 1/3: Checking which of {len(all_tiles)} tiles exist...")
    
    existing_tiles = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_tile_exists, tile, base_url): tile for tile in all_tiles}
        
        with tqdm(total=len(all_tiles), desc="Checking tiles") as pbar:
            for future in as_completed(futures):
                tile, exists = future.result()
                if exists:
                    existing_tiles.append(tile)
                pbar.update(1)
    
    print(f"\n✓ Found {len(existing_tiles)} existing tiles")
    
    # Save the list of existing tiles
    with open("africa_existing_tiles.txt", "w") as f:
        for tile in sorted(existing_tiles):
            f.write(f"{tile}\n")
    
    print(f"Tile list saved to: africa_existing_tiles.txt")
    
    # Step 2: Download all existing tiles
    print(f"\nStep 2/3: Downloading {len(existing_tiles)} tiles...")
    
    def download_tile(tile):
        """Download a single tile"""
        filename = f"{tile}.tif"
        url = f"{base_url}/{filename}"
        
        # Skip if already exists and is valid
        if os.path.exists(filename):
            try:
                if os.path.getsize(filename) > 1000000:  # >1MB
                    return tile, True, os.path.getsize(filename)
            except:
                pass
        
        try:
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filename)
                if file_size > 1000000:  # Valid file should be >1MB
                    return tile, True, file_size
                else:
                    os.remove(filename)
                    return tile, False, 0
            else:
                return tile, False, 0
        except:
            return tile, False, 0
    
    successful = []
    failed = []
    total_downloaded = 0
    
    # Download in batches
    batch_size = 50
    for i in range(0, len(existing_tiles), batch_size):
        batch = existing_tiles[i:i+batch_size]
        print(f"\nDownloading batch {i//batch_size + 1}/{(len(existing_tiles)+batch_size-1)//batch_size}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(download_tile, tile): tile for tile in batch}
            
            for future in as_completed(futures):
                tile, success, file_size = future.result()
                if success:
                    successful.append(tile)
                    total_downloaded += file_size
                    print(f"  ✓ {tile}.tif ({file_size/(1024*1024):.1f} MB)")
                else:
                    failed.append(tile)
    
    # Step 3: Summary and post-processing
    print(f"\n{'='*80}")
    print("DOWNLOAD COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Successfully downloaded: {len(successful)} tiles")
    print(f"✗ Failed: {len(failed)} tiles")
    print(f"📊 Total data: {total_downloaded/(1024**3):.2f} GB")
    
    # Save detailed report
    report = {
        "total_tiles_generated": len(all_tiles),
        "tiles_found_on_server": len(existing_tiles),
        "tiles_successfully_downloaded": len(successful),
        "tiles_failed": len(failed),
        "successful_tiles": successful,
        "failed_tiles": failed[:100],  # Limit to first 100
        "total_data_gb": total_downloaded/(1024**3),
        "server": base_url,
        "download_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("africa_download_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Detailed report saved to: africa_download_report.json")
    
    # Show downloaded files
    tif_files = [f for f in os.listdir('.') if f.endswith('.tif')]
    if tif_files:
        print(f"\n📁 Downloaded {len(tif_files)} .tif files")
        print("First 20 files:")
        for f in sorted(tif_files)[:20]:
            size = os.path.getsize(f) / (1024*1024)
            print(f"  {f} ({size:.1f} MB)")
        
        if len(tif_files) > 20:
            print(f"  ... and {len(tif_files) - 20} more files")
    
    # Create mosaic automatically
    if len(tif_files) >= 5:  # If we have at least 5 tiles
        print(f"\n{'='*80}")
        print("CREATING CONTINENT MOSAIC")
        print(f"{'='*80}")
        
        try:
            import subprocess
            
            # Create VRT (virtual mosaic)
            print("Creating virtual mosaic (africa.vrt)...")
            subprocess.run(["gdalbuildvrt", "africa.vrt", "*.tif"], check=False)
            
            if os.path.exists("africa.vrt"):
                print("✓ Created africa.vrt")
                
                # Get info about the mosaic
                print("\nMosaic information:")
                subprocess.run(["gdalinfo", "africa.vrt"], check=False)
                
                print("\nTo create single GeoTIFF file:")
                print("gdal_translate africa.vrt africa_complete.tif \\")
                print("  -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES")
                print("\nEstimated size: ~15-20 GB")
            else:
                print("✗ Failed to create mosaic")
                print("Install GDAL: sudo apt install gdal-bin")
                
        except Exception as e:
            print(f"✗ Error creating mosaic: {e}")
            print("Install GDAL: sudo apt install gdal-bin")
    
    return successful

if __name__ == "__main__":
    download_complete_africa()