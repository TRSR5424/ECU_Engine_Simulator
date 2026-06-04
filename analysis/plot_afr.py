"""Plot AFR for an experiment folder (wrapper around plot_helpers).

Usage:
	python plot_afr.py /path/to/experiment
"""
import argparse
import os

from analysis.plot_helpers import find_csv_in_folder, load_data, plot_afr


def run_folder(folder: str):
	csv = find_csv_in_folder(folder)
	df = load_data(csv)
	out_path = os.path.join(folder, 'afr.png')
	plot_afr(df, out_path)


def main():
	p = argparse.ArgumentParser()
	p.add_argument('folder', help='Experiment folder containing CSV')
	args = p.parse_args()
	run_folder(args.folder)


if __name__ == '__main__':
	main()

