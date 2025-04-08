# H. Hadipour
# 1397/04/18
"""
变量定义与表示:  x_轮号_字节号_比特号

x_0_0_0 可能表示第 0 轮，第 0 个字节的第 0 个比特（msb，即最重要的比特）。
x_0_0_3 可能表示第 0 轮，第 0 个字节的第 3 个比特（lsb，即最不重要的比特）。

输入分组：
x_i_0_0, x_i_0_1, x_i_0_2, x_i_0_3, ..., x_i_7_0, x_i_7_1, x_i_7_2, x_i_7_3 表示第 i+1 轮输入的左半部分。
y_i_0_0, y_i_0_1, y_i_0_2, y_i_0_3, ..., y_i_7_0, y_i_7_1, y_i_7_2, y_i_7_3 表示第 i+1 轮输入的右半部分。

S-box 输入与输出：
u_i_0_0, u_i_0_1, u_i_0_2, u_i_0_3, ..., u_i_7_0, u_i_7_1, u_i_7_2, u_i_7_3 表示输入到第 i+1 轮 S 盒（S-box）的数据。
v_i_0_0, v_i_0_1, v_i_0_2, v_i_0_3, ..., v_i_7_0, v_i_7_1, v_i_7_2, v_i_7_3 表示第 i+1 轮 S 盒之后的输出。


在混合层中使用的临时变量：
a0, ..., a7,
b0, ..., b7,
c0, ..., c7,
d0, ..., d7
t0, ..., t15
"""

from gurobipy import *  # 导入 Gurobi 库，用于求解混合整数线性规划问题
import time  # 导入时间库，用于记录运行时间
import os  # 导入操作系统库，用于文件和目录操作

class Mibs:
    def __init__(self, round):
        """
        初始化 Mibs 类的实例，设置轮数、活跃比特数、块大小及置换表等基本信息。

        参数:
            round (int): MIBS 算法的轮数
        """
        self.round = round  # 设置 MIBS 轮数
        self.blocksize = 64   # 设置活跃比特数为 64 位
        self.brute_force_flag = '0'  # 设置块大小为 64，标志位为 '0' 表示不进行暴力破解
        self.shuffle = [2, 0, 3, 6, 7, 4, 5, 1]  # 定义一个置换表，用于混淆操作

        # 设置 MILP 模型的文件名，模型文件存放路径为 "model" 文件夹
        self.model_file_name = "./model/MIBS_%d.lp" % self.round  # 模型文件名包含轮数
        # 设置结果文件的文件名，存放路径为 "result" 文件夹
        self.result_file_name = "./result/result_round_%d.txt" % self.round  # 结果文件名包含轮数

        # 确保 "model" 文件夹存在，不存在则创建
        os.makedirs("./model", exist_ok=True)  # 直接使用 "./model" 来确保该文件夹存在
        # 确保 "result" 文件夹存在，不存在则创建
        os.makedirs("./result", exist_ok=True)  # 直接使用 "./result" 来确保该文件夹存在

        # 创建并立即关闭模型文件，确保文件存在
        with open(self.model_file_name, "w") as fileobj:
            pass  # 创建空文件

        # 创建并立即关闭结果文件，确保文件存在
        with open(self.result_file_name, "w") as fileobj:
            pass  # 创建空文件

    # 定义不等式的数量
    NUMBER = 9  # 用于 S-box 约束的不等式数量

    # MIBS 轮函数中 Sbox 使用的线性不等式
    sb = [
        [1, 1, 4, 1, -2, -2, -2, -2, 1],  # 不等式 1
        [0, 3, 0, 0, -1, -1, -1, -1, 1],  # 不等式 2
        [-1, -2, -2, -1, -1, -2, 4, -1, 6],  # 不等式 3
        [-1, -2, -2, -1, 5, 4, 5, 5, 0],  # 不等式 4
        [-1, -1, -1, 0, -1, 3, -2, -1, 4],  # 不等式 5
        [-1, 0, 0, -1, -2, -1, -1, 3, 3],  # 不等式 6
        [1, 0, 0, 0, 1, -1, -1, -1, 1],  # 不等式 7
        [-1, -1, 0, -1, 1, 2, 2, 1, 1],  # 不等式 8
        [0, 0, -1, 0, -1, -1, 2, -1, 2]  # 不等式 9
    ]

    def generate_continuous_arrays(self, n, total_elements=64):
        """
        生成从 0 到 total_elements - 1 的连续数组，数组长度为 n。

        参数:
            n (int): 数组的长度
            total_elements (int): 总元素个数，默认为 64
        返回:
            list: 所有可能的连续数组的列表，按降序排列
        """
        if n > total_elements:
            raise ValueError(f"数组长度不能大于总元素个数（{total_elements}）")  # 检查输入是否有效

        # 生成所有可能的连续数组
        arrays = [list(range(i, i + n)) for i in range(0, total_elements - n + 1)]
        arrays.reverse()  # 按降序排列
        return arrays

    def set_constant_bits(self):
        """
        设置常量比特位（constant_bits），这些比特位将用于后续的算法求解。
        """
        if self.brute_force_flag == '0':  # 如果选择了探测特定情况（0）
            temp = input("请输入常数的位置（请用空格分隔）:\n")  # 询问用户输入常量位的列表
            temp = temp.split()  # 将输入的字符串分割为一个列表
            constant_bits = []  # 创建一个空列表，用来存储常量位
            for element in temp:  # 遍历列表中的每个元素
                constant_bits.append(int(element) - 1)  # 将元素转换为整数并添加到常量位列表中，作为常数项的索引
                # 因为数组下标从零开始，所以要减1
            self.constant_bits = constant_bits  # 存储常量位
            self.make_model()  # 调用make_model方法生成模型
            self.solve_model()  # 调用solve_model方法求解模型

        else:  # 如果选择了暴力破解（1）
            number_of_total_states = 64  # 总状态数为64
            elements = list(range(0, number_of_total_states))  # 生成1到64的数字列表
            # 用户输入数组的长度
            n = int(input("请输入数组的长度："))
            # 生成并打印连续的数组
            arrays = self.generate_continuous_arrays(n)
            for i in range(len(arrays)):  # 遍历所有可能的常量位
                print("%d / %d" % (i + 1, len(arrays)))  # 输出当前进度
                constant_bits = arrays[i]  # 将当前的常量位i作为列表传入
                with open(self.model_file_name, 'w') as f:  # 清空模型文件内容，以便写入新模型
                    pass
                self.constant_bits = constant_bits  # 设置常量位
                self.make_model()  # 生成模型
                self.solve_model()  # 求解模型

    def set_brute_force_flag(self, brute_force_flag):
        """
        设置是否进行暴力破解的标志。暴力破解模式通过设置 flag 为 '1' 来启用。

        参数:
            brute_force_flag (str): '0' 表示不进行暴力破解，'1' 表示进行暴力破解
        """
        self.brute_force_flag = brute_force_flag

    def create_objective_function(self):
        """
        创建并写入 MILP 模型的目标函数。目标是所有变量的最小化总和。
        """
        fileobj = open(self.model_file_name, "a")  # 以追加模式打开模型文件
        fileobj.write("Minimize\n")  # 写入目标函数的关键词

        eqn = []  # 用来存储目标函数的变量项

        # 为目标函数添加 x 变量
        for i in range(0, 8):  # 遍历 8 个位置
            for j in range(0, 4):  # 遍历 4 个子位置
                eqn.append("x" + "_" + str(self.round) + "_" + str(i) + "_" + str(j))  # 添加 x 变量

        # 为目标函数添加 y 变量
        for i in range(0, 8):  # 遍历 8 个位置
            for j in range(0, 4):  # 遍历 4 个子位置
                eqn.append("y" + "_" + str(self.round) + "_" + str(i) + "_" + str(j))  # 添加 y 变量

        # 将变量项连接成一个字符串
        temp = " + ".join(eqn)  # 用 " + " 连接每个变量项

        # 写入目标函数
        fileobj.write(temp)  # 写入目标函数表达式
        fileobj.write("\n")  # 写入换行符

        fileobj.close()  # 关闭文件

    @staticmethod
    def create_variables(n, s):
        """
        生成模型中使用的变量。

        参数:
            n (int): 轮数
            s (str): 变量的前缀（例如 'u' 或 'v'）
        返回:
            list: 生成的变量名列表，格式为 [s_n_0_0, s_n_0_1, ..., s_n_7_3]
        """
        # 初始化一个 8x4 的二维数组，用于存储生成的变量名
        array = [["" for i in range(0, 4)] for j in range(0, 8)]

        # 双重循环遍历每个位置，生成变量名并赋值给数组
        for i in range(0, 8):  # 遍历8个位置
            for j in range(0, 4):  # 遍历4个子位置
                # 生成每个位置的变量名，格式为：s_n_i_j
                array[i][j] = s + "_" + str(n) + "_" + str(i) + "_" + str(j)

        # 返回生成的二维变量数组
        return array

    def constraints_by_sbox(self, variable1, variable2):
        """
        生成并写入 Sbox 的约束。

        参数:
            variable1 (list): 输入变量
            variable2 (list): 输出变量
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")

        # 遍历 Sbox 层的 8 个元素（Sbox的每一行）
        for k in range(0, 8):
            # 遍历 MIBS 算法中定义的 9 个线性不等式
            for coff in Mibs.sb:
                temp = []  # 用于存储约束表达式的一部分

                # 为变量1生成约束
                for u in range(0, 4):  # 遍历 4 个子位置
                    # 将每个系数和对应的变量连接起来
                    temp.append(str(coff[u]) + " " + variable1[k][u])

                # 为变量2生成约束
                for v in range(0, 4):  # 遍历 4 个子位置
                    # 将每个系数和对应的变量连接起来
                    temp.append(str(coff[4 + v]) + " " + variable2[k][v])

                # 将所有项连接成一个字符串
                temp1 = " + ".join(temp)

                # 将 "+ -" 替换成 "- "，以确保表达式的正确格式
                temp1 = temp1.replace("+ -", "- ")

                # 获取不等式的常数部分，并替换 "--" 为 "+"
                s = str(-coff[Mibs.NUMBER - 1])
                s = s.replace("--", "")

                # 生成最终的不等式，并将其写入文件
                temp1 += " >= " + s
                fileobj.write(temp1)  # 将约束写入文件
                fileobj.write("\n")  # 换行

        # 关闭文件
        fileobj.close()

    def constraints_by_copy(self, variablex, variableu, variabley):
        """
        生成并写入复制操作的约束，使用 64bit。

        参数:
            variablex (list): 输入变量
            variableu (list): 中间变量
            variabley (list): 输出变量
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")

        # 遍历 64 位拷贝操作中的每一行和每一列
        for i in range(0, 8):  # 遍历 8 行
            for j in range(0, 4):  # 遍历 4 列
                temp = []  # 用于存储变量的临时列表
                # 将三个变量（x, u, y）按顺序加入 temp 列表
                temp.append(variablex[i][j])
                temp.append(variableu[i][j])
                temp.append(variabley[i][j])

                # 将 temp 列表中的元素以 " - " 连接起来，并且以 " = 0" 作为等式的右侧部分
                s = " - ".join(temp)
                s += " = 0"

                # 将生成的约束写入文件，并换行
                fileobj.write(s)
                fileobj.write("\n")

        # 关闭文件
        fileobj.close()

    def constraints_by_copy_in_F(self, variablex, variableu, variabley):
        """
        生成并写入轮函数中的拷贝操作的约束，只用 4bit。

        参数:
            variablex (list): 输入变量
            variableu (list): 中间变量
            variabley (list): 输出变量
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")

        # 遍历 4 位拷贝操作中的每一列
        for j in range(0, 4):  # 遍历 4 列
            temp = []  # 用于存储变量的临时列表
            # 将三个变量（x, u, y）按顺序加入 temp 列表
            temp.append(variablex[j])
            temp.append(variableu[j])
            temp.append(variabley[j])

            # 将 temp 列表中的元素以 " - " 连接起来，并且以 " = 0" 作为等式的右侧部分
            s = " - ".join(temp)
            s += " = 0"

            # 将生成的约束写入文件，并换行
            fileobj.write(s)
            fileobj.write("\n")

        # 关闭文件
        fileobj.close()

    def constraints_by_xor(self, variabley, variablev, variablex):
        """
        生成并写入异或操作的约束，使用 64bit。

        参数:
            variabley (list): 输出变量
            variablev (list): 输入变量
            variablex (list): 输入变量
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")

        # 遍历 64 位异或操作中的每一行和每一列
        for i in range(0, 8):  # 遍历 8 行
            for j in range(0, 4):  # 遍历 4 列
                temp = []  # 用于存储变量的临时列表
                # 将三个变量（x, v, y）按顺序加入 temp 列表
                temp.append(variablex[i][j])
                temp.append(variablev[i][j])
                temp.append(variabley[i][j])

                # 将 temp 列表中的元素以 " - " 连接起来，并且以 " = 0" 作为等式的右侧部分
                s = " - ".join(temp)
                s += " = 0"

                # 将生成的约束写入文件，并换行
                fileobj.write(s)
                fileobj.write("\n")

        # 关闭文件
        fileobj.close()

    def constraints_by_xor_in_F(self, variabley, variablev, variablex):
        """
        生成并写入轮函数中的异或操作的约束条件，只用 4bit。

        参数:
            variabley (list): 输出变量
            variablev (list): 输入变量
            variablex (list): 输入变量
        """
        # 打开文件以追加模式写入
        fileobj = open(self.model_file_name, "a")

        # 循环4次，处理每个4位的数据
        for j in range(0, 4):
            temp = []
            # 将三个变量添加到temp列表
            temp.append(variablex[j])
            temp.append(variablev[j])
            temp.append(variabley[j])

            # 生成约束公式，使用“ - ”连接
            s = " - ".join(temp)
            s += " = 0"  # 完整约束条件是等于0

            # 将约束写入文件
            fileobj.write(s)
            fileobj.write("\n")

        # 关闭文件
        fileobj.close()

    def nibbles_shuffle(self, inputs):
        """
        对经过 S 盒运算后的数据进行排序，根据预设的置换表进行重新排列。

        参数:
            inputs (list): 输入的Nibble列表
        返回:
            list: 按照置换表顺序排列的Nibble列表
        """
        # 返回按shuffle顺序排列的nibbles
        return [inputs[i] for i in self.shuffle]

    def constraints_by_mixing_layer(self, variables_in, variables_out, round_number):
        """
        生成与混合层相关的约束条件。

        参数:
            variables_in (list): 输入变量
            variables_out (list): 输出变量
            round_number (int): 轮数
        """
        # 创建a、b、c三组变量，每组包含16个4位的变量
        a_vars = self.create_variables(round_number, "a")
        b_vars = self.create_variables(round_number, "b")
        c_vars = self.create_variables(round_number, "c")

        # 初始化t_vars矩阵，为16行4列的零矩阵
        t_vars = [[0 for i in range(4)] for j in range(16)]

        # 为t_vars中的每个元素生成唯一标识
        for i in range(16):
            for j in range(4):
                t_vars[i][j] = "t" + "_" + str(round_number) + "_" + str(i) + "_" + str(j)

        # 通过4位复制约束生成约束条件
        self.constraints_by_copy_in_F(variables_in[3], t_vars[0], a_vars[3])
        self.constraints_by_copy_in_F(variables_in[2], t_vars[1], a_vars[2])
        self.constraints_by_copy_in_F(variables_in[1], t_vars[2], a_vars[1])
        self.constraints_by_copy_in_F(variables_in[0], t_vars[3], a_vars[0])

        self.constraints_by_copy_in_F(a_vars[7], b_vars[7], t_vars[4])
        self.constraints_by_copy_in_F(a_vars[6], b_vars[6], t_vars[5])
        self.constraints_by_copy_in_F(a_vars[5], b_vars[5], t_vars[6])
        self.constraints_by_copy_in_F(a_vars[4], b_vars[4], t_vars[7])

        self.constraints_by_copy_in_F(b_vars[3], c_vars[3], t_vars[8])
        self.constraints_by_copy_in_F(b_vars[2], c_vars[2], t_vars[9])
        self.constraints_by_copy_in_F(b_vars[1], c_vars[1], t_vars[10])
        self.constraints_by_copy_in_F(b_vars[0], c_vars[0], t_vars[11])

        self.constraints_by_copy_in_F(c_vars[7], variables_out[7], t_vars[12])
        self.constraints_by_copy_in_F(c_vars[6], variables_out[6], t_vars[13])
        self.constraints_by_copy_in_F(c_vars[5], variables_out[5], t_vars[14])
        self.constraints_by_copy_in_F(c_vars[4], variables_out[4], t_vars[15])

        # 通过4位异或约束生成约束条件
        self.constraints_by_xor_in_F(variables_in[7], t_vars[0], a_vars[7])
        self.constraints_by_xor_in_F(variables_in[6], t_vars[1], a_vars[6])
        self.constraints_by_xor_in_F(variables_in[5], t_vars[2], a_vars[5])
        self.constraints_by_xor_in_F(variables_in[4], t_vars[3], a_vars[4])

        self.constraints_by_xor_in_F(a_vars[1], t_vars[4], b_vars[1])
        self.constraints_by_xor_in_F(a_vars[0], t_vars[5], b_vars[0])
        self.constraints_by_xor_in_F(a_vars[3], t_vars[6], b_vars[3])
        self.constraints_by_xor_in_F(a_vars[2], t_vars[7], b_vars[2])

        self.constraints_by_xor_in_F(b_vars[4], t_vars[8], c_vars[4])
        self.constraints_by_xor_in_F(b_vars[7], t_vars[9], c_vars[7])
        self.constraints_by_xor_in_F(b_vars[6], t_vars[10], c_vars[6])
        self.constraints_by_xor_in_F(b_vars[5], t_vars[11], c_vars[5])

        self.constraints_by_xor_in_F(c_vars[3], t_vars[12], variables_out[3])
        self.constraints_by_xor_in_F(c_vars[2], t_vars[13], variables_out[2])
        self.constraints_by_xor_in_F(c_vars[1], t_vars[14], variables_out[1])
        self.constraints_by_xor_in_F(c_vars[0], t_vars[15], variables_out[0])

    def constraint(self):
        """
            按照加密算法部件结构，生成约束
        """
        # 确保至少有1轮
        assert (self.round >= 1)

        # 打开文件以追加模式写入约束条件
        fileobj = open(self.model_file_name, "a")

        # 写入约束部分的标题
        fileobj.write("Subject To\n")
        # 关闭文件
        fileobj.close()

        # 为每一轮生成所需的变量
        variableinx = Mibs.create_variables(0, "x")  # 输入x变量
        variableiny = Mibs.create_variables(0, "y")  # 输入y变量
        variableu = Mibs.create_variables(0, "u")  # 中间u变量
        variablev = Mibs.create_variables(0, "v")  # 中间v变量
        variabled = Mibs.create_variables(0, "d")  # 中间d变量
        variableoutx = Mibs.create_variables(1, "x")  # 输出x变量
        variableouty = Mibs.create_variables(1, "y")  # 输出y变量

        # 处理1轮的情况
        if self.round == 1:
            # 通过64位复制生成约束
            self.constraints_by_copy(variableinx, variableu, variableouty)
            # 通过S盒生成约束
            self.constraints_by_sbox(variableu, variablev)
            # 生成混合层约束
            self.constraints_by_mixing_layer(variablev, variabled, 0)
            # 对d变量进行nibbles洗牌操作
            variabled = self.nibbles_shuffle(variabled)
            # 通过64位异或生成约束
            self.constraints_by_xor(variableiny, variabled, variableoutx)

        # 处理多轮的情况
        else:
            # 1轮的操作，和上一轮相同
            self.constraints_by_copy(variableinx, variableu, variableouty)
            self.constraints_by_sbox(variableu, variablev)
            self.constraints_by_mixing_layer(variablev, variabled, 0)
            variabled = self.nibbles_shuffle(variabled)
            self.constraints_by_xor(variableiny, variabled, variableoutx)

            # 从第2轮到第self.round轮，逐步生成约束
            for i in range(1, self.round):
                # 更新每一轮的变量
                variableinx = variableoutx  # 输入x变量来自上一轮的输出x
                variableiny = variableouty  # 输入y变量来自上一轮的输出y
                variableouty = Mibs.create_variables((i + 1), "y")  # 当前轮的输出y变量
                variableoutx = Mibs.create_variables((i + 1), "x")  # 当前轮的输出x变量
                variableu = Mibs.create_variables(i, "u")  # 当前轮的u变量
                variablev = Mibs.create_variables(i, "v")  # 当前轮的v变量
                variabled = Mibs.create_variables(i, "d")  # 当前轮的d变量

                # 生成每一轮的约束条件
                self.constraints_by_copy(variableinx, variableu, variableouty)  # 64位复制约束
                self.constraints_by_sbox(variableu, variablev)  # S盒操作约束
                self.constraints_by_mixing_layer(variablev, variabled, i)  # 混合层约束
                variabled = self.nibbles_shuffle(variabled)  # nibbles洗牌约束
                self.constraints_by_xor(variableiny, variabled, variableoutx)  # 64位异或约束

    # Variables declaration
    def variable_binary(self):
        """
        在模型中写入变量
        """
        # 打开模型文件，追加模式
        fileobj = open(self.model_file_name, "a")
        # 写入"Binary"来标识变量类型
        fileobj.write("Binary\n")

        # 循环遍历 round + 1 次 (round 表示回合数)，为每个回合创建 x 和 y 变量
        for i in range(self.round + 1):
            for j in range(8):  # 循环遍历 8
                for k in range(4):  # 循环遍历 4
                    # 写入 x 和 y 变量
                    fileobj.write("x_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("y_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")

        # 为 round 次 (回合数) 创建 u, v, a, b, c, d 变量
        for i in range(self.round):
            for j in range(8):
                for k in range(4):
                    fileobj.write("u_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("v_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("a_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("b_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("c_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("d_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")

        # 为 round 次 (回合数) 创建 t 变量
        for i in range(self.round):
            for j in range(16):
                for k in range(4):
                    fileobj.write("t_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")

        # 写入结束标记
        fileobj.write("END")
        # 关闭文件对象
        fileobj.close()

    def init(self):
        """
        生成并写入初始可分性的约束
        """
        # 调用 Mibs.create_variables 函数创建变量 y 和 x
        variabley = Mibs.create_variables(0, "y")
        variablex = Mibs.create_variables(0, "x")
        # 打开模型文件，追加模式
        fileobj = open(self.model_file_name, "a")

        eqn = []  # 初始化方程列表

        for i in range(64):  # 遍历 64 个输入状态
            if i in self.constant_bits:  # 如果是活跃比特，设置为 1
                if i <= 31:
                    temp = variabley[7 - (i // 4)][3 - i % 4] + " = 0"  # 对应的变量 y 设为 1
                    fileobj.write(temp)
                    fileobj.write("\n")
                else:
                    temp = variablex[7 - (i // 4)][3 - i % 4] + " = 0"  # 对应的变量 x 设为 0
                    fileobj.write(temp)
                    fileobj.write("\n")
            else:
                if i <= 31:
                    temp = variabley[7 - (i // 4)][3 - i % 4] + " = 1"  # 对应的变量 y 设为 1
                    fileobj.write(temp)
                    fileobj.write("\n")
                else:
                    temp = variablex[7 - (i // 4)][3 - i % 4] + " = 1"  # 对应的变量 x 设为 0
                    fileobj.write(temp)
                    fileobj.write("\n")

        # 关闭文件对象
        fileobj.close()

    def make_model(self):
        """
        生成MILP模型
        """
        # 调用 create_objective_function 方法生成目标函数
        self.create_objective_function()

        # 调用 constraint 方法生成约束条件
        self.constraint()

        # 调用 init 方法生成初始可分性
        self.init()

        # 调用 variable_binary 方法生成二进制变量
        self.variable_binary()

    def solve_model(self):
        """
        求解MILP模型
        """
        time_start = time.time()  # 记录开始时间，用于计算算法运行时间

        balance_count = 64  # 初始化平衡比特计数为64
        # 初始化平衡位列表，初始时每个比特位为未知状态 "?"
        balanced_bits = ["b" for i in range(64)]
        balanced_flag = False  # 用于标记是否找到积分区分器

        m = read(self.model_file_name)  # 读取MILP模型文件

        # 如果启用暴力破解（brute_force_flag 为 '1'），则关闭输出
        if (self.brute_force_flag == '1'):
            m.setParam("OutputFlag", 0)  # 设置Gurobi参数，关闭输出

        counter = 0  # 初始化计数器
        set_zero = []  # 初始化空列表，用于存储设为零的变量

        # 循环，直到达到给定的 blocksize
        while counter < self.blocksize:
            m.optimize()  # 求解MILP模型

            # Gurobi语法: m.Status == 2表示模型是可行的
            if m.Status == 2:
                obj = m.getObjective()  # 获取目标函数
                if obj.getValue() > 1:  # 如果目标函数值大于1，说明已找到积分区分器
                    balanced_flag = True
                    break
                else:
                    # 否则，遍历每个变量，找到未平衡的比特位
                    for i in range(0, self.blocksize):
                        u = obj.getVar(i)  # 获取第i个变量
                        temp = u.getAttr('x')  # 获取该变量的值
                        if temp == 1:  # 如果该变量值为1
                            set_zero.append(u.getAttr('VarName'))  # 将该变量名加入 set_zero
                            balanced_bits[i] = "?"  # 设置该比特位为 "?"，表示未平衡
                            balance_count -= 1  # 减少平衡比特计数
                            m.addConstr(u == 0)  # 为该变量添加约束，强制其值为0
                            m.update()  # 更新模型
                            counter += 1  # 计数器加1
                            break
            # Gurobi语法: m.Status == 3表示模型是不可行的
            elif m.Status == 3:
                balanced_flag = True
                break
            else:
                print("Unknown error!")  # 如果模型返回未知错误，打印错误信息

        # 打开结果文件进行写入
        fileobj = open(self.result_file_name, "a")
        fileobj.write(f"轮数为: {self.round}\n")  # 写入当前轮数

        # 根据是否找到积分区分器，写入相应的信息
        new_constant_bits = [x + 1 for x in self.constant_bits]  # 将常量比特位索引加1，符合阅读习惯
        if balanced_flag:  # 如果找到了积分区分器
            fileobj.write("常量比特位: %s \n" % ",".join(map(str, new_constant_bits)))
            fileobj.write("存在积分区分器\n")
            print("\n常量比特位: %s" % ",".join(map(str, new_constant_bits)))
            print("存在积分区分器")
        else:  # 如果未找到积分区分器
            fileobj.write("常量比特位为: %s\n" % ",".join(map(str, new_constant_bits)))
            fileobj.write("不存在积分区分器\n")
            print("\n常量比特位为: %s" % ",".join(map(str, new_constant_bits)))
            print("不存在积分区分器")

        # 创建一个长度为64的列表，用于表示输入值
        input_array = ['a'] * 64
        # 更新 input_array，根据 constant_bits 中的索引将元素修改为 'c'
        for index in self.constant_bits:
            input_array[63 - index] = 'c'

        # 将 input_array 划分为 16 组，每组4个比特，形成一个新的输入表示
        input_array = ["".join(input_array[4 * i: 4 * i + 4]) for i in range(16)]
        fileobj.write("输入为: %s\n" % " ".join(input_array))  # 写入输入信息

        # 打印整个 input_array
        print("输入为:" + " ".join(input_array))

        # 将平衡比特位的状态按4个比特一组进行输出
        output_state = ["".join(balanced_bits[4 * i: 4 * i + 4]) for i in range(16)]
        fileobj.write("输出为: %s" % " ".join(output_state))  # 写入输出信息
        print("输出为:" + " ".join(output_state))

        # 打印平衡比特数量
        print(f"平衡比特数量：{balance_count}")

        # 记录结束时间并计算算法运行时间
        time_end = time.time()  # 记录结束时间
        elapsed_time = time_end - time_start  # 计算算法运行时间
        fileobj.write("\n用时为 = %.2f\n\n" % elapsed_time)  # 写入运行时间
        print("用时为 = %.2f\n" % elapsed_time)  # 打印运行时间

        # 关闭结果文件
        fileobj.close()
