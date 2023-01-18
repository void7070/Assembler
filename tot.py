import sys
import string
import re
import struct

cond = {'eq': 0, 'ne': 1, 'hs': 2, 'cs': 2, 'lo': 3,
        'cc': 3, 'mi': 4, 'pl': 5, 'vs': 6, 'vc': 7,
        'hi': 8, 'ls': 9, 'ge': 10, 'lt': 11, 'gt': 12,
        'le': 13, 'al': 14, 'nv': 15}

registers = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3, 'r4': 4,
             'r5': 5, 'r6': 6, 'r7': 7, 'r8': 8, 'r9': 9,
             'r10': 10, 'r11': 11, 'r12': 12, 'r13': 13,
             'r14': 14, 'r15': 15, 'sl': 10, 'fp': 11,
             'ip': 12, 'sp': 13, 'lr': 14, 'pc': 15}

sh = {'lsl': 0,'lsr': 1, 'asr':2, 'ror':3}

def make_regexp(li):
    res = '('
    for elem in li:
        res += elem + '|'
    res = res.rstrip('|')
    res += ')'
    return res

cond_regexp = make_regexp(cond.keys())

def process_cond_field(mach_code, tok):
    cond_field = tok[:2]
    if cond_field in cond:
        mach_code |= cond[cond_field] << 28
        tok = tok[2:]
#        print('\tCOND is set to ' + str(cond[cond_field]))
        print('\tCOND is set to ' + str(bin(cond[cond_field])))
    else: # if cond is undefined
        mach_code |= 14 << 28
        print('\tCOND is undefined')
    return (mach_code, tok)

def process_S_flag(mach_code, tok):
    if tok == 's':
        print('\tS flag is set')
        mach_code |= 1 << 20
        tok = tok[1:]
    return (mach_code, tok)

def process_1_args(mach_code, args):
    tmp = bin(int(args[0]))
    tmp_s= int(tmp[2:],2)
    mach_code |= tmp_s

    return mach_code

def process_2_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 12
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)

    if args[2] in registers:
        mach_code |= registers[args[2]]
    elif args[2][0] == '#':
        mach_code |= 1<< 25
        tmp = bin(int(args[2][1:]))
        if(len(tmp)<=8):
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
        else:
            rot=16
            while(True):
                if(tmp[len(tmp)-2:]=='00'):
                    rot-=1
                    tmp=tmp[:len(tmp)-2]
                else:
                    if(rot==16):
                        print('error')
                        sys.exit(1)
                    break
            
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
            mach_code |= rot << 8


    else: # operand is neither register nor constant
        print('ERROR: Invalid operand')
        sys.exit(1)
    if(len(args)==6):
        if args[5] in sh:
            mach_code |= sh[args[5]] << 5
            tmp = bin(int(args[6][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7
        if args[5] in registers:
            mach_code |= sh[args[4]] << 5
            mach_code |= registers[args[5]] << 8
            mach_code |= 1 << 4
        else:
            mach_code |= sh[args[4]] << 5
            tmp = bin(int(args[5][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7

    return mach_code

def process_3_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 12
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)
    if(len(args)==3):
        if args[2] in registers:
            mach_code |= registers[args[2]]
            mach_code |= registers[args[0]]<<16
        elif args[2][0] == '#':
            mach_code |= registers[args[0]]<<16
            mach_code |= 1<< 25
            tmp = bin(int(args[2][1:]))
            if(len(tmp)<=8):
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
    else:    
        if args[2] in registers:
            mach_code |= registers[args[2]]<<16
        else: # operand is neither register nor constant
            print('ERROR: Invalid operand')
            sys.exit(1)

        if args[3] != ',':
            print('ERROR: Invalid syntax')
            sys.exit(1)

        if args[4] in registers:
            mach_code |= registers[args[4]]
        elif args[4][0] == '#':
            mach_code |= 1<< 25
            tmp = bin(int(args[4][1:]))
            if(len(tmp)<=8):
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
            else:
                rot=16
                while(True):
                    if(tmp[len(tmp)-2:]=='00'):
                        rot-=1
                        tmp=tmp[:len(tmp)-2]
                    else:
                        if(rot==16):
                            print('error')
                            sys.exit(1)
                        break
                
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
                mach_code |= rot << 8
        else: 
            if(len(args)==6):
                if args[5] in registers:
                    mach_code |= sh[args[4]] << 5
                    mach_code |= registers[args[5]]<<8
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    mach_code |= 1 << 4
                else:
                    mach_code |= sh[args[4]] << 5
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    tmp = bin(int(args[5][1:]))
                    tmp_s= int(tmp[2:],2)
                    mach_code |= tmp_s << 7
          
        if(len(args)==8):
            if args[7] in registers:
                mach_code |= sh[args[6]] << 5
                mach_code |= registers[args[7]] << 8
                mach_code |= 1 << 4
            else:
                mach_code |= sh[args[6]] << 5
                tmp = bin(int(args[7][1:]))
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s << 7
        
    return mach_code

def process_t_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 16
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)
    if(len(args)==3):
        if args[2] in registers:
            mach_code |= registers[args[2]]
          
        elif args[2][0] == '#':
           
            mach_code |= 1<< 25
            tmp = bin(int(args[2][1:]))
            if(len(tmp)<=8):
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
    else:    
        if args[2] in registers:
            mach_code |= registers[args[2]]<<16
        else: # operand is neither register nor constant
            print('ERROR: Invalid operand')
            sys.exit(1)

        if args[3] != ',':
            print('ERROR: Invalid syntax')
            sys.exit(1)

        if args[4] in registers:
            mach_code |= registers[args[4]]
        elif args[4][0] == '#':
            mach_code |= 1<< 25
            tmp = bin(int(args[4][1:]))
            if(len(tmp)<=8):
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
            else:
                rot=16
                while(True):
                    if(tmp[len(tmp)-2:]=='00'):
                        rot-=1
                        tmp=tmp[:len(tmp)-2]
                    else:
                        if(rot==16):
                            print('error')
                            sys.exit(1)
                        break
                
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s
                mach_code |= rot << 8
        else: 
            if(len(args)==6):
                if args[5] in registers:
                    mach_code |= sh[args[4]] << 5
                    mach_code |= registers[args[5]]<<8
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    mach_code |= 1 << 4
                else:
                    mach_code |= sh[args[4]] << 5
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    tmp = bin(int(args[5][1:]))
                    tmp_s= int(tmp[2:],2)
                    mach_code |= tmp_s << 7
        if(len(args)==8):
            if args[7] in registers:
                mach_code |= sh[args[6]] << 5
                mach_code |= registers[args[7]] << 8
                mach_code |= 1 << 4
            else:
                mach_code |= sh[args[6]] << 5
                tmp = bin(int(args[7][1:]))
                tmp_s= int(tmp[2:],2)
                mach_code |= tmp_s << 7
        
    return mach_code

def process_cmp_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 16
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)

    if args[2] in registers:
        mach_code |= registers[args[2]]
    elif args[2][0] == '#':
        mach_code |= 1<< 25
        tmp = bin(int(args[2][1:]))
        if(len(tmp)<=8):
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
        else:
            rot=16
            while(True):
                if(tmp[len(tmp)-2:]=='00'):
                    rot-=1
                    tmp=tmp[:len(tmp)-2]
                else:
                    if(rot==16):
                        print('error')
                        sys.exit(1)
                    break
            
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
            mach_code |= rot << 8


    else: # operand is neither register nor constant
        print('ERROR: Invalid operand')
        sys.exit(1)
    if(len(args)==6):
        if args[5] in sh:
            mach_code |= sh[args[5]] << 5
            tmp = bin(int(args[6][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7
        if args[5] in registers:
            mach_code |= sh[args[4]] << 5
            mach_code |= registers[args[5]] << 8
            mach_code |= 1 << 4
        else:
            mach_code |= sh[args[4]] << 5
            tmp = bin(int(args[5][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7

    return mach_code

def process_mvn_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 12
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)

    if args[2] in registers:
        mach_code |= registers[args[2]]
    elif args[2][0] == '#':
        mach_code |= 1<< 25
        tmp = bin(int(args[2][1:]))
        if(len(tmp)<=8):
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
        else:
            rot=16
            while(True):
                if(tmp[len(tmp)-2:]=='00'):
                    rot-=1
                    tmp=tmp[:len(tmp)-2]
                else:
                    if(rot==16):
                        print('error')
                        sys.exit(1)
                    break
            
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
            mach_code |= rot << 8


    else: # operand is neither register nor constant
        print('ERROR: Invalid operand')
        sys.exit(1)
    if(len(args)==6):
        if args[5] in sh:
            mach_code |= sh[args[5]] << 5
            tmp = bin(int(args[6][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7
        if args[5] in registers:
            mach_code |= sh[args[4]] << 5
            mach_code |= registers[args[5]] << 8
            mach_code |= 1 << 4
        else:
            mach_code |= sh[args[4]] << 5
            tmp = bin(int(args[5][1:]))
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s << 7

    return mach_code

def process_mul_args(mach_code, args):
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 16
    else: # destination must be register
        print('ERROR: Invalid operand')
        sys.exit(1)

    if args[1] != ',':
        print('ERROR: Invalid syntax')
        sys.exit(1)
    if(len(args)==3):
        if args[2] in registers:
            mach_code |= registers[args[2]]<<8
            mach_code |= registers[args[0]]
    else:    
        if args[2] in registers:
            mach_code |= registers[args[2]]
        else: # operand is neither register nor constant
            print('ERROR: Invalid operand')
            sys.exit(1)

        if args[3] != ',':
            print('ERROR: Invalid syntax')
            sys.exit(1)

        if args[4] in registers:
            mach_code |= registers[args[4]]<<8
        else: # operand is neither register nor constant
            print('ERROR: Invalid operand')
            sys.exit(1)
        
    return mach_code

def process_instruction(tokens):
    mach_code = 0
    tok = tokens[0]
    args = tokens[1:]

    and_re = 'and' + cond_regexp + '?' + 's' + '?'
    eor_re = 'eor' + cond_regexp + '?' + 's' + '?'
    sub_re = 'sub' + cond_regexp + '?' + 's' + '?'
    rsb_re = 'rsb' + cond_regexp + '?' + 's' + '?'
    add_re = 'add' + cond_regexp + '?' + 's' + '?'
    adc_re = 'adc' + cond_regexp + '?' + 's' + '?'
    sbc_re = 'sbc' + cond_regexp + '?' + 's' + '?'
    rsc_re = 'rsc' + cond_regexp + '?' + 's' + '?'
    tst_re = 'tst' + cond_regexp + '?' + 's' + '?'
    teq_re = 'teq' + cond_regexp + '?' + 's' + '?'
    cmp_re = 'cmp' + cond_regexp + '?' + 's' + '?'
    cmn_re = 'cmn' + cond_regexp + '?' + 's' + '?'
    orr_re = 'orr' + cond_regexp + '?' + 's' + '?'
    mov_re = 'mov' + cond_regexp + '?' + 's' + '?'
    bic_re = 'bic' + cond_regexp + '?' + 's' + '?'
    mvn_re = 'mvn' + cond_regexp + '?' + 's' + '?'

    swi_re = 'swi' + cond_regexp + '?' + 's' + '?'
    
    mul_re = 'mul' + cond_regexp + '?' + 's' + '?'
    
    

    if re.match(and_re, tok):
        print('\tAND FAMILY')
        mach_code = 0b0000 << 21
        tok = tok[3:]
        
        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
               
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)
        
        mach_code = process_3_args(mach_code, args)
    
    if re.match(eor_re, tok):
        print('\tEOR FAMILY')
        mach_code = 0b0001 << 21
        tok = tok[3:]
        
        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
               
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)
        
        mach_code = process_3_args(mach_code, args)

    if re.match(sub_re, tok):
        print('\tSUB FAMILY')
        mach_code = 0b0010 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
               
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(rsb_re, tok):
        print('\tRSB FAMILY')
        mach_code = 0b0011 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
            
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(add_re, tok):
        print('\tADD FAMILY')
        mach_code = 0b0100 << 21
        tok = tok[3:]
        
        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
               
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)
        
        mach_code = process_3_args(mach_code, args)

    if re.match(adc_re, tok):
        print('\tADC FAMILY')
        mach_code = 0b0101 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
            
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(sbc_re, tok):
        print('\tSBC FAMILY')
        mach_code = 0b0110 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
            
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(rsc_re, tok):
        print('\tRSC FAMILY')
        mach_code = 0b0111 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
            
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(tst_re, tok):
        print('\tTST FAMILY')
        mach_code = 0b1000 << 21
        tok = tok[3:]
        tmps=''
        (mach_code, tmps) = process_S_flag(mach_code, 's')
        if (len(tok)!=0):
            if('s'== tok[0]):
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_t_args(mach_code, args)

    if re.match(teq_re, tok):
        print('\tTEQ FAMILY')
        mach_code = 0b1001 << 21
        tok = tok[3:]
        tmps=''
        (mach_code, tmps) = process_S_flag(mach_code, 's')
        if (len(tok)!=0):
            if('s'== tok[0]):
                
            
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_t_args(mach_code, args)

    if re.match(cmp_re, tok):
        print('\tCMP FAMILY')
        mach_code = 0b1010 << 21
        tok = tok[3:]
        tmps=''
        (mach_code, tmps) = process_S_flag(mach_code, 's')
        if (len(tok)!=0):
            if('s'== tok[0]):
                if(len(tok)>1):
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_cmp_args(mach_code, args)

    if re.match(cmn_re, tok):
        print('\tCMN FAMILY')
        mach_code = 0b1011 << 21
        tok = tok[3:]
        tmps=''
        (mach_code, tmps) = process_S_flag(mach_code, 's')
        if (len(tok)!=0):
            if('s'== tok[0]):
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_cmp_args(mach_code, args)

    if re.match(orr_re, tok):
        print('\tORR FAMILY')
        mach_code = 0b1100 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)

    if re.match(mov_re, tok):
        print('\tMOV FAMILY')
        mach_code = 0b1101 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_2_args(mach_code, args)
    
    if re.match(bic_re, tok):
        print('\tBIC FAMILY')
        mach_code = 0b1110 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_3_args(mach_code, args)
    
    if re.match(mvn_re, tok):
        print('\tMVN FAMILY')
        mach_code = 0b1111 << 21
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_mvn_args(mach_code, args)

    if re.match(swi_re, tok):
        print('\tSWI FAMILY')
        mach_code = 0b1111 << 24
        tok = tok[3:]

        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)

        mach_code = process_1_args(mach_code, args)
    
    if re.match(mul_re, tok):
        print('\tMUL FAMILY')
        mach_code = 0b1001 << 4
        tok = tok[3:]
        
        if (len(tok)!=0):
            if('s'== tok[0]):
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
                tok = tok[1:]
                (mach_code, tok) = process_cond_field(mach_code, tok)
            else:
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else:
            (mach_code, tok) = process_cond_field(mach_code, tok)
        
        mach_code = process_mul_args(mach_code, args)

    return mach_code

### main() starts here ###
    
lines = sys.stdin.readlines()
splitter = re.compile(r'([ \t\n,])')
ip=0x8080
data=[['0',0]]
for line in lines:
    tokens = splitter.split(line)
    tokens = [tok for tok in tokens
              if re.match('\s*$', tok) == None]
    mach_code = 0
    while len(tokens) > 0:
        print(hex(ip)+' : ',end='')
        print(tokens)
        ip+=0x4
        if tokens[0].endswith(':'): # process label
            print('\tLABEL ' + tokens[0].rstrip(':') + ' FOUND')
            tokens = tokens[1:]
            continue
        elif tokens[0].startswith('.'): # process directive
            print('\tDIRECTIVE ' + tokens[0] + ' FOUND')
            tokens = tokens[1:]
            continue
        else: # process instruction
            mach_code = process_instruction(tokens)
            print(hex(mach_code) + ' : Machine Instruction\n')
            print()
            #print (struct.pack('I', mach_code))
            break
