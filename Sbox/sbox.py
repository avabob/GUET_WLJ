class Sbox:
    # 初始化方法，接收 S-box 映射，并计算 S-box 的大小
    def __init__(self, sbox):
        self.sbox = sbox  # S-box 映射表
        self.SBOXSIZE = self.SboxSize()  # 计算 S-box 大小

    # 计算 S-box 的大小，确保 S-box 的长度是 2 的幂次方
    def SboxSize(self):
        """
        This function is used to calculate the size of a given sbox
        """
        # 获取 S-box 长度的二进制表示
        s = format(len(self.sbox), "b")
        # 计算二进制表示中 '1' 的个数
        num_of_1_in_the_binary_experission_of_the_len_of_sbox = s.count("1")
        # 断言该个数为 1，确保长度是 2 的幂次方
        assert num_of_1_in_the_binary_experission_of_the_len_of_sbox == 1
        # 返回 S-box 的大小（即二进制长度减去 1）
        return (len(s) - 1)

    # 计算位积函数 Pi_u(x)，判断 u 是否是 x 的子集
    def BitProduct(self, u, x):
        """
        Return the value of the bitproduct function Pi_u(x)
        """
        if (u & x) == u:  # 如果 u 是 x 的子集
            return 1
        else:
            return 0

    # 生成 S-box 的真值表，计算每个 u 对应的 Pi_u(y) 值
    def GetTruthTable(self, u):
        """
        Retrieve the truth table of the boolean function Pi_u(y), where y = sbox(x)
        """
        # 创建一个与 S-box 长度相同的临时列表
        temp = [u for i in range(len(self.sbox))]
        # 使用 BitProduct 函数计算 Pi_u(x) 并返回真值表
        table = list(map(self.BitProduct, temp, self.sbox))  # 将 map 对象转换为列表
        return table

    # 处理真值表，生成代数普通形式（ANF）
    def ProcessTable(self, table):
        """
        Process the truth table to get the ANF of the boolean function
        we use table size to calculate the SBOXSIZE
        """
        # 对每个大小进行处理，计算 ANF
        for i in range(0, self.SBOXSIZE):
            for j in range(0, 2**i):
                for k in range(0, 2**(self.SBOXSIZE - 1 - i)):
                    table[k + 2**(self.SBOXSIZE - 1 - i) + j*(2**(self.SBOXSIZE - i))] =\
                    table[k + 2**(self.SBOXSIZE - 1 - i) + j*(2**(self.SBOXSIZE - i))] ^\
                    table[k + j*(2**(self.SBOXSIZE - i))]

    # 生成 S-box 的代数普通形式（ANF）
    def CreatANF(self):
        """
        Return the ANF of the sbox, moreover, this function also return the ANF of boolean function which
        is the product of some coordinates of the sbox output
        """
        # 初始化 ANF，列表大小与 S-box 长度相同
        ANF = [[] for i in range(0, len(self.sbox))]
        # 对 S-box 输出的每一项计算真值表，并处理为 ANF
        for i in range(1, len(self.sbox)):
            table = self.GetTruthTable(i)
            self.ProcessTable(table)
            sqr = []
            for j in range(0, len(self.sbox)):
                if table[j] != 0:  # 如果真值表中的值不为 0，加入到结果中
                    sqr.append(j)
            ANF[i] = sqr  # 更新 ANF
        return ANF

    # 生成 S-box 的所有分割轨迹（division trails）
    def CreateDivisionTrails(self):
        """
        Return all the division trails of a given sbox
        """
        ANF = self.CreatANF()  # 获取 S-box 的 ANF
        INDP = []  # 存储分割轨迹的列表
        # 将零向量加入分割轨迹
        sqr = [0 for i in range(2 * self.SBOXSIZE)]
        INDP.append(sqr)
        # 从非零向量开始，构建分割轨迹
        for i in range(1, len(self.sbox)):
            sqn = []
            # 遍历所有的非零向量
            for j in range(1, len(self.sbox)):
                flag = False
                for entry in ANF[j]:
                    if (i | entry) == entry:  # 如果 i 是 entry 的子集
                        flag = True
                        break
                if flag:
                    sqn1 = []
                    flag_add = True
                    for t1 in sqn:
                        if (t1 | j) == j:  # 检查是否需要添加 j 到结果
                            flag_add = False
                            break
                        elif (t1 | j) == t1:
                            sqn1.append(t1)
                    if flag_add:
                        for t2 in sqn1:
                            sqn.remove(t2)
                        sqn.append(j)
            # 将每个向量转为二进制形式，存入分割轨迹
            for num in sqn:
                # 将数字格式化为二进制字符串，并进行反转
                a = format(i, "0256b")
                b = format(num, "0256b")
                a = list(reversed(list(map(int, list(a)))))
                b = list(reversed(list(map(int, list(b)))))
                # 只保留前 SBOXSIZE 位
                a = a[0:self.SBOXSIZE]
                b = b[0:self.SBOXSIZE]
                # 反转列表
                a.reverse()
                b.reverse()
                # 添加合并后的结果到分割轨迹中
                INDP.append((a + b))
        return INDP

    # 将所有分割轨迹写入文件
    def PrintfDivisionTrails(self, filename):
        """
        Write all division trails of an sbox into a file
        """
        INDP = self.CreateDivisionTrails()  # 获取分割轨迹
        fileobj = open(filename, "w")  # 打开文件以写入
        for l in INDP:
            fileobj.write(str(l) + "\n")  # 将每个分割轨迹写入文件
        fileobj.write("\n")
        fileobj.close()  # 关闭文件
