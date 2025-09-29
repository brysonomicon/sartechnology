#!/usr/bin/env python3
"""
Simple Camera Serial Number Detection Test for Jetson/Ubuntu

This script focuses specifically on detecting camera serial numbers
using the same approach as cam_utils.py for camera detection.
Designed for Ubuntu/Jetson systems with V4L2 support.

Usage: python camera-serial-simple.py
"""

import os
import subprocess
import sys
from typing import Optional, List, Tuple


def get_camera_serial(device: str) -> Optional[str]:
    """
    Try to get the serial number for a /dev/video* device.
    Uses sysfs first, then falls back to udevadm.
    """
    print(f"  Looking for serial of {device}...")
    
    # Method 1: Try sysfs path
    try:
        # Get the real device path
        base = os.path.realpath(f"/sys/class/video4linux/{os.path.basename(device)}/device")
        serial_path = os.path.join(base, "serial")
        
        print(f"    Checking sysfs: {serial_path}")
        
        if os.path.exists(serial_path):
            with open(serial_path, "r") as f:
                serial = f.read().strip()
                if serial:
                    print(f"    Found via sysfs: {serial}")
                    return serial
        else:
            print(f"    sysfs serial file not found")
    except Exception as e:
        print(f"    sysfs error: {e}")
    
    # Method 2: Try udevadm
    try:
        print(f"    Trying udevadm...")
        result = subprocess.run(
            ["udevadm", "info", "--query=all", "--name", device],
            capture_output=True, 
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "ID_SERIAL=" in line:
                    serial = line.split("ID_SERIAL=")[-1].strip()
                    if serial:
                        print(f"    Found via udevadm: {serial}")
                        return serial
                elif "ID_SERIAL_SHORT=" in line:
                    serial = line.split("ID_SERIAL_SHORT=")[-1].strip()
                    if serial:
                        print(f"    Found via udevadm (short): {serial}")
                        return serial
            print(f"    udevadm found no serial")
        else:
            print(f"    udevadm failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"    udevadm timed out")
    except FileNotFoundError:
        print(f"    udevadm not found")
    except Exception as e:
        print(f"    udevadm error: {e}")
    
    print(f"    No serial found for {device}")
    return None


def get_camera_info(device: str) -> Optional[dict]:
    """
    Get additional camera information via udevadm
    """
    info = {
        "vendor": None,
        "model": None,
        "product": None,
        "bus_info": None
    }
    
    try:
        result = subprocess.run(
            ["udevadm", "info", "--query=all", "--name", device],
            capture_output=True, 
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "ID_VENDOR=" in line:
                    info["vendor"] = line.split("ID_VENDOR=")[-1].strip()
                elif "ID_MODEL=" in line:
                    info["model"] = line.split("ID_MODEL=")[-1].strip()
                elif "ID_USB_MODEL=" in line:
                    info["product"] = line.split("ID_USB_MODEL=")[-1].strip()
                elif "ID_PATH=" in line:
                    info["bus_info"] = line.split("ID_PATH=")[-1].strip()
    except Exception as e:
        print(f"    WARNING: Could not get device info: {e}")
    
    return info


def detect_cameras_with_serials(max_devices: int = 12) -> List[Tuple[str, Optional[str], dict]]:
    """
    Detect cameras and their serial numbers, similar to find_working_cameras approach
    """
    print("Scanning for cameras and serial numbers...\n")
    
    cameras_found = []
    
    for i in range(max_devices):
        device = f"/dev/video{i}"
        
        # Check if device exists (like cam_utils.py does)
        if not os.path.exists(device):
            continue
        
        print(f"Found device: {device}")
        
        # Get serial number
        serial = get_camera_serial(device)
        
        # Get additional info
        info = get_camera_info(device)
        
        cameras_found.append((device, serial, info))
        
        print(f"  Summary:")
        print(f"     Device: {device}")
        print(f"     Serial: {serial or 'Not found'}")
        print(f"     Vendor: {info.get('vendor', 'Unknown')}")
        print(f"     Model: {info.get('model', 'Unknown')}")
        print(f"     Product: {info.get('product', 'Unknown')}")
        print("")
    
    return cameras_found


def main():
    """Main test execution"""
    print("Camera Serial Number Detection Test")
    print("=" * 45)
    print("Jetson/Ubuntu camera detection using cam_utils.py approach\n")
    
    try:
        # Detect cameras with serials
        cameras = detect_cameras_with_serials(max_devices=12)
        
        # Print summary
        print("SERIAL DETECTION SUMMARY")
        print("=" * 30)
        
        if not cameras:
            print("ERROR: No camera devices found!")
            print("   Make sure cameras are connected and /dev/video* devices exist.")
        else:
            cameras_with_serials = [c for c in cameras if c[1] is not None]
            
            print(f"Total devices found: {len(cameras)}")
            print(f"Devices with serials: {len(cameras_with_serials)}")
            print(f"Devices without serials: {len(cameras) - len(cameras_with_serials)}")
            
            if cameras_with_serials:
                print(f"\nCameras with serial numbers:")
                for device, serial, info in cameras_with_serials:
                    vendor_model = f"{info.get('vendor', 'Unknown')} {info.get('model', 'Unknown')}"
                    print(f"   {device}: {serial} ({vendor_model})")
            
            cameras_without_serials = [c for c in cameras if c[1] is None]
            if cameras_without_serials:
                print(f"\nCameras without serial numbers:")
                for device, _, info in cameras_without_serials:
                    vendor_model = f"{info.get('vendor', 'Unknown')} {info.get('model', 'Unknown')}"
                    print(f"   {device}: No serial found ({vendor_model})")
        
        print(f"\nTips:")
        print(f"   - Virtual cameras (like OBS) typically don't have serial numbers")
        print(f"   - Built-in CSI cameras may not expose serial numbers")
        print(f"   - USB cameras usually have serial numbers accessible via udevadm")
        print(f"   - Jetson cameras may use CSI interface (/dev/video0, /dev/video1)")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nERROR during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()