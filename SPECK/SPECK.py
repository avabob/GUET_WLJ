# H. Hadipour
# 1397/04/18
"""
变量定义与表示:  x_轮号_字节号_比特号

x_0_0_0 表示第 0 轮，第 0 个字节的第 0 个比特。
x_0_0_3 表示第 0 轮，第 0 个字节的第 3 个比特。

输入分组：
x_i_0_0, x_i_0_1, x_i_0_2, x_i_0_3, ..., x_i_7_0, x_i_7_1, x_i_7_2, x_i_7_3 表示第 i+1 轮输入的左半部分。
y_i_0_0, y_i_0_1, y_i_0_2, y_i_0_3, ..., y_i_7_0, y_i_7_1, y_i_7_2, y_i_7_3 表示第 i+1 轮输入的右半部分。

"""


from gurobipy import *  # 导入 Gurobi 库
import time  # 导入时间库
import os

class Speck:
    def __init__(self, round ,blocksize):
        """
        初始化 Mibs 类的实例，设置轮数、活跃比特数、块大小及置换表等基本信息。
        """
        self.round = round  # 设置 MIBS 轮数
        self.blocksize = blocksize
        if self.blocksize == 32:
            self.R1 = 7
            self.R2 = 2
        elif self.blocksize == 48:
            self.R1 = 8
            self.R2 = 3
        elif self.blocksize == 64:
            self.R1 = 8
            self.R2 = 3

        self.word_length = self.blocksize // 2

        self.brute_force_flag = '0'

        # 设置 MILP 模型的文件名，模型文件存放路径为 "model" 文件夹
        self.model_file_name = "./model/SPECK_%d.lp" % self.round
        # 设置结果文件的文件名，存放路径为 "result" 文件夹
        self.result_file_name = "./result/SPECK_round%d_result.txt" % self.round

        # 确保 "model" 文件夹存在，不存在则创建
        os.makedirs("./model", exist_ok=True)
        # 确保 "result" 文件夹存在，不存在则创建
        os.makedirs("./result", exist_ok=True)

        # 创建并立即关闭模型文件，确保文件存在
        with open(self.model_file_name, "w") as fileobj:
            pass

        # 创建并立即关闭结果文件，确保文件存在
        with open(self.result_file_name, "w") as fileobj:
            pass


    def generate_continuous_arrays(self, n):
        total_elements = self.blocksize
        # 确保 n <= total_elements
        if n > total_elements:
            raise ValueError(f"数组长度不能大于分组长度（{total_elements}）")
        # 生成从 0 到 total_elements - 1 的连续数组
        arrays = [list(range(i, i + n)) for i in range(0, total_elements - n + 1)]
        arrays.reverse()
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
            if (len(constant_bits) > self.blocksize):
                raise ValueError(f"数组长度不能大于分组长度（{self.blocksize}）")  # 检查输入是否有效
            for index in constant_bits:
                if index > self.blocksize:
                    raise ValueError(f"常数比特位置不能大于分组长度（{self.blocksize}）")  # 检查输入是否有效
            self.constant_bits = constant_bits
            self.make_model()  # 调用make_model方法生成模型
            self.solve_model()  # 调用solve_model方法求解模型

        else:  # 如果选择了暴力破解（1）
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
        """
        self.brute_force_flag = brute_force_flag

    def create_objective_function(self):
        """
        创建并写入 MILP 模型的目标函数。
        """
        fileobj = open(self.model_file_name, "a")  # 以追加模式打开模型文件
        fileobj.write("Minimize\n")  # 写入目标函数的关键词

        eqn = []  # 用来存储目标函数的变量项

        for i in range(0, self.word_length):
            eqn.append("x" + "_" + str(self.round) + "_" + str(i))
        for j in range(0, self.word_length):
            eqn.append("y" + "_" + str(self.round) + "_" + str(j))

        # 将变量项连接成一个字符串
        temp = " + ".join(eqn)  # 用 " + " 连接每个变量项

        # 写入目标函数
        fileobj.write(temp)  # 写入目标函数表达式
        fileobj.write("\n")  # 写入换行符

        fileobj.close()  # 关闭文件

    def create_variables(self, n, s):
        """
        生成模型中使用的变量。
        """
        variable = []
        for i in range(0, self.word_length):
            variable.append(s + "_" + str(n) + "_" + str(i))
        return variable


    def constraints_by_copy(self, in1, out1, out2):
        """
        生成并写入复制操作的约束
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")
        for i in range(0, self.word_length):
            fileobj.write((in1[i] + " - " + out1[i] + " - " + out2[i] + " = " + str(0)))
            fileobj.write("\n")
        fileobj.close()


    def constraints_by_xor(self, in1, in2, out):
        """
        生成并写入异或操作的约束，使用64bit
        """
        # 以追加模式打开模型文件
        fileobj = open(self.model_file_name, "a")

        for i in range(0, self.word_length):
            fileobj.write((out[i] + " - " + in1[i] + " - " + in2[i] + " = " + str(0)))
            fileobj.write("\n")
        fileobj.close()

    def constraints_by_and(self, in1, in2, out):
        """
        Generate constraints by and operation.
        """
        fileobj = open(self.model_file_name, "a")
        for i in range(0, self.word_length):
            fileobj.write((out[i] + " - " + in1[i] + " >= " + str(0)))
            fileobj.write("\n")
            fileobj.write((out[i] + " - " + in2[i] + " >= " + str(0)))
            fileobj.write("\n")
            fileobj.write((out[i] + " - " + in1[i] + " - " + in2[i] + " <= " + str(0)))
            fileobj.write("\n")
        fileobj.close()

    def rotation_L(self, x, n):
        """
        Bit Rotation.
        """
        eqn = []
        for i in range(0, self.word_length):
            eqn.append(x[(i + n) % self.word_length])
        return eqn

    def rotation_R(self, x, n):
        """
        Bit Rotation.
        """
        eqn = []
        for i in range(0, self.word_length):
            eqn.append(x[(i - n) % self.word_length])
        return eqn


    def constraint(self):
        """
        生成用于MILP模型的约束条件
        """
        assert (self.round >= 1)
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        x_in = self.create_variables(0, "x")
        y_in = self.create_variables(0, "y")
        for i in range(0, self.round):
            u = self.create_variables(i, "u")
            v = self.create_variables(i, "v")
            w = self.create_variables(i, "w")
            t = self.create_variables(i, "t")
            x_out = self.create_variables((i + 1), "x")
            y_out = self.create_variables((i + 1), "y")
            x_in = self.rotation_R(x_in, self.R1)
            self.constraints_by_copy(y_in, u, v)
            v = self.rotation_L(v, self.R2)
            self.constraints_by_and(u, x_in, w)
            self.constraints_by_copy(w, t, x_out)
            self.constraints_by_xor(t, v, y_out)
            x_in = x_out
            y_in = y_out

    # Variables declaration
    def variable_binary(self):
        """
        在模型中写入变量
        """
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Binary\n")
        for i in range(0, self.round):
            for j in range(0, self.word_length):
                fileobj.write(("x_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.word_length):
                fileobj.write(("y_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.word_length):
                fileobj.write(("u_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.word_length):
                fileobj.write(("v_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.word_length):
                fileobj.write(("w_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.word_length):
                fileobj.write(("t_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
        for j in range(0, self.word_length):
            fileobj.write(("x_" + str(self.round) + "_" + str(j)))
            fileobj.write("\n")
        for j in range(0, self.word_length):
            fileobj.write(("y_" + str(self.round) + "_" + str(j)))
            fileobj.write("\n")
        fileobj.write("END")
        fileobj.close()

    def init(self):
        """
        生成并写入初始可分性的约束
        """
        # 调用 Mibs.create_variables 函数创建变量 y 和 x
        variabley = self.create_variables(0, "y")
        variablex = self.create_variables(0, "x")
        # 打开模型文件，追加模式
        fileobj = open(self.model_file_name, "a")
        eqn = []  # 初始化方程列表
        for i in range(self.blocksize):  # 遍历 64 个输入状态
            if i in self.constant_bits:  # 如果是活跃比特，设置为 1
                if i <= self.word_length - 1:
                    temp = variabley[self.word_length - i - 1] + " = 0"  # 对应的变量 y 设为 1
                    fileobj.write(temp)
                    fileobj.write("\n")
                else:
                    temp = variablex[self.word_length - i - 1] + " = 0"  # 对应的变量 x 设为 0
                    fileobj.write(temp)
                    fileobj.write("\n")
            else:
                if i <= self.word_length - 1:
                    temp = variabley[self.word_length - i - 1] + " = 1"  # 对应的变量 y 设为 1
                    fileobj.write(temp)
                    fileobj.write("\n")
                else:
                    temp = variablex[self.word_length - i - 1] + " = 1"  # 对应的变量 x 设为 0
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
        time_start = time.time()

        balance_count = self.blocksize  # 平衡比特计数
        # 初始化平衡位列表，初始时每个比特位为未知状态 "?"
        balanced_bits = ["b" for i in range(self.blocksize)]
        balanced_flag = False  # 用于标记是否找到积分区分器

        m = read(self.model_file_name)

        # 如果启用暴力破解（brute_force_flag 为 '1'），则关闭输出
        if (self.brute_force_flag == '1'):
            m.setParam("OutputFlag", 0)

        counter = 0
        set_zero = []
        while counter < self.blocksize:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                obj = m.getObjective()
                if obj.getValue() > 1:
                    balanced_flag = True
                    break
                else:
                    for i in range(0, self.blocksize):
                        u = obj.getVar(i)
                        temp = u.getAttr('x')
                        if temp == 1:
                            set_zero.append(u.getAttr('VarName'))
                            balanced_bits[i] = "?"  # 设置为 "?" set_zero代表未平衡bit "?"
                            balance_count -= 1
                            m.addConstr(u == 0)
                            m.update()
                            counter += 1
                            break
            # Gurobi syntax: m.Status == 3 represents the model is infeasible.
            elif m.Status == 3:
                balanced_flag = True
                break
            else:
                print("Unknown error!")

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

        input_array = ['a'] * self.blocksize
        # 更新 input_array，根据 constant_bits 中的索引将元素修改为 'c'

        for index in self.constant_bits:
            input_array[self.blocksize - index - 1] = 'c'
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
        fileobj.write(f"\n平衡比特数量：{balance_count}")
        print(f"平衡比特数量：{balance_count}")
        # 记录结束时间并计算算法运行时间
        time_end = time.time()
        elapsed_time = time_end - time_start
        fileobj.write("\n用时为 = %.2f\n\n" % elapsed_time)
        print("用时为 = %.2f\n" % elapsed_time)

        # 关闭结果文件
        fileobj.close()