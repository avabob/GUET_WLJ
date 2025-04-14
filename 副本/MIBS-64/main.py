from mibs import Mibs  # 从 mibs 模块导入 Mibs 类

# 主程序入口
if __name__ == "__main__":  # 判断脚本是否作为主程序运行
    rounds = int(input("请输入目标轮数: "))  # 用户输入目标回合数，并将其转换为整数
    while not (rounds > 0):  # 如果输入的回合数小于等于0，则提示重新输入
        print("轮数必须大于零！")  # 提示用户输入大于0的回合数
        rounds = int(input("请重新输入目标轮数: "))  # 重新输入回合数
    Mibs = Mibs(rounds)  # 创建一个Mibs对象，初始化时传入目标回合数

    brute_force_flag = input("请选择：（1）自动搜索  （0）手动输入 \n")  # 询问用户是否选择暴力破解（1）或探测特定情况（0）
    while (brute_force_flag not in ['0', '1']):  # 如果输入既不是0也不是1，要求重新输入
        print("请输入0或1！")  # 提示用户输入有效选项
        brute_force_flag = input("请选择：（1）自动搜索  （0）手动输入 \n")  # 重新输入

    Mibs.set_brute_force_flag(brute_force_flag)  # 设置Mibs对象的暴力破解标志
    Mibs.set_constant_bits()

# set_zero 为未知 ？
