"""Simple report generator for analysis outputs.

This writes a short text summary (mean AFR, max RPM, mean throttle) into the
target experiment folder as `analysis_report.txt`.
"""
from typing import Optional

import os
import numpy as np


def generate_report(df, out_folder: str, filename: str = 'analysis_report.txt') -> str:
	afr_col = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio'
	rpm_col = 'engine_speed_rpm' if 'engine_speed_rpm' in df.columns else 'rpm'
	throttle_col = 'throttle' if 'throttle' in df.columns else None

	mean_afr = float(np.nan) if afr_col not in df.columns else float(df[afr_col].mean())
	max_rpm = float(np.nan) if rpm_col not in df.columns else float(df[rpm_col].max())
	mean_throttle = float(np.nan) if (throttle_col is None or throttle_col not in df.columns) else float(df[throttle_col].mean())

	out_path = os.path.join(out_folder, filename)
	with open(out_path, 'w') as f:
		f.write(f"Mean {afr_col}: {mean_afr:.3f}\n")
		f.write(f"Max {rpm_col}: {max_rpm:.3f}\n")
		f.write(f"Mean {throttle_col or 'N/A'}: {mean_throttle:.3f}\n")

	return out_path

