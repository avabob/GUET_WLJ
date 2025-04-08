
import copy

class Reduce():
    def __init__(self, filename):
        self.filename = filename   # 存储文件路径

    def ReadIne(self):
        """
        从文件中读取线性不等式，并将其存储为一个列表
        """
        fileobj = open(self.filename, "r")  # 打开文件
        ine = []  # 存储不等式的列表
        for i in fileobj:  # 遍历文件中的每一行
            ine.append(list(map(int, (i.strip()).split())))  # 将每行的内容分割并转换为整数后添加到ine列表中
        fileobj.close()  # 关闭文件
        return ine  # 返回读取的线性不等式列表

    @staticmethod
    def Integer2Bitlist(n, l):
        """
        将整数n转换为二进制表示，并将二进制长度限制为l。
        对于长度小于l的二进制表示，我们在前面添加0。
        假设整数n的二进制表示的长度小于256。
        """
        s = list(map(int, bin(n)[2:].zfill(l)))  # 将map对象转换为list
        s = s[len(s) - l :]  # 保留长度为l的最低位（从右往左）
        return s  # 返回二进制列表

    @staticmethod
    def ValueOfExpression(p, l):
        """
        计算线性不等式在点p处的值，l表示一个线性不等式。
        """
        assert len(p) + 1 == len(l)  # 检查点p的长度加1是否等于不等式l的长度
        # 深拷贝p列表，因为我们会修改列表，而这可能会影响到外部的p列表
        temp_p = copy.deepcopy(p)
        temp_p.append(1)  # 添加1作为常数项，假设线性不等式是Ax + b的形式
        # 计算Ax + b的结果，使用zip将p和l中的元素一一对应相乘并求和
        return sum([x * y for (x, y) in zip(temp_p, l)])

    def InequalitySizeReduce(self):
        """
        给定一组点和对应的H-Representation，从H-Representation中选择一个子集的不等式，
        该子集的表达式等价于描述这些点的集合。
        """
        with open('./GIFT-64_DivisionTrails.txt', 'r') as file:  ###
            points = []
            for line in file:
                # 去掉行首尾空格，去掉括号，分割数字并转换为整数
                line = line.strip()[1:-1]  # 去掉两边的括号
                # 使用列表推导式，只处理非空字符串并将其转换为整数
                numbers = [int(x.strip()) for x in line.split(',') if x.strip()]
                points.append(numbers)

        inequalities = self.ReadIne()  # 读取线性不等式
        assert len(points) > 0  # 确保点集非空
        assert len(inequalities) > 0  # 确保不等式集非空
        assert len(points[0]) + 1 == len(inequalities[0])  # 检查点的维度和不等式的维度是否匹配
        length = len(points[0])  # 获取点的维度

        # 获取所有可能的点集 {0,1}^n，表示为二进制位
        apoints = [Reduce.Integer2Bitlist(i, length) for i in range(2**length)]
        # 获取补集：所有不在points中的点
        cpoints = [p for p in apoints if p not in points]
        ineq = copy.deepcopy(inequalities)  # 深拷贝不等式集
        rineq = []  # 存储选择的子集不等式

        # 当补集cpoints不为空时，继续处理
        while len(cpoints) > 0:
            temp_p = []  # 存储临时点集
            temp_l = []  # 存储临时选择的不等式
            # 找到一个不等式，这个不等式在cpoints中不满足的点最多
            for l in ineq:
                temp = [p for p in cpoints if (Reduce.ValueOfExpression(p, l) < 0)]  # 计算不等式值，找到不满足不等式的点
                if len(temp) > len(temp_p):  # 如果当前不等式不满足的点更多，则更新temp_p和temp_l
                    temp_p = temp
                    temp_l = l
            # 将这些点从补集cpoints中移除
            for p in temp_p:
                cpoints.remove(p)
            # 将选择的不等式添加到结果集合中
            rineq.append(temp_l)
            # 移除已选择的不等式
            ineq.remove(temp_l)

        return rineq  # 返回最终选择的不等式子集
