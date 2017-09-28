from ..IOUtil import doc_dir, result_dir
import os

if __name__ == "__main__":
	base_dir = os.path.join(result_dir, '360/mapping')
	filepath = os.path.join(base_dir, 'predicates_map_human_1.txt')
	name_map = {}
	for line in file(filepath):
		p = line.split('\t')
		name = p[1]
		if not name in name_map:
			name_map[name] = []
		for value in p[2:]:
			p2 = value.split(" ")
			o_name = p2[0]
			name_map[name].append(o_name)
	outf = file(os.path.join(base_dir, 'name_map_1.txt'), 'w')
	for name in name_map:
		if len(name_map[name]) == 1:
			print "error %s" %(name)
			continue
		else:
			o_names = list(set(name_map[name]))
			outf.write("%s\t%s\n" %(name, "\t".join(name_map[name])))
	outf.close()
