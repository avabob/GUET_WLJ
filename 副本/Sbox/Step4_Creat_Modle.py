class Present:
    # Linear inequalities for the PRESENT Sbox
    S_T = [[1, 1, 1, 1, -1, -1, -1, -1, 0],
           [0, -1, -1, -2, 1, 0, 1, -1, 3],
           [0, -1, -1, -2, 4, 3, 4, 2, 0],
           [-2, -1, -1, 0, 2, 2, 2, 1, 1],
           [-2, -1, -1, 0, 3, 3, 3, 2, 0],
           [0, 0, 0, 0, -1, 1, -1, 1, 1],
           [-2, -2, -2, -4, 1, 4, 1, -3, 7],
           [1, 1, 1, 1, -2, -2, 1, -2, 1],
           [0, -4, -4, -2, 1, -3, 1, 2, 9],
           [0, 0, 0, -2, -1, -1, -1, 2, 3],
           [0, 0, 0, 1, 1, -1, -2, -1, 2]]
    NUMBER = 9
    def __init__(self, Round, activebits):
        self.Round = Round
        self.activebits = activebits
        self.blocksize = 64
        self.filename_model = "Present_" + str(self.Round) + "_" + str(self.activebits) + ".lp"
        self.filename_result = "result_" + str(self.Round) + "_" + str(self.activebits) + ".txt"
        fileobj = open(self.filename_model, "w")
        fileobj.close()
        fileboj = open(self.filename_result, "w")
        fileobj.close()



    def ConstraintsBySbox(self, variable1, variable2):
        """
        Generate the constraints by sbox layer.
        """
        fileobj = open(self.filename_model, "a")
        for k in range(0, 16):  # k的值取决于中间状态的长度以及s盒的结构。若s盒为4*4 = 16，中间状态为64位则需要
            for coff in Present.S_T:  # coff是s盒的多项式系数和常数项，前八位为系数，最后一位为常数项
                temp = []
                for u in range(0, 4):
                    temp.append(str(coff[u]) + " " + variable1[(k * 4) + 3 - u])  # u的值为0，1，2，3 ; (k * 4) + 3 - u的值为3，2，1，0
                for v in range(0, 4):
                    temp.append(
                        str(coff[v + 4]) + " " + variable2[(k * 4) + 3 - v])  # v + 4的值为4，5，6，7 ; (k * 4) + 3 - v的值为3，2，1，0
                temp1 = " + ".join(temp)
                temp1 = temp1.replace("+ -", "- ")
                s = str(-coff[Present.NUMBER - 1])  # 最后一位，即s盒的多项式常数项
                s = s.replace("--", "")
                temp1 += " >= " + s
                fileobj.write(temp1)
                fileobj.write("\n")
        fileobj.close();