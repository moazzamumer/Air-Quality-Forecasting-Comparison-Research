"""Isolated revision tools; never modify the original notebook or data."""
import os

# Set before NumPy/PyTorch imports. Runtime reports record the actual configuration.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "2")
os.environ.setdefault("MPLBACKEND", "Agg")
