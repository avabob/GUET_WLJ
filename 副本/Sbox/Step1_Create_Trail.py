# Algorithm 2 presented in paper "Applyint MILP Method to Searching Integral 
# Distinguishers based on Division Property for 6 Lightweight Block Ciphers"
# Regarding to the paper, please refer to https://eprint.iacr.org/2016/857
# For more information, feedback or questions, pleast contact at xiangzejun@iie.ac.cn

# Implemented by Xiang Zejun, State Key Laboratory of Information Security, 
# Institute Of Information Engineering, CAS



from sbox import Sbox


def input_sbox():
	# 输入sbox字符串
	sbox_input = input("S盒: ")
	# 移除方括号并按逗号分割字符串
	sbox_input = sbox_input.strip()[1:-1]  # 去掉两边的方括号
	# 将每个十六进制数转换为整数
	sbox = [int(x.strip(), 16) for x in sbox_input.split(',')]
	# 输出结果
	return sbox

if __name__ == "__main__":
	cipher_name = input("算法名称: ")
	sbox = input_sbox()

	present = Sbox(sbox)

	filename = cipher_name + "_DivisionTrails.txt"

	present.PrintfDivisionTrails(filename)
