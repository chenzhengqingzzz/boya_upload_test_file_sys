# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 13:56:11 2023

@author: LZJ
"""
import os


Pattern_H = \
'''import BY_SD_NAND_PK2.ktl

VectorChar {
	0 = G2LVM, G2LVM,	G2LVM,  G2LVM  (0);//00
	1 = G2LVM, G2LVM,	_G2LVM, _G2LVM (0);//01
	2 = G2LVM, G2LVM,	_G2LVM, _G2LVM (1);//10
	3 = G2LVM, G2LVM,	G2LVM,  G2LVM  (1);//11
	P = G2LVM, _G2LVM,	G2LVM,  _G2LVM (0);//postive
	N = G2LVM, _G2LVM,	G2LVM,  _G2LVM (1);//negative
	L = G2Z,   ELVM,	G2Z,    ELVM   (0);//LL
	R = G2Z,   ELVM,	G2Z,    _ELVM  (0); //LH
	F = G2Z,   ELVM,	G2Z,    _ELVM  (1);//HL
	H = G2Z,   ELVM,	G2Z,    ELVM   (1);//HH
	X = G2Z,   DC,		G2Z,    DC     (0); //don't care
	Z = G2Z,   G2Z,		G2Z,    G2Z    (0);//HiZ
	A = G2Z,   DC,		G2Z,    ELVM   (0);//XL (double/single)
	B = G2Z,   DC,		G2Z,    ELVM   (1);//XH (double/single)
	C = G2Z,   ELVM,	G2Z,    DC	   (0);//LX (double/single)
	D = G2Z,   ELVM,	G2Z,    DC     (1);//HX (double/single)
};

PG_VCD {
	SCK		= 0;
	CMD		= 1;
	DAT0	= 2;
	DAT1	= 3;
	DAT2	= 4;
	DAT3	= 5;
};

PG_PATTERN um_random_program {

	INIT: ( 
	    cga()=0x0, 
        cga_cmp(x)=0x0,

	    cga_mask(x) = 0xff,
		cga_mask(y) = 0xff,
		cga_mask(z) = 0xff,

        loop(0) = 8,
		loop(1) = 16,
		loop(2) = 16
	 );

'''

Pattern_E = "};"

file = ''

def cmpBit(bit, mask):
    if mask == 1:
        return bit
    else:
        return 'X'

def read(data, mask):
    if mask == 3:
        if data == 0x0:
            read = 'L'
        elif data == 0x1:
            read = 'R'
        elif data == 0x2:
            read = 'F'
        elif data == 0x3:
            read = 'H'
    elif mask == 2:
        if (data & mask) != 0:
            read = 'D'
        else:
            read = 'C'
    elif mask == 1:
        if (data & mask) != 0:
            read = 'B'
        else:
            read = 'A'
    elif mask == 0:
        read = 'X'
    return read

def CalcCRC7(bits):
    length = len(bin(bits)) - 2
    bits <<= 7
    polynomial = 0x89  # x^7 + x^3 + 1
    polynomial <<= length - 1

    for i in range(length):
        bit = (bits >> (length - 1 - i)) & 0x80
        if bit:
            bits ^= polynomial
        polynomial >>= 1

    return bits

def Ncc(timing, loop_cnt):
    print("\t(%s) repeat %d\t\"1 Z Z Z Z Z\";\t// Nxx" % (timing, loop_cnt), file = file)
    
def command_nodata(timing, cmd, data, dataLen):
    loop_cnt = 1
    crc = CalcCRC7((0x01 << dataLen + 6) + (cmd << dataLen) + data)
    crc_end = (crc << 1) + 0x1
    print("\t(%s)\t\t\t\"P 1 Z Z Z Z\";\t// START" % timing, file = file)    # start
    for i in range(4, -1, -2):
        print("\t(%s)\t\t\t\"P %d Z Z Z Z\";\t// CMD %d%d" % (timing, cmd >> i & 0x3, cmd >> (i + 1) & 0x1, cmd >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
    for i in range(dataLen - 2, -1, -2):
        if i != 0 and (data >> i & 0x3) == (data >> i - 2 & 0x3):
            loop_cnt += 1
            continue
        while loop_cnt > 31:
            print("\t(%s) repeat %d\t\"P %d Z Z Z Z\";" % (timing, 31, data >> i & 0x3), file = file)   #BIT(i+1),BIT(i)
            loop_cnt -= 31
        if loop_cnt > 1:
            print("\t(%s) repeat %d\t\"P %d Z Z Z Z\";" % (timing, loop_cnt, data >> i & 0x3), file = file)   #BIT(i+1),BIT(i)
            loop_cnt = 1
        elif loop_cnt == 1:
            print("\t(%s)\t\t\t\"P %d Z Z Z Z\";" % (timing, data >> i & 0x3), file = file)   #BIT(i+1),BIT(i)
        else:
            loop_cnt = 1
    for i in range(6, -1, -2):
        if i:
            print("\t(%s)\t\t\t\"P %d Z Z Z Z\";\t// CRC %d%d" % (timing, crc_end >> i & 0x3, crc_end >> (i + 1) & 0x1, crc_end >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
        else:
            print("\t(%s)\t\t\t\"P %d Z Z Z Z\";\t// CRC %d (0x%02X)END" % (timing, crc_end >> i & 0x3, crc_end >> (i + 1) & 0x1, crc), file = file)   #BIT(i+1),BIT(i)
    
def response_nodata_cmp(timing, cmd, data, dataLen, mask):
    print("\tdo{ um_cmdEL_datz_cyc(); } while (FAIL);", file = file)
    loop_cnt = 1
    if cmd == 0x3f:
        crc = 0x7f
    elif cmd == 2:
        crc = CalcCRC7(data)
    else:
        crc = CalcCRC7((0x00 << dataLen + 6) + (cmd << dataLen) + data)
    crc_end = (crc << 1) + 0x1
    if (mask != 0xffffffff) and (mask != 0xffffffffffffffffffffffffffffff):
        crc_mask = 0x1
        crc = 'DC'
    else:
        crc_mask = 0xff
        crc = '0x%02X'%crc
    print("\t(tset 3)\t\t\t\"1 A Z Z Z Z\";\t// START", file = file)    # start
    for i in range(4, -1, -2):
        print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CMD %d%d" % (timing, read(cmd >> i & 0x3, 0x3), cmd >> (i + 1) & 0x1, cmd >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
    for i in range(dataLen - 2, -1, -2):
        if i != 0 and read(data >> i & 0x3, mask >> i & 0x3) == read(data >> i - 2 & 0x3, mask >> i - 2 & 0x3):
            loop_cnt += 1
            continue
        while loop_cnt > 31:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, 31, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt -= 31
        if loop_cnt > 1:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, loop_cnt, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt = 1
        elif loop_cnt == 1:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";" % (timing, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
        else:
            loop_cnt = 1
    for i in range(6, -1, -2):
        if i:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CRC %s%s" % (timing, read(crc_end >> i & 0x3, crc_mask >> i & 0x3),        \
                                                                  cmpBit(crc_end >> (i + 1) & 0x1, crc_mask >> (i + 1) & 0x1),  \
                                                                  cmpBit(crc_end >> i & 0x1, crc_mask >> i & 0x1)), file = file)   #BIT(i+1),BIT(i)
        else:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CRC %s (%s)END" % (timing, read(crc_end >> i & 0x3, crc_mask >> i & 0x3),  \
                                                                            cmpBit(crc_end >> i + 1 & 0x1, crc_mask >> i + 1 & 0x1), crc), file = file)   #BIT(i+1),BIT(i)
    
def response_nodata_polling1(timing, cmd, data, dataLen, cmp_bit, mask):
    print("\tdo{ um_cmdEL_datz_cyc(); } while (FAIL);", file = file)
    loop_cnt = 1
    if cmd == 0x3f:
        crc = 0x7f
    else:
        crc = CalcCRC7((0x00 << dataLen + 6) + (cmd << dataLen) + data)
    crc_end = (crc << 1) + 0x1
    if (mask != 0xffffffff) and (mask != 0xffffffffffffffffffffffffffffff):
        crc_mask = 0x1
        crc = 'DC'
    else:
        crc_mask = 0xff
        crc = '0x%02X'%crc
    print("\t(tset 3)\t\t\t\"1 A Z Z Z Z\";\t// START", file = file)    # start
    for i in range(4, -1, -2):
        print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CMD %d%d" % (timing, read(cmd >> i & 0x3, 0x3), cmd >> (i + 1) & 0x1, cmd >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
    for i in range(dataLen - 2, -1, -2):
        if cmp_bit == i or  cmp_bit == (i + 1):
            busy_flag = 1
        elif i != 0 and read(data >> i & 0x3, mask >> i & 0x3) == read(data >> (i - 2) & 0x3, mask >> (i - 2) & 0x3):
            loop_cnt += 1
            continue
        while loop_cnt > 31:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, 31, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt -= 31
        if busy_flag == 2:
            print("\tum_cmdE%d%d_datz_double_cyc();" % (data >> (i + 1) & 0x1, data >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
            busy_flag = 0
        elif loop_cnt > 1:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, loop_cnt, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt = 1
        elif loop_cnt == 1:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";" % (timing, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
        else:
            loop_cnt = 1
        if busy_flag == 1:
            print("do {", file = file)
            busy_flag = 2
    for i in range(6, -1, -2):
        if i:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CRC %s%s" % (timing, read(crc_end >> i & 0x3, crc_mask >> i & 0x3),        \
                                                                  cmpBit(crc_end >> (i + 1) & 0x1, crc_mask >> (i + 1) & 0x1),  \
                                                                  cmpBit(crc_end >> i & 0x1, crc_mask >> i & 0x1)), file = file)   #BIT(i+1),BIT(i)
        else:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CRC %s (%s)END" % (timing, read(crc_end >> i & 0x3, crc_mask >> i & 0x3),  \
                                                                            cmpBit(crc_end >> i + 1 & 0x1, crc_mask >> i + 1 & 0x1), crc), file = file)   #BIT(i+1),BIT(i)
        
def response_nodata_polling2(timing, cmd, data, dataLen, cmp_bit, mask):
    print("\tdo{ um_cmdEL_datz_cyc(); } while (FAIL);", file = file)
    loop_cnt = 1
    if cmd == 0x3f:
        crc = 0x7f
    else:
        crc = CalcCRC7((0x00 << dataLen + 6) + (cmd << dataLen) + data)
    crc_end = (crc << 1) + 0x1
    if (mask != 0xffffffff) and (mask != 0xffffffffffffffffffffffffffffff):
        crc_mask = 0x1
        crc = 'DC'
    else:
        crc_mask = 0xff
        crc = '0x%02X'%crc
    print("\t(tset 3)\t\t\t\"1 A Z Z Z Z\";\t// START", file = file)    # start
    for i in range(4, -1, -2):
        print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CMD %d%d" % (timing, read(cmd >> i & 0x3, 0x3), cmd >> (i + 1) & 0x1, cmd >> i & 0x1), file = file)   #BIT(i+1),BIT(i)
    for i in range(dataLen - 2, -1, -2):
        if cmp_bit == i or  cmp_bit == (i + 1):
            busy_flag = 1
            if loop_cnt:
                loop_cnt -= 1
        elif i != 0 and read(data >> i & 0x3, mask >> i & 0x3) == read(data >> i - 2 & 0x3, mask >> (i - 2) & 0x3):
            loop_cnt += 1
            continue
        while loop_cnt > 31:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, 31, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt -= 31
        if loop_cnt > 1:
            print("\t(%s) repeat %d\t\"P %s Z Z Z Z\";" % (timing, loop_cnt, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
            loop_cnt = 1
        elif loop_cnt == 1:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";" % (timing, read(data >> i & 0x3, mask >> i & 0x3)), file = file)   #BIT(i+1),BIT(i)
        else:
            loop_cnt = 1
        if busy_flag:
            print("\tum_cmdE%d%d_datz_double_cyc();\n} while (FAIL);" % (data >> (i + 1) & 0x1, data >> i & 0x1), file = file) #jump busy
            busy_flag = 0
    for i in range(6, -1, -2):
        if i:
            print("\t(%s)\t\t\t\"P %s Z Z Z Z\";\t// CRC %s%s" % (timing, read(crc_end >> i & 0x3, crc_mask >> i & 0x3),        \
                                                                  cmpBit(crc_end >> (i + 1) & 0x1, crc_mask >> (i + 1) & 0x1),  \
                                                                  cmpBit(crc_end >> i & 0x1, crc_mask >> i & 0x1)), file = file)   #BIT(i+1),BIT(i)
        else:
            print("\tum_cmdE%s%s_datz_double_cyc();\t\t// CRC %s (%s)END" % (cmpBit(crc_end >> i + 1 & 0x1, crc_mask >> i + 1 & 0x1),   \
                                                                             cmpBit(crc_end >> i & 0x1, crc_mask >> i & 0x1),           \
                                                                             cmpBit(crc_end >> i + 1 & 0x1, crc_mask >> i + 1 & 0x1), crc), file = file) #busy END

def busy_polling(ACMD, R, Argument, R_CMD, R_Argument, RA_Len, BusyBit, ReadyFlag, mask):
    if ReadyFlag == 1:
        R_Argument1 = R_Argument & ~(1 << BusyBit)
        R_Argument2 = R_Argument | (1 << BusyBit)
    else:
        R_Argument1 = R_Argument | (1 << BusyBit)
        R_Argument2 = R_Argument & ~(1 << BusyBit)
    print("\t// %s = CMD55 + %s" % (ACMD, ACMD[1:]), file = file)
    print("\t// CMD55 response-R1", file = file)
    command_nodata('tset 0', 55, 0x00, 32) #CMD55
    response_nodata_cmp('tset 1', 55, 0x120, 32, 0xffffffff) #CMD55 response R1
    Ncc('tset 3', 8)
    
    print("\t// %s response-%s" % (ACMD[1:], R), file = file)
    command_nodata('tset 0', int(ACMD[4:]), Argument, RA_Len) #ACMD First
    response_nodata_polling1('tset 1', R_CMD, R_Argument1, RA_Len, BusyBit, mask) #ACMD response R
    Ncc('tset 3', 8)
    
    print("\t// %s = CMD55 + %s" % (ACMD, ACMD[1:]), file = file)
    print("\t// CMD55", file = file)
    command_nodata('tset 0', 55, 0x00, 32) #CMD55
    response_nodata_cmp('tset 1', 55, 0x120, 32, 0xffffffff) #CMD55 response R1
    Ncc('tset 3', 8)
    
    print("\t// %s response-%s" % (ACMD[1:], R), file = file)
    command_nodata('tset 0', int(ACMD[4:]), Argument, RA_Len) #ACMD Second
    response_nodata_polling2('tset 1', R_CMD, R_Argument2, RA_Len, BusyBit, mask) #ACMD response R
    
def CID(MID, OID, PNM, PRV, PSN, MDT):
    data = MID
    data = data << 16 + OID
    data = data << 40 + PNM
    data = data << 8 + PRV
    data = data << 32 + PSN
    data = data << 4 + 0x0
    data = data << 12 + MDT
    return data
    
def initial_p(file_path):
    global file
    with open(file_path, 'w+') as file:
        print(Pattern_H, file = file)
        print("\t(%s) repeat %d\t\"P 3 Z Z Z Z\";" % ('tset 0', 30), file = file)
        print("\t(%s) repeat %d\t\"P 3 Z Z Z Z\";" % ('tset 0', 30), file = file)
        print("\t(%s) repeat %d\t\"P 3 Z Z Z Z\";" % ('tset 0', 14), file = file)
        print("", file = file)
        print("\t// CMD0", file = file)
        command_nodata('tset 0', 0, 0x00, 32) #CMD0
        Ncc('tset 3', 8)
        print("\t// CMD8 response-R7", file = file)
        command_nodata('tset 0', 8, 0x01aa, 32) #CMD8
        response_nodata_cmp('tset 1', 8, 0x01aa, 32, 0xffffffff) #CMD8 response R7
        Ncc('tset 3', 8)
        #ACMD    R?   CMD-Argument R-CMD R-Argument RA_Len BusyBit ReadyFlag R_mask
        busy_polling('ACMD41', 'R3', 0x40ff8000, 0x3f, 0x80ff8000, 32, 31, 1, 0xffffffff)
        print("\t// CMD2 response-R2", file = file)
        command_nodata('tset 0', 2, 0x00, 32) #CMD2
        response_nodata_cmp('tset 1', 0x3f, CID(0x00, 0x00, 0x00, 0x00, 0x00, 0x00), 120, 0x000000000000000000000000000000) #CMD2 response R2
        Ncc('tset 3', 8)
        print("\t// CMD3 response-R6", file = file)
        command_nodata('tset 0', 3, 0x00, 32) #CMD3
        response_nodata_cmp('tset 1', 3, 0x00000600, 32, 0xffffffff) #CMD3(mask: 0x00c81e00) response R3 Standby
        Ncc('tset 3', 8)
        print("", file = file)
        print("\tum_cmdz_datz_double_cyc() stop;", file = file)
        print(Pattern_E, file = file)

if __name__ == '__main__':
    if not os.path.exists('./Pattern'):
        os.mkdir('./Pattern/')
    initial_p('./Pattern/initial_p.kpl')
    