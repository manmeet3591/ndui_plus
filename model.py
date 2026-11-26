"""SwinIR configuration used for the NDUI+ DMSP-OLS/VIIRS cross-calibration.

The network code in SwinIR_train_function.py is the original SwinIR implementation
(Liang et al., 2021; https://github.com/JingyunLiang/SwinIR, models/network_swinir.py)
without architectural changes. Only two constructor defaults differ from upstream
(in_chans 3 -> 1, upscale 2 -> 1); every value used is passed explicitly below.

Usage
-----
    from model import build_swinir, load_cell_model
    net = load_cell_model("weights/best_model_lats_40.0_late_45.0_lons_-90.0_lone_-85.0.pth")
"""
import torch

from SwinIR_train_function import SwinIR

# Exact hyperparameters used to train every weight file deposited on Zenodo
# (doi:10.5281/zenodo.24545916) and every city model in this repository.
SWINIR_CONFIG = dict(
    upscale=1,                     # same grid in and out (VIIRS regridded to the DMSP grid)
    in_chans=1,                    # single band: VIIRS avg_rad -> DMSP stable_lights
    img_size=(30, 30),             # 30 x 30 pixel patches (~28 km at 927.67 m)
    patch_size=1,
    window_size=5,                 # 5 x 5 attention windows, shifted every other block
    img_range=1.0,                 # inputs are pre-scaled to [0, 1]
    depths=[6, 6, 6, 6],           # 4 residual Swin transformer blocks x 6 Swin layers
    embed_dim=60,
    num_heads=[6, 6, 6, 6],
    mlp_ratio=2,
    drop_path_rate=0.1,
    upsampler="pixelshuffledirect",  # with upscale=1: one 3x3 conv to 1 channel
    resi_connection="1conv",
)

PATCH_SIZE = 30
TILE_PIXELS = 600                  # 600 x 600 DMSP pixels per 5 x 5 degree cell -> 400 patches
DMSP_SCALE_M = 927.67
VIIRS_SCALE_M = 463.83


def build_swinir(device="cpu"):
    """Return an untrained SwinIR with the NDUI+ configuration (882,385 trainable parameters)."""
    return SwinIR(**SWINIR_CONFIG).to(device)


def load_cell_model(weight_path, device="cpu"):
    """Load one regional weight file (a 5 x 5 degree cell or a city-centred box)."""
    net = build_swinir(device)
    net.load_state_dict(torch.load(weight_path, map_location=device))
    net.eval()
    return net


def cell_weight_name(lat_center, lon_center, buffer=2.5):
    """Weight file name for the 5 x 5 degree cell centred at (lat_center, lon_center).

    Cell centres are on the grid lat = -87.5, -82.5, ..., lon = -177.5, -172.5, ...
    """
    lats, late = float(lat_center) - buffer, float(lat_center) + buffer
    lons, lone = float(lon_center) - buffer, float(lon_center) + buffer
    return f"best_model_lats_{lats}_late_{late}_lons_{lons}_lone_{lone}.pth"


def cell_center(lat, lon):
    """Centre of the 5 x 5 degree cell that contains the point (lat, lon)."""
    import math
    return math.floor(lat / 5) * 5 + 2.5, math.floor(lon / 5) * 5 + 2.5


if __name__ == "__main__":
    net = build_swinir()
    print("parameters:", sum(p.numel() for p in net.parameters()))
    x = torch.rand(4, 1, PATCH_SIZE, PATCH_SIZE)
    print("output shape:", tuple(net(x).shape))
