import os
import time
class Solve:
    def __init__(self, rounds):
        self.rounds = rounds  # 设置 rounds（算法回合数）

        self.brute_force_flag = '0'  # 默认为不进行暴力破解
        self.block_size = 64  # 块大小设为 64 位

        # 设置 nibbles 置换表（用于 Sbox 操作），这可能与 CRAFT 算法的具体细节有关


        # 设置 MILP 模型的文件名，模型文件存放路径为 "model" 文件夹
        self.model_file_name = ".\\model\\CRAFT%d.lp" % self.rounds
        # 设置结果文件的文件名，存放路径为 "result" 文件夹
        self.result_file_name = ".\\result\\result_round_%d.txt" % self.rounds

        # 确保 "model" 文件夹存在，不存在则创建
        os.makedirs(os.path.dirname(self.model_file_name), exist_ok=True)
        # 确保 "result" 文件夹存在，不存在则创建
        os.makedirs(os.path.dirname(self.result_file_name), exist_ok=True)

        # 创建并立即关闭模型文件，确保文件存在
        with open(self.model_file_name, "w") as fileobj:
            pass

        # 创建并立即关闭结果文件，确保文件存在
        with open(self.result_file_name, "w") as fileobj:
            pass

def solve_model(self):
    """
    求解 MILP 模型，搜索算法的积分区分器（Integral Distinguisher）。
    """
    # 记录开始时间
    time_start = time.time()

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
    for i in range(0, self.block_size):
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
            balanced_bits[i] = "b"  # 设置当前比特位为 "b"（表示该比特位平衡）

        # 移除临时约束
        m.remove(temporary_constraints)
        m.update()

    # 打开结果文件进行写入
    fileobj = open(self.result_file_name, "a")
    fileobj.write(f"轮数为: {self.rounds}\n")
    # 根据是否找到积分区分器，写入相应的信息
    if balanced_flag:
        fileobj.write("常量比特索引为: %s\n" %
                      ",".join(map(str, self.constant_bits)))
        fileobj.write("存在积分区分器\n")
        print("\n常量比特索引: %s" %
              ",".join(map(str, self.constant_bits)))
        print("存在积分区分器")
    else:
        fileobj.write("常量比特索引为: %s\n" %
                      ",".join(map(str, self.constant_bits)))
        fileobj.write("不存在积分区分器\n")
        print("\n常量比特索引为: %s" %
              ",".join(map(str, self.constant_bits)))
        print("不存在积分区分器")

    input_array = ['a'] * 64

    # 更新 input_array，根据 constant_bits 中的索引将元素修改为 'c'
    for index in self.constant_bits:
        input_array[index] = 'c'
    input_array = ["".join(input_array[4 * i: 4 * i + 4])
                   for i in range(16)]
    fileobj.write("输入为: %s\n" % " ".join(input_array))

    # 打印整个 input_array
    print("输入为:" + " ".join(input_array))
    # 将平衡比特位的状态按 4 个比特一组进行输出
    output_state = ["".join(balanced_bits[4 * i: 4 * i + 4])
                    for i in range(16)]
    fileobj.write("输出为: %s" % " ".join(output_state))
    print("输出为:" + " ".join(output_state))

    # 记录结束时间并计算算法运行时间
    time_end = time.time()
    elapsed_time = time_end - time_start
    fileobj.write("\n用时为 = %.2f\n\n" % elapsed_time)
    print("用时为 = %.2f\n" % elapsed_time)

    # 关闭结果文件
    fileobj.close()
