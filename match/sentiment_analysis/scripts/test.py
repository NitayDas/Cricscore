import torch
print(torch.cuda.is_available())  # Should print True if GPU is detected
print(torch.cuda.device_count())  # Number of available GPUs
print(torch.cuda.get_device_name(0))

# import torch
# torch.cuda.empty_cache()  # Clears cached memory
# torch.cuda.ipc_collect()  # Frees up fragmented memory
