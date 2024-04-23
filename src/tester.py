import cv2

def check_cuda_support():
    cuda_enabled_devices = cv2.cuda.getCudaEnabledDeviceCount()
    if cuda_enabled_devices == 0:
        print("CUDA is not available.")
    else:
        print(f"CUDA is available. Found {cuda_enabled_devices} CUDA-enabled device(s).")

check_cuda_support()