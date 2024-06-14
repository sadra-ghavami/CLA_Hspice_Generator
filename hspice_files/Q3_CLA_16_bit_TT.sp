HSPICE FILE : Q3_CLA_16_bit_TT
**********Library**********
.lib 'crn90g_2d5_lk_v1d2p1.l'	TT
**********INVERTER**********
.SUBCKT	INVERTER	in1	out
M1	out	in1	0	0	nch	L=Lmin	W=Wmin
M2	out	in1	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
Vsupply	Vdin	0	Vdd
.ENDS INVERTER
**********XOR2**********
.SUBCKT	XOR2	in1	in2	out
X1	in1	in1_b	INVERTER
X2	in2	in2_b	INVERTER
M1	n1	in1	0	0	nch	L=Lmin	W='Wmin*2'
M2	out	in2	n1	0	nch	L=Lmin	W='Wmin*2'
M3	n2	in1_b	0	0	nch	L=Lmin	W='Wmin*2'
M4	out	in2_b	n2	0	nch	L=Lmin	W='Wmin*2'
M5	n3	in2_b	Vdin	Vdin	pch	L=Lmin	W='Wmin*4'
M6	out	in1	n3	Vdin	pch	L=Lmin	W='Wmin*4'
M7	n4	in2	Vdin	Vdin	pch	L=Lmin	W='Wmin*4'
M8	out	in1_b	n4	Vdin	pch	L=Lmin	W='Wmin*4'
Vsupply	Vdin	0	Vdd
.ENDS XOR2
**********NAND_2**********
.SUBCKT	NAND_2	in1	in2	out
M1	n1	in1	0	0	nch	L=Lmin	W='Wmin*2'
M2	out	in2	n1	0	nch	L=Lmin	W='Wmin*2'
M3	out	in1	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M4	out	in2	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
Vsupply	Vdin	0	Vdd
.ENDS NAND_2
**********FA**********
.SUBCKT	FA	A	B	Cin	S	Co
X0	A	B	A_XOR_B	XOR2
X1	A_XOR_B	Cin	S	XOR2
X2	A	B	A_NAND_B	NAND_2
X3	Cin	A_XOR_B	cin_NAND_AB	NAND_2
X4	cin_NAND_AB	A_NAND_B	Co	NAND_2
.ENDS FA
**********CPA_4_bit**********
.SUBCKT	CPA_4_bit	A1	B1	A2	B2	A3	B3	A4	B4	Cin	S1	S2	S3	S4	Cout
X0	A1	B1	Cin	S1	C1	FA
X1	A2	B2	C1	S2	C2	FA
X2	A3	B3	C2	S3	C3	FA
X3	A4	B4	C3	S4	Cout	FA
.ENDS CPA_4_bit
**********NAND_3**********
.SUBCKT	NAND_3	in1	in2	in3	out
M1	n1	in1	0	0	nch	L=Lmin	W='Wmin*3'
M2	n2	in2	n1	0	nch	L=Lmin	W='Wmin*3'
M3	out	in3	n2	0	nch	L=Lmin	W='Wmin*3'
M4	out	in1	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M5	out	in2	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M6	out	in3	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
Vsupply	Vdin	0	Vdd
.ENDS NAND_3
**********NAND_4**********
.SUBCKT	NAND_4	in1	in2	in3	in4	out
M1	n1	in1	0	0	nch	L=Lmin	W='Wmin*4'
M2	n2	in2	n1	0	nch	L=Lmin	W='Wmin*4'
M3	n3	in3	n2	0	nch	L=Lmin	W='Wmin*4'
M4	out	in4	n3	0	nch	L=Lmin	W='Wmin*4'
M5	out	in1	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M6	out	in2	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M7	out	in3	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
M8	out	in4	Vdin	Vdin	pch	L=Lmin	W='Wmin*2'
Vsupply	Vdin	0	Vdd
.ENDS NAND_4
**********LAG_4_bit**********
.SUBCKT	LAG_4_bit	A1	B1	A2	B2	A3	B3	A4	B4	G4:1	P4:1
X0	A1	B1	P1	XOR2
X1	A1	B1	G1_b	NAND_2
X2	G1_b	G1	INVERTER
X3	A2	B2	P2	XOR2
X4	A2	B2	G2_b	NAND_2
X5	G2_b	G2	INVERTER
X6	A3	B3	P3	XOR2
X7	A3	B3	G3_b	NAND_2
X8	G3_b	G3	INVERTER
X9	A4	B4	P4	XOR2
X10	A4	B4	G4_b	NAND_2
X11	G4_b	G4	INVERTER
X12	P1	P2	P3	P4	P4:1_b	NAND_4
X13	P4:1_b	P4:1	INVERTER
X14	G1	P2	P3	P4	in_nand1	NAND_4
X15	G2	P3	P4	in_nand2	NAND_3
X16	G3	P4	in_nand3	NAND_2
X17	G4_b	in_nand1	in_nand2	in_nand3	G4:1	NAND_4
.ENDS LAG_4_bit
**********CLA_16**********
.SUBCKT	CLA_16	A1	B1	A2	B2	A3	B3	A4	B4	A5	B5	A6	B6	A7	B7	A8	B8	A9	B9	A10	B10	A11	B11	A12	B12	A13	B13	A14	B14	A15	B15	A16	B16	Cin	S1	S2	S3	S4	S5	S6	S7	S8	S9	S10	S11	S12	S13	S14	S15	S16	Cout
X0	A1	B1	A2	B2	A3	B3	A4	B4	G4:1	P4:1	LAG_4_bit
X1	A1	B1	A2	B2	A3	B3	A4	B4	Cin	S1	S2	S3	S4	cout_s0	CPA_4_bit
X2	G4:1	G4:1_b	INVERTER
X3	Cin	P4:1	P_and_cin0	NAND_2
X4	P_and_cin0	G4:1_b	C4	NAND_2
X5	A5	B5	A6	B6	A7	B7	A8	B8	G8:5	P8:5	LAG_4_bit
X6	A5	B5	A6	B6	A7	B7	A8	B8	C4	S5	S6	S7	S8	cout_s1	CPA_4_bit
X7	G8:5	G8:5_b	INVERTER
X8	C4	P8:5	P_and_cin1	NAND_2
X9	P_and_cin1	G8:5_b	C8	NAND_2
X10	A9	B9	A10	B10	A11	B11	A12	B12	G12:9	P12:9	LAG_4_bit
X11	A9	B9	A10	B10	A11	B11	A12	B12	C8	S9	S10	S11	S12	cout_s2	CPA_4_bit
X12	G12:9	G12:9_b	INVERTER
X13	C8	P12:9	P_and_cin2	NAND_2
X14	P_and_cin2	G12:9_b	C12	NAND_2
X15	A13	B13	A14	B14	A15	B15	A16	B16	G16:13	P16:13	LAG_4_bit
X16	A13	B13	A14	B14	A15	B15	A16	B16	C12	S13	S14	S15	S16	cout_s3	CPA_4_bit
X17	G16:13	G16:13_b	INVERTER
X18	C12	P16:13	P_and_cin3	NAND_2
X19	P_and_cin3	G16:13_b	Cout	NAND_2
.ENDS CLA_16
**********Main Circuit**********
X0	A1	B1	A2	B2	A3	B3	A4	B4	A5	B5	A6	B6	A7	B7	A8	B8	A9	B9	A10	B10	A11	B11	A12	B12	A13	B13	A14	B14	A15	B15	A16	B16	Cin	S1	S2	S3	S4	S5	S6	S7	S8	S9	S10	S11	S12	S13	S14	S15	S16	Cout	CLA_16
**********Parameters**********
.param	Vdd=1.0
.param	Lmin=180n
.param	Wmin=180n
**********Simulation**********
.op
.tran	1p	301.5n
.vec	'Q3_CLA_16_bit_TT.vec'
.measure	tran	tpd	trig	V(A1)	td=1.47n	val='Vdd/2'	cross=1
+targ	V(S16)	td=1.5n	val='Vdd/2'	cross=1
.measure	tran	avgpower	AVG	power	from=0n	to=301.5n
.OPTION post=2
.end
