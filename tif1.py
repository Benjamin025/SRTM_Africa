#!/usr/bin/env python3
"""
Custom converter for your specific VRT file
"""

import subprocess
import os
import sys

# Your specific paths
VRT_FILE = "/home/benjamin/Documents/Benjamin/srtm/Africa/srtm_africa/africa_srtm_complete/africa_srtm.vrt"
OUTPUT_DIR = "/home/benjamin/Documents/Benjamin/srtm/Africa/srtm_africa/africa_srtm_complete"
OUTPUT_TIF = os.path.join(OUTPUT_DIR, "africa_30m_complete.tif")

def main():
    print("=" * 80)
    print("AFRICA SRTM VRT to GeoTIFF CONVERSION")
    print("=" * 80)
    
    # Check if VRT exists
    if not os.path.exists(VRT_FILE):
        print(f"❌ ERROR: VRT file not found!")
        print(f"   Looking for: {VRT_FILE}")
        print("\nPlease check the path and make sure:")
        print(f"1. The VRT file exists at that location")
        print(f"2. The file is named 'africa_srtm.vrt'")
        print(f"3. You have read permissions")
        
        # Try to find it
        print(f"\n📁 Looking for VRT files in the directory...")
        vrt_dir = os.path.dirname(VRT_FILE)
        if os.path.exists(vrt_dir):
            vrt_files = [f for f in os.listdir(vrt_dir) if f.endswith('.vrt')]
            if vrt_files:
                print(f"Found VRT files: {', '.join(vrt_files)}")
                print(f"\nTry running: python tif.py {os.path.join(vrt_dir, vrt_files[0])}")
        return 1
    
    print(f"✓ VRT file found: {VRT_FILE}")
    print(f"  Size: {os.path.getsize(VRT_FILE) / 1024:.1f} KB")
    
    # Change to output directory
    os.chdir(OUTPUT_DIR)
    print(f"\n📁 Working in: {os.getcwd()}")
    
    # Show disk space
    print("\n💾 Checking disk space...")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        print(f"  Free space: {free_gb:.1f} GB")
        
        if free_gb < 30:
            print(f"⚠️  WARNING: Only {free_gb:.1f} GB free. Need at least 30 GB!")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() not in ['y', 'yes']:
                return 1
    except:
        pass
    
    # Build command
    cmd = [
        "gdal_translate",
        "africa_srtm.vrt",  # Now we're in the directory
        "africa_30m.tif",
        "-co", "COMPRESS=LZW",
        "-co", "PREDICTOR=2",
        "-co", "TILED=YES",
        "-co", "BLOCKXSIZE=256",
        "-co", "BLOCKYSIZE=256",
        "-co", "BIGTIFF=YES",
        "-co", "NUM_THREADS=ALL_CPUS",
        "-stats"
    ]
    
    print(f"\n🔨 Conversion command:")
    print(" ".join(cmd))
    
    print(f"\n⏳ This will take 15-60 minutes depending on your system...")
    print("   Output file: africa_30m.tif")
    print("   Expected size: 15-25 GB")
    
    # Run the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ GeoTIFF created successfully!")
            
            # Check file size
            if os.path.exists("africa_30m.tif"):
                size_gb = os.path.getsize("africa_30m.tif") / (1024**3)
                print(f"📊 File size: {size_gb:.2f} GB")
                
                # Create overviews
                print(f"\n📐 Creating pyramid overviews...")
                overview_cmd = [
                    "gdaladdo", "-r", "average",
                    "africa_30m.tif", "2", "4", "8", "16"
                ]
                subprocess.run(overview_cmd, capture_output=True, text=True)
                print(f"✅ Overviews created")
                
                # Show final info
                print(f"\n🎉 Conversion complete!")
                print(f"File: {os.path.abspath('africa_30m.tif')}")
                print(f"Size: {size_gb:.2f} GB")
                
            return 0
        else:
            print(f"\n❌ Conversion failed!")
            print(f"Error: {result.stderr}")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())