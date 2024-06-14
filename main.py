import Primitives

# Simualtion Constant Values
TIME_UNIT = "n"
PERIOD = 1.5
SLOPE = 0.0
VOH_COEFF = 0.8
VOL_COEFF = 0.2
VDD = 1.0
L_MIN = "180n"
W_MIN = "180n"
ADDER_SIZE = 16
BASE = 4
Q3_TEST_NUMBER = 200
Q2_TEST_NUMBER = 10

def Q2():
    cla = Primitives.CLA(ADDER_SIZE, BASE, 'Vdd', 'Lmin', 'Wmin')
    subckt_text = cla.create_SUBCKT()
    A = []
    B = []
    Sum = []
    cin = "Cin"
    cout = 'Cout'
    for i in range(ADDER_SIZE):
        A.append(f"A{i+1}")
        B.append(f"B{i+1}")
        Sum.append(f"S{i+1}")

    instance_line = cla.instantiate_module(A, B, cin, Sum, cout, f"X{0}")
    vector_text = cla.create_vector_file(Q2_TEST_NUMBER, 'A', 'B', 'Cin', 'S', 'Cout', PERIOD, SLOPE, TIME_UNIT, VOH_COEFF, VOL_COEFF)
    file_name = f"Q2_CLA_{ADDER_SIZE}_bit"
    hspice_file_addr = f"./hspice_files/{file_name}.sp"
    vector_file_address = f"./vector_files/{file_name}.vec"
    library_name = "crn90g_2d5_lk_v1d2p1.l"
    design_corner = "TT"
    Q2_write_hspice_code(subckt_text, instance_line, hspice_file_addr, file_name, library_name, design_corner, 'Vdd', 'Lmin', 'Wmin', Sum[ADDER_SIZE-1], A[0])
    write_vector_file(vector_text, vector_file_address)

def Q2_write_hspice_code(subckt_text : str, instnce_line : str, file_addr : str, file_name : str, library_name : str,
                      design_corner : str, voltage_param : str, lmin_param : str, wmin_param : str, last_sum : str, first_in : str):
    
    hspice_text = f"HSPICE FILE : {file_name}\n"
    hspice_text += "**********Library**********\n"
    hspice_text += f".lib '{library_name}'\t{design_corner}\n"
    hspice_text += subckt_text
    hspice_text += "**********Main Circuit**********\n"
    hspice_text += instnce_line
    hspice_text += "**********Parameters**********\n"
    hspice_text += f".param\t{voltage_param}={VDD}\n"
    hspice_text += f".param\t{lmin_param}={L_MIN}\n"
    hspice_text += f".param\t{wmin_param}={W_MIN}\n"
    hspice_text += "**********Simulation**********\n"
    hspice_text += f".op\n.tran\t1p\t{(Q2_TEST_NUMBER+1) * PERIOD}{TIME_UNIT}\n.vec\t'{file_name}.vec'\n"
    hspice_text += f".measure\ttran\ttpd\ttrig\tV({first_in})\ttd={0.98*PERIOD}n\tval='{voltage_param}/2'\tcross=1\n"
    hspice_text += f"+targ\tV({last_sum})\ttd={PERIOD}n\tval='{voltage_param}/2'\tcross=1\n"
    hspice_text += ".OPTION post=2\n.end\n"

    file = open(file_addr, 'w')
    file.write(hspice_text)
    file.close()

def Q3():
    cla = Primitives.CLA(ADDER_SIZE, BASE, 'Vdd', 'Lmin', 'Wmin')
    subckt_text = cla.create_SUBCKT()
    A = []
    B = []
    Sum = []
    cin = "Cin"
    cout = 'Cout'
    for i in range(ADDER_SIZE):
        A.append(f"A{i+1}")
        B.append(f"B{i+1}")
        Sum.append(f"S{i+1}")

    instance_line = cla.instantiate_module(A, B, cin, Sum, cout, f"X{0}")
    vector_text = cla.create_vector_file(Q3_TEST_NUMBER, 'A', 'B', 'Cin', 'S', 'Cout', PERIOD, SLOPE, TIME_UNIT, VOH_COEFF, VOL_COEFF)
    design_corners = ["TT", "SS", "FF", "SF", "FS"]
    for design_corner in design_corners:
        file_name = f"Q3_CLA_{ADDER_SIZE}_bit_{design_corner}"
        hspice_file_addr = f"./hspice_files/{file_name}.sp"
        vector_file_address = f"./vector_files/{file_name}.vec"
        library_name = "crn90g_2d5_lk_v1d2p1.l"
        Q3_write_hspice_code(subckt_text, instance_line, hspice_file_addr, file_name, library_name, design_corner, 'Vdd', 'Lmin', 'Wmin', Sum[ADDER_SIZE-1], A[0])
        write_vector_file(vector_text, vector_file_address)


def Q3_write_hspice_code(subckt_text : str, instnce_line : str, file_addr : str, file_name : str, library_name : str,
                      design_corner : str, voltage_param : str, lmin_param : str, wmin_param : str, last_sum : str, first_in : str):
    
    hspice_text = f"HSPICE FILE : {file_name}\n"
    hspice_text += "**********Library**********\n"
    hspice_text += f".lib '{library_name}'\t{design_corner}\n"
    hspice_text += subckt_text
    hspice_text += "**********Main Circuit**********\n"
    hspice_text += instnce_line
    hspice_text += "**********Parameters**********\n"
    hspice_text += f".param\t{voltage_param}={VDD}\n"
    hspice_text += f".param\t{lmin_param}={L_MIN}\n"
    hspice_text += f".param\t{wmin_param}={W_MIN}\n"
    hspice_text += "**********Simulation**********\n"
    hspice_text += f".op\n.tran\t1p\t{(Q3_TEST_NUMBER+1) * PERIOD}{TIME_UNIT}\n.vec\t'{file_name}.vec'\n"
    hspice_text += f".measure\ttran\ttpd\ttrig\tV({first_in})\ttd={0.98*PERIOD}n\tval='{voltage_param}/2'\tcross=1\n"
    hspice_text += f"+targ\tV({last_sum})\ttd={PERIOD}n\tval='{voltage_param}/2'\tcross=1\n"
    hspice_text += f".measure\ttran\tavgpower\tAVG\tpower\tfrom=0n\tto={(Q3_TEST_NUMBER+1) * PERIOD}{TIME_UNIT}\n"
    hspice_text += ".OPTION post=2\n.end\n"

    file = open(file_addr, 'w')
    file.write(hspice_text)
    file.close()

def write_vector_file(vector_file_text : str, file_addr : str):
    file = open(file_addr, 'w')
    file.write(vector_file_text)
    file.close()


if __name__ == "__main__":
    # Q2()
    Q3()


# def main_2():
#     # cla = Primitives.CLA(16, 4, 'Vdd', 'Lmin', 'Wmin')
#     # print(cla.create_SUBCKT())
#     cpa = Primitives.CPA(16, 'Vdd', 'Lmin', 'Wmin')
#     subckt_text = cpa.create_SUBCKT()
#     A = []
#     B = []
#     Sum = []
#     cin = "Cin"
#     cout = 'Cout'
#     for i in range(16):
#         A.append(f"A{i+1}")
#         B.append(f"B{i+1}")
#         Sum.append(f"S{i+1}")

#     instance_line = cpa.instantiate_module(A, B, cin, Sum, cout, f"X{0}")
#     vector_text = cpa.create_vector_file(TEST_NUMBER, 'A', 'B', 'Cin', 'S', 'Cout', PERIOD, SLOPE, TIME_UNIT, VOH_COEFF, VOL_COEFF)
#     file_name = "CPA_16_bit"
#     hspice_file_addr = f"./hspice_files/{file_name}.sp"
#     vector_file_address = f"./vector_files/{file_name}.vec"
#     library_name = "crn90g_2d5_lk_v1d2p1.l"
#     design_corner = "TT"
#     write_hspice_code(subckt_text, instance_line, hspice_file_addr, file_name, library_name, design_corner, 'Vdd', 'Lmin', 'Wmin')
#     write_vector_file(vector_text, vector_file_address)