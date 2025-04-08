from Reducelin import Reduce

if __name__ == "__main__":
	# cipher_name = "PRESENT"
	# sbox = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2]
	cipher_name = input("算法名称: ")
	# sbox = [0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6]
	filename_inequalities = cipher_name + "_Inequalities.txt"

	present = Reduce(filename_inequalities)
	rine = present.InequalitySizeReduce()

	filename_result = cipher_name + "_Reduce_Inequalities.txt"

	fileobj = open(filename_result, "w")
	for l in rine:
		fileobj.write(str(l) + "\n")
	fileobj.close()