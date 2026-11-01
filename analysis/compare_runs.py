"""Compare two experiment folders and write comparison plots into both.

Usage:
	python compare_runs.py /path/to/expA /path/to/expB
"""
import argparse
import os
import sys
from pathlib import Path

# Always ensure project root is on sys.path so `from analysis import ...` works
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
	sys.path.insert(0, project_root)

from analysis.plot_helpers import (
	find_csv_in_folder,
	load_data,
	plot_comparison,
	ensure_dir,
)
from analysis.plot_helpers import plot_afr_vs_rpm


def compare(a_folder: str, b_folder: str):
	"""Run the compare operation."""
	csv_a = find_csv_in_folder(a_folder)
	csv_b = find_csv_in_folder(b_folder)
	df_a = load_data(csv_a)
	df_b = load_data(csv_b)
	name_a = os.path.basename(os.path.normpath(a_folder))
	name_b = os.path.basename(os.path.normpath(b_folder))
	out_a = os.path.join(a_folder, f"{name_b}_Comparison")
	out_b = os.path.join(b_folder, f"{name_a}_Comparison")
	ensure_dir(out_a)
	ensure_dir(out_b)

	# columns to compare (use measured if present)
	afr_col = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df_a.columns else 'air_fuel_ratio'
	plot_comparison(df_a, df_b, afr_col, os.path.join(out_a, 'afr_comparison.png'), labels=(name_a, name_b))
	plot_comparison(df_a, df_b, 'engine_speed_rpm', os.path.join(out_a, 'rpm_comparison.png'), labels=(name_a, name_b))
	plot_comparison(df_a, df_b, 'throttle', os.path.join(out_a, 'throttle_comparison.png'), labels=(name_a, name_b))

	# scatter AFR vs RPM colored by throttle for each run (saved separately)
	plot_afr_vs_rpm(df_a, os.path.join(out_a, f'{name_a}_afr_vs_rpm.png'))
	plot_afr_vs_rpm(df_b, os.path.join(out_a, f'{name_b}_afr_vs_rpm.png'))

	# copy into other folder so both see the comparison
	import shutil

	# If the two output folders are different, copy the generated files so both experiments have them.
	if os.path.abspath(out_a) != os.path.abspath(out_b):
		for fname in ('afr_comparison.png', 'rpm_comparison.png', 'throttle_comparison.png'):
			shutil.copy(os.path.join(out_a, fname), os.path.join(out_b, fname))


def main():
	"""Parse inputs and run the command-line entry point."""
	p = argparse.ArgumentParser()
	p.add_argument('-a')
	p.add_argument('-b')
	args = p.parse_args()
	
	exp1 = args.a
	exp2 = args.b
	
	if exp1 == None or exp2 == None:
		exp1 = input("Please input experiment 1: ")
		exp2 = input("Please input experiment 2: ")
  
	compare(exp1, exp2)


if __name__ == '__main__':
	main()

