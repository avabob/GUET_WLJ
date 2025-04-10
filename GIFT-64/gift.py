"""
"x_i_63, x_i_62, ..., x_i_0" 表示第 (i+1) 轮的输入。
"""

from gurobipy import *
import os
import time


class Gift:
    def __init__(self, round):
        self.round = round
        self.blocksize = 64
        self.brute_force_flag = '0'

        # 设置 MILP 模型的文件名，模型文件存放路径为 "model" 文件夹
        self.model_file_name = "./model/CRAFT%d.lp" % self.round
        # 设置结果文件的文件名，存放路径为 "result" 文件夹
        self.result_file_name = "./result/result_round_%d.txt" % self.round

        # 确保 "model" 文件夹存在，不存在则创建
        os.makedirs("./model", exist_ok=True)  # 确保该文件夹存在
        # 确保 "result" 文件夹存在，不存在则创建
        os.makedirs("./result", exist_ok=True)  # 来确保该文件夹存在

        # 创建并立即关闭模型文件，确保文件存在
        with open(self.model_file_name, "w") as fileobj:
            pass

        # 创建并立即关闭结果文件，确保文件存在
        with open(self.result_file_name, "w") as fileobj:
            pass

    # Linear inequalities for the Gift Sbox
    S_T = [[1, 1, 1, 1, -1, -1, -1, -1, 0],
           [-3, -3, -5, -4, 2, 3, 1, 1, 8],
           [-3, -2, 3, -1, -1, -2, -4, 3, 7],
           [-1, -1, -1, 0, 2, 3, 1, 1, 0],
           [0, 0, 0, 3, -1, -2, -1, -1, 2],
           [0, -1, 0, -2, -1, 1, 2, -2, 4],
           [1, 0, 0, -1, 1, -1, -2, -1, 3],
           [-3, -1, -5, -6, 2, 1, 5, 3, 8],
           [0, 1, 3, 1, -2, -2, -1, -2, 2],
           [0, 1, 0, 3, -2, -2, -1, -1, 2],
           [-1, -1, 0, -1, 3, 2, 2, 1, 0],
           [0, -1, 0, -1, 0, -1, 1, 1, 2],
           [2, 1, 0, 1, -1, -2, -1, -2, 2],
           [0, -2, -2, -1, 1, 2, 1, 1, 2],
           [-1, 0, 0, -2, -1, 1, -2, 2, 4]]
    NUMBER = 9

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
            raise ValueError(f"数组长度不能大于总元素个数（{total_elements}）")

        # 生成从 0 到 total_elements - 1 的连续数组
        arrays = [list(range(i, i + n)) for i in range(0, total_elements - n + 1)]
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
            self.constant_bits = constant_bits
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
                self.constant_bits = constant_bits
                self.make_model()  # 调用make_model方法生成模型
                self.solve_model()  # 调用solve_model方法求解模型

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
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Minimize\n")
        eqn = []
        for i in range(0, 64):
            eqn.append("x" + "_" + str(self.round) + "_" + str(i))
        temp = " + ".join(eqn)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    @staticmethod
    def create_variables(n):
        """
        生成模型中使用的变量。

        参数:
            n (int): 轮数
            s (str): 变量名（例如 'u' 或 'v'）
        返回:
            list: 生成的变量名列表，格式为 [s_n_0_0, s_n_0_1, ..., s_n_7_3]
        """
        array = []
        for i in range(0, 64):
            array.append(("x" + "_" + str(n) + "_" + str(i)))
        return array

    def constraintsBySbox(self, variable1, variable2):
        """
        生成并写入 Sbox 的约束。

        参数:
            variable1 (list): 输入变量
            variable2 (list): 输出变量
        """
        fileobj = open(self.model_file_name, "a")
        for k in range(0, 16):  # k的值取决于中间状态的长度以及s盒的结构。若s盒为4*4 = 16，中间状态为64位则需要
            for coff in Gift.S_T:  # coff是s盒的多项式系数和常数项，前八位为系数，最后一位为常数项
                temp = []
                for u in range(0, 4):
                    temp.append(
                        str(coff[u]) + " " + variable1[(k * 4) + 3 - u])  # u的值为0，1，2，3 ; (k * 4) + 3 - u的值为3，2，1，0
                for v in range(0, 4):
                    temp.append(str(coff[v + 4]) + " " + variable2[
                        (k * 4) + 3 - v])  # v + 4的值为4，5，6，7 ; (k * 4) + 3 - v的值为3，2，1，0
                temp1 = " + ".join(temp)
                temp1 = temp1.replace("+ -", "- ")
                s = str(-coff[Gift.NUMBER - 1])  # 最后一位，即s盒的多项式常数项
                s = s.replace("--", "")
                temp1 += " >= " + s
                fileobj.write(temp1)
                fileobj.write("\n")
        fileobj.close();

    @staticmethod
    def p_layer(variable):  # 对应文章https://zhuanlan.zhihu.com/p/461549805中的p-Layer
        """
            P盒操作
        """
        p_box = [
            0, 17, 34, 51, 48, 1, 18, 35, 32, 49, 2, 19, 16, 33, 50, 3,
            4, 21, 38, 55, 52, 5, 22, 39, 36, 53, 6, 23, 20, 37, 54, 7,
            8, 25, 42, 59, 56, 9, 26, 43, 40, 57, 10, 27, 24, 41, 58, 11,
            12, 29, 46, 63, 60, 13, 30, 47, 44, 61, 14, 31, 28, 45, 62, 15
        ]
        array = ["" for i in range(0, 64)]
        for i in range(0, 64):
            array[p_box[i]] = variable[i]

        # for i in range(0, 64):
        # 	array[int((4 * (i // 16)) + (16 * (((3 * ((i % 16) // 4) + (i % 4)) % 4))) + i % 4)] = variable[i]
        # print(array)
        return array

    def constraint(self):
        """
            按照加密算法部件结构，生成约束
        """
        assert (self.round >= 1)
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        variablein = Gift.create_variables(0)
        variableout = Gift.create_variables(1)
        if self.round == 1:
            self.constraintsBySbox(variablein, variableout)
        # omit the last linear layer
        else:
            self.constraintsBySbox(variablein, variableout)
            for i in range(1, self.round):
                variablein = Gift.p_layer(variableout)
                variableout = Gift.create_variables(i + 1)
                self.constraintsBySbox(variablein, variableout)
            # omit the last linear layer

    def variable_binary(self):  # 写入二进制变量
        """
        在模型中写入变量
        """
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Binary\n")
        for i in range(0, (self.round + 1)):
            for j in range(0, 64):
                fileobj.write("x_" + str(i) + "_" + str(j))
                fileobj.write("\n")
        fileobj.write("END")
        fileobj.close()

    def init(self):
        """
        生成由初始分割属性引入的初始约束条件。
        """
        input_state = Gift.create_variables(0)
        fileobj = open(self.model_file_name, "a")  # 打开文件以追加数据
        eqn = []  # 初始化等式列表
        for i in range(64):  # 遍历 64 个输入状态
            if i in self.constant_bits:  # 如果是常量，设置为 0
                fileobj.write("%s = 0\n" % input_state[63 - i])
            else:  # 如果是活跃比特，设置为 1
                fileobj.write("%s = 1\n" % input_state[63 - i])
        fileobj.close()  # 关闭文件

    def make_model(self):
        """
        生成MILP模型
        """
        self.create_objective_function()
        self.constraint()
        self.init()
        self.variable_binary()

    def solve_model(self):
        """
        求解 MILP 模型，搜索 Gift 算法的积分区分器（Integral Distinguisher）。
        """
        # 记录开始时间
        time_start = time.time()
        balance_count = 0  # 平衡比特计数
        # 初始化平衡位列表，初始时每个比特位为未知状态 "?"
        balanced_bits = ["?" for i in range(64)]
        balanced_flag = False  # 用于标记是否找到积分区分器

        # 读取 MILP 模型文件
        m = read(self.model_file_name)

        # 如果启用暴力破解（brute_force_flag 为 '1'），则关闭输出
        if (self.brute_force_flag == '1'):
            m.setParam("OutputFlag", 0)

        # 获取模型的目标函数
        obj = m.getObjective()

        # 遍历每个比特位，进行求解
        for i in range(0, self.blocksize):
            # 初始化一个长度为 64 的零列表，表示比特位约束
            mask = [0 for j in range(64)]
            # 设置当前比特位为 1
            mask[i] = 1

            # 添加临时约束，目标函数的变量值与 mask 中相应位置的值一致
            temporary_constraints = m.addConstrs(
                (obj.getVar(j) == mask[j] for j in range(64)), name='temp_constraints')

            # 对模型进行优化求解
            m.optimize()

            # 如果找到可行解（状态为 3），说明找到了平衡比特位
            if m.Status == 3:
                balanced_flag = True
                # 设置当前比特位为 "b"（表示该比特位平衡）
                balanced_bits[63 - i] = "b"     #xi = x[63-i]  倒序阅读，所以第一个变量 x0 在数组中为最后一个元素 x[63]
                balance_count += 1
            # 移除临时约束
            m.remove(temporary_constraints)
            m.update()

        # 打开结果文件进行写入
        fileobj = open(self.result_file_name, "a")
        fileobj.write(f"轮数为: {self.round}\n")
        # 根据是否找到积分区分器，写入相应的信息
        new_constant_bits = [x + 1 for x in self.constant_bits]  # constant_bits存储的是索引，因为索引是从零开始，不易阅读，因此加1，符合阅读习惯
        if balanced_flag:
            fileobj.write("常量比特位: %s \n" %
                          ",".join(map(str, new_constant_bits)))
            fileobj.write("存在积分区分器\n")
            print("\n常量比特位: %s" %
                  ",".join(map(str, new_constant_bits)))
            print("存在积分区分器")
        else:
            fileobj.write("常量比特位为: %s\n" %
                          ",".join(map(str, new_constant_bits)))
            fileobj.write("不存在积分区分器\n")
            print("\n常量比特位为: %s" %
                  ",".join(map(str, new_constant_bits)))
            print("不存在积分区分器")

        input_array = ['a'] * 64
        # 更新 input_array，根据 constant_bits 中的索引将元素修改为 'c'

        for index in self.constant_bits:
            input_array[63 - index] = 'c'    #xi = x[63-i]  倒序阅读，所以第一个变量 x0 在数组中为最后一个元素 x[63]
        # 输入

        input_array = ["".join(input_array[4 * i: 4 * i + 4])
                       for i in range(16)]
        fileobj.write("输入为: %s\n" % " ".join(input_array))

        # 打印整个 input_array
        print("输入为:" + " ".join(input_array))
        # 将平衡比特位的状态按 4 个比特一组进行输出

        # 输出
        output_state = ["".join(balanced_bits[4 * i: 4 * i + 4])
                        for i in range(16)]
        fileobj.write("输出为: %s" % " ".join(output_state))
        print("输出为:" + " ".join(output_state))
        print(f"平衡比特数量：{balance_count}")
        # 记录结束时间并计算算法运行时间
        time_end = time.time()
        elapsed_time = time_end - time_start
        fileobj.write("\n用时为 = %.2f\n\n" % elapsed_time)
        print("用时为 = %.2f\n" % elapsed_time)

        # 关闭结果文件
        fileobj.close()
