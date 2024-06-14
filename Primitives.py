import numpy as np
import random

class CLA:
    is_SUBCKT_generated = False
    
    def __init__(self, width : int, base : int, voltage_param : str, lmin_param : str, wmin_param : str):
        self.width = 2 ** int(np.log2(width))
        self.base = 2 ** int(np.log2(base))
        self.voltage_param = voltage_param
        self.lmin = lmin_param
        self.wmin = wmin_param
        self.name = f"CLA_{self.width}"
        self.Cin = "Cin"
        self.Cout = "Cout"
        self.A_input = []
        self.B_input = []
        self.Sum = []
        self.hspice_SUBCKT = ""
        self.vector_file = ""
        self.instance_num = 0
        for i in range(self.width):
            self.A_input.append(f"A{i+1}")
            self.B_input.append(f"B{i+1}")
            self.Sum.append(f"S{i+1}")

        self.CPA = CPA(self.base, self.voltage_param, self.lmin, self.wmin)
        self.nand2 = NAND(2, self.voltage_param, self.lmin, self.wmin)
        self.INV = INVERTER(self.voltage_param, self.lmin, self.wmin)
        self.LGA = LOOK_AHEAD_GENERATOR(base, self.voltage_param, self.lmin, self.wmin)

    def create_heading(self):
        self.hspice_SUBCKT += f"**********{self.name}**********\n"
        self.hspice_SUBCKT += f".SUBCKT\t{self.name}\t"
        for i in range(self.width):
            self.hspice_SUBCKT += f"{self.A_input[i]}\t"
            self.hspice_SUBCKT += f"{self.B_input[i]}\t"
        self.hspice_SUBCKT += f"{self.Cin}\t"
        for i in range(self.width):
            self.hspice_SUBCKT += f"{self.Sum[i]}\t"
        self.hspice_SUBCKT += f"{self.Cout}\n"

    def create_base_blocks(self):
        block_num = int(self.width / self.base)
        for i in range(block_num):
            cin = f"C{self.base * i}"
            cout = f"C{self.base * (i + 1)}"
            if i == 0:
                cin = self.Cin
            elif i == block_num - 1:
                cout = self.Cout
            self.hspice_SUBCKT += self.LGA.instantiate_module(self.A_input[self.base*i : self.base*(i+1)], self.B_input[self.base*i : self.base*(i+1)], f"G{self.base*(i+1)}:{self.base*i + 1}", f"P{self.base*(i+1)}:{self.base*i + 1}", f"X{self.instance_num}")
            self.instance_num += 1
            self.hspice_SUBCKT += self.CPA.instantiate_module(self.A_input[self.base*i : self.base*(i+1)], self.B_input[self.base*i : self.base*(i+1)], cin, self.Sum[self.base*i : self.base*(i+1)], f"cout_s{i}", f"X{self.instance_num}")    
            self.instance_num += 1
            self.hspice_SUBCKT += self.INV.instantiate_gate([f"G{self.base*(i+1)}:{self.base*i + 1}"], f"G{self.base*(i+1)}:{self.base*i + 1}_b", f"X{self.instance_num}")
            self.instance_num += 1
            self.hspice_SUBCKT += self.nand2.instantiate_gate([cin, f"P{self.base*(i+1)}:{self.base*i + 1}"], f"P_and_cin{i}", f"X{self.instance_num}")
            self.instance_num += 1
            self.hspice_SUBCKT += self.nand2.instantiate_gate([f"P_and_cin{i}", f"G{self.base*(i+1)}:{self.base*i + 1}_b"], cout, f"X{self.instance_num}")
            self.instance_num += 1

    def create_SUBCKT(self):
        if CLA.is_SUBCKT_generated:
            return ""
        self.hspice_SUBCKT += self.CPA.create_SUBCKT()
        self.hspice_SUBCKT += self.nand2.create_SUBCKT()
        self.hspice_SUBCKT += self.INV.create_SUBCKT()
        self.hspice_SUBCKT += self.LGA.create_SUBCKT()
        self.create_heading()
        self.create_base_blocks()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        CLA.is_SUBCKT_generated = True
        return self.hspice_SUBCKT

    def instantiate_module(self, A : list, B : list, cin : str, sum : list, cout : str, instance_name : str):
        instance_line = f"{instance_name}\t"
        for i in range(self.width):
            instance_line += f"{A[i]}\t"
            instance_line += f"{B[i]}\t"
        instance_line += f"{cin}\t"
        for i in range(self.width):
            instance_line += f"{sum[i]}\t"
        instance_line += f"{cout}\t{self.name}\n"
        return instance_line
    
    def create_vector_file(self, input_num : int, A : str, B : str, cin : str, sum : str, cout : str,
                           period : float, slope : float, time_unit : str, VOH_coeff : float, VOL_coeff : float):
        self.declare_radix()
        self.define_name_and_IO(A, B, cin, sum, cout)
        self.define_waveform_characteristics(period, slope, time_unit, VOH_coeff, VOL_coeff)
        # self.generate_random_tabular_data(input_num)
        self.generate_critical_path_data(input_num)
        return self.vector_file

    def define_name_and_IO(self, A : str, B : str, cin : str, sum : str, cout : str):
        self.vector_file += f"; define name for each vector\n"
        self.vector_file += f"vname\t{A}[{self.width}:1]\t{B}[{self.width}:1]\t{cin}\t{sum}[{self.width}:1]\t{cout}\n"
        self.vector_file += f"; define IO\n"
        self.vector_file += "IO\t" + int(self.width/4)*"I" + "\t" + int(self.width/4)*"I" + "\tI\t" + int(self.width/4)*"O" + "\tO\n"


    def generate_random_tabular_data(self, input_num : int):
        self.vector_file += "; tabular data\n"
        for i in range(input_num):
            A_value = random.randrange(0, 2 ** self.width)
            A_hex = f"{A_value:0{int(self.width/4)}x}"
            B_value = random.randrange(0, 2 ** self.width)
            B_hex = f"{B_value:0{int(self.width/4)}x}"
            Cin = random.randrange(0, 2)
            result = A_value + B_value + Cin
            res_hex = f"{result:0{int(self.width/4)+1}x}"
            cout = res_hex[0]
            res_hex = res_hex[1:]
            self.vector_file += f"{A_hex}\t{B_hex}\t{Cin}\t{res_hex}\t{cout}\n"

    def generate_critical_path_data(self, input_num: int):
        self.vector_file += "; tabular data\n"
        initial_A = f"{0:0{int(self.width/4)}x}"
        initial_B = f"{0:0{int(self.width/4)}x}"
        initial_res = f"{0:0{int(self.width/4)}x}"
        self.vector_file += f"{initial_A}\t{initial_B}\t0\t{initial_res}\t0\n"
        for i in range(input_num):
            A_value = 0
            B_value = 0
            for j in range(self.width - 2):
                rnd = random.randrange(0, 2)
                A_value = (A_value << 1) + rnd
                B_value = (B_value << 1) + (1 if rnd == 0 else 0)
            A_value = (A_value << 1) + 1
            B_value = (B_value << 1) + 1
            result = A_value + B_value
            A_hex = f"{A_value:0{int(self.width/4)}x}"
            B_hex = f"{B_value:0{int(self.width/4)}x}"
            res_hex = f"{result:0{int(self.width/4)}x}"
            self.vector_file += f"{A_hex}\t{B_hex}\t0\t{res_hex}\t0\n"

    def declare_radix(self):
        self.vector_file += f"; {self.width}-bit carry look ahead adder: A[{self.width}:1] B[{self.width}:1] cin sum[{self.width}:1] cout\n"
        self.vector_file += f"radix\t"
        self.vector_file += int(self.width/4)*"4"
        self.vector_file += "\t"
        self.vector_file += int(self.width/4)*"4"
        self.vector_file += "\t1\t"
        self.vector_file += int(self.width/4)*"4"
        self.vector_file += "\t1\n"

    def define_waveform_characteristics(self, period, slope, time_unit, VOH_coeff, VOL_coeff):
        self.vector_file += "; define waveform characteristics \n"
        self.vector_file += f"tunit\t{time_unit}s\n"
        self.vector_file += f"Period\t{period}\n"
        self.vector_file += f"tdelay\t{period*0.98}\t" + int(self.width/4)*"0" + "\t" + int(self.width/4)*"0" + "\t0\t" + int(self.width/4)*"F" + "\t1\n"
        self.vector_file += f"Slope\t{slope}\n"
        self.vector_file += f"VOH\t'{VOH_coeff}*{self.voltage_param}'\nVOL\t'{VOL_coeff}*{self.voltage_param}'\n"
        self.vector_file += f"VIL\t0\nVIH\t{self.voltage_param}\n"


        

class GATE:
    def __init__(self, input_num, voltage_param, lmin_param, wmin_param):
        self.num = input_num
        self.name = f"GATE_{self.num}"
        self.voltage_param = voltage_param
        self.voltage = "Vdin"
        self.lmin = lmin_param
        self.wmin = wmin_param
        self.hspice_SUBCKT = ""
        self.inputs = []
        self.output = "out"
        for i in range(self.num):
            self.inputs.append(f"in{i+1}")

    def create_SUBCKT(self):
        self.create_heading()
        self.instanciate_nmos()
        self.instanciate_pmos()
        self.add_voltage_source()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        return self.hspice_SUBCKT
    
    def create_heading(self):
        self.hspice_SUBCKT += f"**********{self.name}**********\n"
        self.hspice_SUBCKT += f".SUBCKT\t{self.name}\t"
        for i in range(self.num):
            self.hspice_SUBCKT += f"{self.inputs[i]}\t"
        self.hspice_SUBCKT += f"{self.output}\n"

    def add_voltage_source(self):
        self.hspice_SUBCKT += f"Vsupply\t{self.voltage}\t0\t{self.voltage_param}\n"

    def instanciate_nmos(self):
        pass
    
    def instanciate_pmos(self):
        pass

    def instantiate_gate(self, input_names : list, output_name : str, instance_name : str):
        instance_line = f"{instance_name}\t"
        for i in range(self.num):
            instance_line += f"{input_names[i]}\t"
        instance_line += f"{output_name}\t{self.name}\n"
        return instance_line



class NAND(GATE):
    different_input_num = []

    def __init__(self, input_num, voltage_param, lmin_param, wmin_param):
        super().__init__(input_num, voltage_param, lmin_param, wmin_param)
        self.name = f"NAND_{self.num}"

    def create_SUBCKT(self):
        for num in NAND.different_input_num:
            if num == self.num:
                return ""
        NAND.different_input_num.append(self.num)
        return super().create_SUBCKT()

    def instanciate_nmos(self):
        for i in range(self.num):
            drain = f"n{i+1}"
            source = f"n{i}"

            if i == 0:
                source = "0"
            if i == self.num - 1:
                drain = self.output
            
            self.hspice_SUBCKT += f"M{i+1}\t{drain}\t{self.inputs[i]}\t{source}\t0\tnch\tL={self.lmin}\tW='{self.wmin}*{self.num}'\n"

    def instanciate_pmos(self):
        for i in range(self.num):
            self.hspice_SUBCKT += f"M{self.num+i+1}\t{self.output}\t{self.inputs[i]}\t{self.voltage}\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*2'\n"

class NOR(GATE):
    different_input_num = []
    def __init__(self, input_num, voltage_param, lmin_param, wmin_param):
        super().__init__(input_num, voltage_param, lmin_param, wmin_param)
        self.name = f"NOR_{self.num}"

    def create_SUBCKT(self):
        for num in NOR.different_input_num:
            if num == self.num:
                return ""
        NOR.different_input_num.append(self.num)
        return super().create_SUBCKT()
        
    def instanciate_pmos(self):
        for i in range(self.num):
            drain = f"n{i+1}"
            source = f"n{i}"

            if i == 0:
                source = self.voltage
            if i == self.num - 1:
                drain = self.output
            
            self.hspice_SUBCKT += f"M{self.num+i+1}\t{drain}\t{self.inputs[i]}\t{source}\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*{self.num*2}'\n"

    def instanciate_nmos(self):
        for i in range(self.num):
            self.hspice_SUBCKT += f"M{i+1}\t{self.output}\t{self.inputs[i]}\t0\t0\tnch\tL={self.lmin}\tW='{self.wmin}'\n"

class INVERTER(GATE):
    is_SUBCKT_generated = False
    def __init__(self, voltage_param, lmin_param, wmin_param):
        super().__init__(1, voltage_param, lmin_param, wmin_param)
        self.name = "INVERTER"

    def create_SUBCKT(self):
        if INVERTER.is_SUBCKT_generated:
            return ""
        INVERTER.is_SUBCKT_generated = True
        return super().create_SUBCKT()
    
    def instanciate_nmos(self):
        self.hspice_SUBCKT += f"M1\t{self.output}\t{self.inputs[0]}\t0\t0\tnch\tL={self.lmin}\tW={self.wmin}\n"

    def instanciate_pmos(self):
        self.hspice_SUBCKT += f"M2\t{self.output}\t{self.inputs[0]}\t{self.voltage}\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*2'\n"


class XOR2(GATE):
    is_SUBCKT_generated = False
    def __init__(self, voltage_param, lmin_param, wmin_param):
        super().__init__(2, voltage_param, lmin_param, wmin_param)
        self.name = "XOR2"
        self.inputs_bar = []
        for i in range(self.num):
            self.inputs_bar.append(self.inputs[i]+"_b")

    def create_SUBCKT(self):
        if XOR2.is_SUBCKT_generated:
            return ""
        inv = INVERTER(self.voltage_param, self.lmin, self.wmin)
        self.hspice_SUBCKT += inv.create_SUBCKT()
        self.create_heading()
        self.hspice_SUBCKT += inv.instantiate_gate([self.inputs[0]], self.inputs_bar[0], 'X1')
        self.hspice_SUBCKT += inv.instantiate_gate([self.inputs[1]], self.inputs_bar[1], 'X2')
        self.instanciate_nmos()
        self.instanciate_pmos()
        self.add_voltage_source()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        XOR2.is_SUBCKT_generated = True
        return self.hspice_SUBCKT

    def instanciate_nmos(self):
        self.hspice_SUBCKT += f"M1\tn1\t{self.inputs[0]}\t0\t0\tnch\tL={self.lmin}\tW='{self.wmin}*2'\n"
        self.hspice_SUBCKT += f"M2\t{self.output}\t{self.inputs[1]}\tn1\t0\tnch\tL={self.lmin}\tW='{self.wmin}*2'\n"
        self.hspice_SUBCKT += f"M3\tn2\t{self.inputs_bar[0]}\t0\t0\tnch\tL={self.lmin}\tW='{self.wmin}*2'\n"
        self.hspice_SUBCKT += f"M4\t{self.output}\t{self.inputs_bar[1]}\tn2\t0\tnch\tL={self.lmin}\tW='{self.wmin}*2'\n"

    def instanciate_pmos(self):
        self.hspice_SUBCKT += f"M5\tn3\t{self.inputs_bar[1]}\t{self.voltage}\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*4'\n"
        self.hspice_SUBCKT += f"M6\t{self.output}\t{self.inputs[0]}\tn3\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*4'\n"
        self.hspice_SUBCKT += f"M7\tn4\t{self.inputs[1]}\t{self.voltage}\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*4'\n"
        self.hspice_SUBCKT += f"M8\t{self.output}\t{self.inputs_bar[0]}\tn4\t{self.voltage}\tpch\tL={self.lmin}\tW='{self.wmin}*4'\n"


class LOOK_AHEAD_GENERATOR():
    is_SUBCKT_generated = False

    def __init__(self, bit_num, voltage_param, lmin_param, wmin_param):
        self.num = bit_num
        self.gate_num = 0
        self.name = f"LAG_{self.num}_bit"
        self.voltage_param = voltage_param
        self.voltage = "Vdin"
        self.lmin = lmin_param
        self.wmin = wmin_param
        self.hspice_SUBCKT = ""
        self.A_input = []
        self.B_input = []
        self.P = []
        self.G = []
        self.generate = f"G{self.num}:1"
        self.propagate = f"P{self.num}:1"
        for i in range(self.num):
            self.A_input.append(f"A{i+1}")
            self.B_input.append(f"B{i+1}")
            self.P.append(f"P{i+1}")
            self.G.append(f"G{i+1}")
        self.xor2 = XOR2(self.voltage_param, self.lmin, self.wmin)
        self.inv = INVERTER(self.voltage_param, self.lmin, self.wmin)
        # self.nand = NAND(2, self.voltage_param, self.lmin, self.wmin)
        # self.nand_n = NAND(self.num, self.voltage_param, self.lmin, self.wmin)
        self.nand = []
        for i in range(self.num - 1):
            self.nand.append(NAND(i+2, self.voltage_param, self.lmin, self.wmin))
        
    def create_heading(self):
        self.hspice_SUBCKT += f"**********{self.name}**********\n"
        self.hspice_SUBCKT += f".SUBCKT\t{self.name}\t"
        for i in range(self.num):
            self.hspice_SUBCKT += f"{self.A_input[i]}\t"
            self.hspice_SUBCKT += f"{self.B_input[i]}\t"
        self.hspice_SUBCKT += f"{self.generate}\t{self.propagate}\n"

    def create_generate_propagate(self):
        for i in range(self.num):
            self.hspice_SUBCKT += self.xor2.instantiate_gate([self.A_input[i], self.B_input[i]], self.P[i], f"X{self.gate_num}")
            self.gate_num += 1
            self.hspice_SUBCKT += self.nand[0].instantiate_gate([self.A_input[i], self.B_input[i]], f"G{i+1}_b", f"X{self.gate_num}")
            self.gate_num += 1
            self.hspice_SUBCKT += self.inv.instantiate_gate([f"G{i+1}_b"], self.G[i], f"X{self.gate_num}")
            self.gate_num += 1

    def create_propagate_output(self):
        self.hspice_SUBCKT += self.nand[self.num-2].instantiate_gate(self.P, f"P{self.num}:1_b", f"X{self.gate_num}")
        self.gate_num += 1
        self.hspice_SUBCKT += self.inv.instantiate_gate([f"P{self.num}:1_b"], self.propagate, f"X{self.gate_num}")
        self.gate_num += 1

    # def create_generate_output(self):
    #     G_prev = self.G[0]
    #     for i in range(self.num - 1):
    #         self.hspice_SUBCKT += self.nand[0].instantiate_gate([self.P[i+1], G_prev], f"int_wire{i}", f"X{self.gate_num}")
    #         self.gate_num += 1
    #         self.hspice_SUBCKT += self.nand[0].instantiate_gate([f"int_wire{i}", self.G[i+1]], f"G{i+2}:1", f"X{self.gate_num}")
    #         self.gate_num += 1
    #         G_prev = f"G{i+2}:1"
    
    def create_generate_output(self):
        final_nand_inputs = []
        final_nand_inputs.append(f"G{self.num}_b")
        for i in range(self.num - 1):
            nand_in = []
            nand_in.append(self.G[i])
            for j in range(i+1, self.num):
                nand_in.append(self.P[j])
            self.hspice_SUBCKT += self.nand[self.num - 2 - i].instantiate_gate(nand_in, f"in_nand{i+1}", f"X{self.gate_num}")
            self.gate_num += 1
            final_nand_inputs.append(f"in_nand{i+1}")
        self.hspice_SUBCKT += self.nand[self.num - 2].instantiate_gate(final_nand_inputs, self.generate, f"X{self.gate_num}")
        self.gate_num += 1

    def create_SUBCKT(self):
        if LOOK_AHEAD_GENERATOR.is_SUBCKT_generated:
            return ""
        
        self.hspice_SUBCKT += self.xor2.create_SUBCKT()
        self.hspice_SUBCKT += self.inv.create_SUBCKT()
        # self.hspice_SUBCKT += self.nand.create_SUBCKT()
        # self.hspice_SUBCKT += self.nand_n.create_SUBCKT()
        for gate in self.nand:
            self.hspice_SUBCKT += gate.create_SUBCKT()
        self.create_heading()
        self.create_generate_propagate()
        self.create_propagate_output()
        self.create_generate_output()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        LOOK_AHEAD_GENERATOR.is_SUBCKT_generated = True
        return self.hspice_SUBCKT

    def instantiate_module(self, A_input : list, B_input : list, generate_output : str, propagate_output : str, instance_name : str):
        instance_line = f"{instance_name}\t"
        for i in range(self.num):
            instance_line += f"{A_input[i]}\t{B_input[i]}\t"
        instance_line += f"{generate_output}\t{propagate_output}\t{self.name}\n"
        return instance_line
    
class FA():
    is_SUBCKT_generated = False
    
    def __init__(self, voltage_param, lmin_param, wmin_param):
        self.gate_num = 0
        self.name = f"FA"
        self.voltage_param = voltage_param
        self.voltage = "Vdin"
        self.lmin = lmin_param
        self.wmin = wmin_param
        self.hspice_SUBCKT = ""
        self.A = "A"
        self.B = "B"
        self.cin = "Cin"
        self.sum = "S"
        self.cout = "Co"
        
        self.xor2 = XOR2(self.voltage_param, self.lmin, self.wmin)
        self.nand = NAND(2, self.voltage_param, self.lmin, self.wmin)

    def create_heading(self):
        self.hspice_SUBCKT += f"**********{self.name}**********\n"
        self.hspice_SUBCKT += f".SUBCKT\t{self.name}\t"
        self.hspice_SUBCKT += f"{self.A}\t{self.B}\t{self.cin}\t{self.sum}\t{self.cout}\n"

    def create_sum(self):
        self.hspice_SUBCKT += self.xor2.instantiate_gate([self.A, self.B], "A_XOR_B", f"X{self.gate_num}")
        self.gate_num += 1
        self.hspice_SUBCKT += self.xor2.instantiate_gate(["A_XOR_B", self.cin], self.sum, f"X{self.gate_num}")
        self.gate_num += 1
    
    def create_cout(self):
        self.hspice_SUBCKT += self.nand.instantiate_gate([self.A, self.B], "A_NAND_B", f"X{self.gate_num}")
        self.gate_num += 1
        self.hspice_SUBCKT += self.nand.instantiate_gate([self.cin, "A_XOR_B"], "cin_NAND_AB", f"X{self.gate_num}")
        self.gate_num += 1
        self.hspice_SUBCKT += self.nand.instantiate_gate(["cin_NAND_AB", "A_NAND_B"], self.cout, f"X{self.gate_num}")
        self.gate_num += 1

    def create_SUBCKT(self):
        if FA.is_SUBCKT_generated:
            return ""
        self.hspice_SUBCKT += self.xor2.create_SUBCKT()
        self.hspice_SUBCKT += self.nand.create_SUBCKT()
        self.create_heading()
        self.create_sum()
        self.create_cout()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        FA.is_SUBCKT_generated = True
        return self.hspice_SUBCKT
    
    def instantiate_module(self, A : str, B : str, cin : str, sum : str, cout : str, instance_name : str):
        instance_line = f"{instance_name}\t"
        instance_line += f"{A}\t{B}\t{cin}\t{sum}\t{cout}\t{self.name}\n"
        return instance_line


class CPA():
    is_SUBCKT_generated = False

    def __init__(self, bit_num, voltage_param, lmin_param, wmin_param):
        self.num = bit_num
        self.gate_num = 0
        self.name = f"CPA_{self.num}_bit"
        self.voltage_param = voltage_param
        self.lmin = lmin_param
        self.wmin = wmin_param
        self.hspice_SUBCKT = ""
        self.vector_file = ""
        self.A_input = []
        self.B_input = []
        self.sum = []
        self.cin = "Cin"
        self.cout = "Cout"
        for i in range(self.num):
            self.A_input.append(f"A{i+1}")
            self.B_input.append(f"B{i+1}")
            self.sum.append(f"S{i+1}")

        self.FA = FA(self.voltage_param, self.lmin, self.wmin)

    def create_heading(self):
        self.hspice_SUBCKT += f"**********{self.name}**********\n"
        self.hspice_SUBCKT += f".SUBCKT\t{self.name}\t"
        for i in range(self.num):
            self.hspice_SUBCKT += f"{self.A_input[i]}\t"
            self.hspice_SUBCKT += f"{self.B_input[i]}\t"
        self.hspice_SUBCKT += f"{self.cin}\t"
        for i in range(self.num):
            self.hspice_SUBCKT += f"{self.sum[i]}\t"
        self.hspice_SUBCKT += f"{self.cout}\n"

    def instantiate_FAs(self):   
        for i in range(self.num):
            cin = f"C{i}"
            cout = f"C{i+1}"
            
            if i == 0:
                cin = self.cin
            elif i == self.num - 1:
                cout = self.cout

            self.hspice_SUBCKT += self.FA.instantiate_module(self.A_input[i], self.B_input[i], cin, self.sum[i], cout, f"X{self.gate_num}")
            self.gate_num += 1

    def create_SUBCKT(self):
        if CPA.is_SUBCKT_generated:
            return ""
        
        self.hspice_SUBCKT += self.FA.create_SUBCKT()
        self.create_heading()
        self.instantiate_FAs()
        self.hspice_SUBCKT += f".ENDS {self.name}\n"
        CPA.is_SUBCKT_generated = True
        return self.hspice_SUBCKT
    
    def instantiate_module(self, A : list, B : list, cin : str, sum : list, cout : str, instance_name : str):
        instance_line = f"{instance_name}\t"
        for i in range(self.num):
            instance_line += f"{A[i]}\t"
            instance_line += f"{B[i]}\t"
        instance_line += f"{cin}\t"
        for i in range(self.num):
            instance_line += f"{sum[i]}\t"
        instance_line += f"{cout}\t{self.name}\n"
        return instance_line
    
    def create_vector_file(self, input_num : int, A : str, B : str, cin : str, sum : str, cout : str,
                           period : float, slope : float, time_unit : str, VOH : float, VOL : float):
        self.declare_radix()
        self.define_name_and_IO(A, B, cin, sum, cout)
        self.define_waveform_characteristics(period, slope, time_unit, VOH, VOL)
        self.generate_random_tabular_data(input_num)
        return self.vector_file

    def define_name_and_IO(self, A : str, B : str, cin : str, sum : str, cout : str):
        self.vector_file += f"; define name for each vector\n"
        self.vector_file += f"vname\t{A}[{self.num}:1]\t{B}[{self.num}:1]\t{cin}\t{sum}[{self.num}:1]\t{cout}\n"
        self.vector_file += f"; define IO\n"
        self.vector_file += "IO\t" + int(self.num/4)*"I" + "\t" + int(self.num/4)*"I" + "\tI\t" + int(self.num/4)*"O" + "\tO\n"


    def generate_random_tabular_data(self, input_num : int):
        self.vector_file += "; tabular data\n"
        for i in range(input_num):
            A_value = random.randrange(0, 2 ** self.num)
            A_hex = f"{A_value:0{int(self.num/4)}x}"
            B_value = random.randrange(0, 2 ** self.num)
            B_hex = f"{B_value:0{int(self.num/4)}x}"
            Cin = random.randrange(0, 2)
            result = A_value + B_value + Cin
            res_hex = f"{result:0{int(self.num/4)+1}x}"
            cout = res_hex[0]
            res_hex = res_hex[1:]
            self.vector_file += f"{A_hex}\t{B_hex}\t{Cin}\t{res_hex}\t{cout}\n"

    def declare_radix(self):
        self.vector_file += f"; {self.num}-bit carry propagation adder: A[{self.num}:1] B[{self.num}:1] cin sum[{self.num}:1] cout\n"
        self.vector_file += f"radix\t"
        self.vector_file += int(self.num/4)*"4"
        self.vector_file += "\t"
        self.vector_file += int(self.num/4)*"4"
        self.vector_file += "\t1\t"
        self.vector_file += int(self.num/4)*"4"
        self.vector_file += "\t1\n"

    def define_waveform_characteristics(self, period, slope, time_unit, VOH, VOL):
        self.vector_file += "; define waveform characteristics \n"
        self.vector_file += f"tunit\t{time_unit}s\n"
        self.vector_file += f"Period\t{period}\n"
        self.vector_file += f"tdelay\t{period*0.95}\t" + int(self.num/4)*"0" + "\t" + int(self.num/4)*"0" + "\t0\t" + int(self.num/4)*"F" + "\t1\n"
        self.vector_file += f"Slope\t{slope}\n"
        self.vector_file += f"VOH\t{VOH}\nVOL\t{VOL}\n"





        

    
        