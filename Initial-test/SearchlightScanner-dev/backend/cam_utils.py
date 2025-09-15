import cv2
import os


def find_working_cameras(desired_resolutions, max_devices=12, max_cams=6):
    """
    Scan /dev/video* and return up to `max_cams` working camera paths.

    Args:
        max_devices (int): How many /dev/video* devices to check (default: 12)
        max_cams (int): How many working cameras to return (default: 6)
        desired_resolutions (list of tuples): Resolutions to try in order of preference

    Returns:
        List[str]: List of working camera device paths
    """
    working_cams = []

    for i in range(max_devices):
        device = f"/dev/video{i}"
        if not os.path.exists(device):
            continue

        print(f"Trying {device}...")

        if try_camera(device, desired_resolutions, "MJPG", fps=15):
            print(f"[{device}] MJPG works")
            working_cams.append(device)
        elif try_camera(device, desired_resolutions, "YUYV", fps=15):
            print(f"[{device}] MJPG failed, using YUYV")
            working_cams.append(device)
        else:
            print(f"[{device}] Failed with both MJPG and YUYV")

        if len(working_cams) >= max_cams:
            break

    return working_cams


def try_camera(device, resolutions, codec, fps=30):
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*codec))
    cap.set(cv2.CAP_PROP_FPS, fps)

    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] >= 100:
            print(f"✓ {device} works at {width}x{height} with {codec}")
            cap.release()
            return True

    cap.release()
    return False
