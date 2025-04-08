from sage.all import *
import re

# 读取文件内容
with open('./demo/GIFT-64_DivisionTrails.txt', 'r') as f:
    lines = f.readlines()

matrix_data = []

# 检查每行，去除空行并确保格式正确
for line in lines:
    line = line.strip()  # 去除行首尾空白字符
    if line:  # 如果行不为空
        # 去掉方括号和逗号
        cleaned_line = line.replace('[', '').replace(']', '').replace(',', '')
        # 将清理后的行分割并转换为整数
        row = list(map(int, cleaned_line.split()))
        matrix_data.append(row)

# 检查矩阵数据
if matrix_data:
    # 创建 SageMath 矩阵
    P = Matrix(ZZ, matrix_data)
    P = Polyhedron(vertices=P)

    # 使用 inequality_generator() 获取不等式
    inequalities = P.inequality_generator()

    str_inequalities_list = []
    for inequality in inequalities:
        inequality = str(inequality)
        # 提取括号内的数值
        coefficients = re.search(r'\((.*?)\)', inequality).group(1)
        coefficients = list(map(int, coefficients.split(',')))

        # 提取加号后的数字
        constant = int(re.search(r'\+ (\d+)', inequality).group(1))
        # 将 coefficients 中的每个元素转换为字符串并用空格连接
        str_inequalities = ' '.join(map(str, coefficients)) + ' ' + str(constant)
        # 打印结果：将括号内的数值和加号后的数按要求格式输出
        print(str_inequalities)
        str_inequalities_list.append(str_inequalities)

    with open('GIFT-64_Inequalities.txt', 'w') as file:
        for str_inequalitie in str_inequalities_list:
            file.write(str_inequalitie + '\n')

else:
    print("未读取到有效数据，无法创建矩阵。")