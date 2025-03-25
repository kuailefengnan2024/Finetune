import torch
x = torch.randn(10, 10, dtype=torch.float8_e4m3fn, device="cuda")
print(x)