import argparse
import numpy as np
from scipy import stats
from openpyxl import load_workbook


def parse_args():
	""" Parse command line arguments """
	parser = argparse.ArgumentParser(
		description="")

	parser.add_argument(
		"--association", required=True,
		help="Input association matrix Excel file")

	parser.add_argument(
		"--relatedness", required=True,
		help="Input relatedness matrix Excel file")

	parser.add_argument(
		"--permutations", default=1000, type=int,
		help="Number of permutations.")

	args = parser.parse_args()
	return args

def read_excel_matrix_as_edgelist(file1):
	wb = load_workbook(filename = file1)
	sheet = wb.active
	d1 = {}
	id_idx = []
	row_num = 0
	row_id = None
	for row in sheet.iter_rows():
		cell_num = 0
		for cell in row:
			if row_num == 0 and cell_num == 0:
				cell_num += 1
				continue
			else:
				if row_num == 0:
					id_idx.append(cell.value)
				else:
					if cell_num == 0:
						row_id = cell.value
					else:
						col_id = id_idx[cell_num - 1]
						if col_id == row_id:
							pass
						else:
							if (col_id, row_id) not in d1:
								d1[(col_id, row_id)] = cell.value
				cell_num += 1
		row_num += 1
	return d1

def main():
	args = parse_args()

	assoc = read_excel_matrix_as_edgelist(args.association)
	relate = read_excel_matrix_as_edgelist(args.relatedness)

	assoc1 = {k: assoc[k] for k in relate if k in assoc}
	relate1 = {k: relate[k] for k in assoc1 if k in relate}

	assoc_values = list(assoc1.values())

	p95 = np.percentile(np.array(assoc_values), 95)
	p5 = np.percentile(np.array(assoc_values), 5)

	pref_count = 0
	casual_count = 0
	avoid_count = 0
	for x in assoc_values:
		if x > p95:
			pref_count += 1
		elif x < p5:
			avoid_count += 1
		else:
			casual_count += 1
	other_count = casual_count + avoid_count
	temp_pref = []
	temp_not = []

	print("Preferred associates (no particular order):")
	for pair in assoc1:
		if assoc1[pair] > p95:
			temp_pref.append(relate1[pair])
			print("{}: {}".format(pair, assoc1[pair]))
		else:
			temp_not.append(relate1[pair])

	empirical_pref = np.mean(temp_pref)
	empirical_not = np.mean(temp_not)

	print(np.mean(temp_pref), np.mean(temp_not))

	print(pref_count, avoid_count, casual_count)

	relate_values = list(relate1.values())

	#without replacement
	pref_dist = []
	not_dist = []
	for i in range(0, args.permutations):
		k = np.random.permutation(relate_values)
		pref1 = k[:pref_count]
		not1 = k[pref_count:]

		pref_dist.append(np.mean(pref1))
		not_dist.append(np.mean(not1))

	#with replacement
	pref_with_repl = []
	not_with_repl = []
	for i in range(0, args.permutations):
		pref_with_repl.append(np.mean(np.random.choice(relate_values, pref_count)))
		not_with_repl.append(np.mean(np.random.choice(relate_values, other_count)))

	print("")

	print(
		"Emprical preferred mean: {}. Percentile of {} permutations without replacement: {}".format(
			empirical_pref, args.permutations, stats.percentileofscore(
				pref_dist, empirical_pref, kind="strict")))

	print(
		"Emprical not preferred mean: {}. Percentile of {} permutations without replacement: {}".format(
			empirical_not, args.permutations, stats.percentileofscore(
				not_dist, empirical_not, kind="strict")))

	print("")

	print(
		"Emprical preferred mean: {}. Percentile of {} permutations with replacement: {}".format(
			empirical_pref, args.permutations, stats.percentileofscore(
				pref_with_repl, empirical_pref, kind="strict")))

	print(
		"Emprical not preferred mean: {}. Percentile of {} permutations with replacement: {}".format(
			empirical_not, args.permutations, stats.percentileofscore(
				not_with_repl, empirical_not, kind="strict")))


if __name__ == "__main__":
	main()
