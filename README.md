# Assembler
코드 설명
들여쓰기는 문서작성 시 제대로 옮겨지지 않는 경우가 있으므로 코드를 확인하여 주시길 바랍니다. 또한, 코드가 길어 생략한 부분이 있습니다. 상세한 코드는 코드를 확인하여 주십시오.
// 모듈 import 부분 및 cond(조건 코드 : key 매칭), registers(레지스터:key)와 sh(시프트:key) 정의 
import .. //생략
cond = //생략
registers = //생략

sh = {'lsl': 0,'lsr': 1, 'asr':2, 'ror':3}

make_regexp, process_cond_field, process_S_flag 함수 정의 
def make_regexp(li):
   //생략
cond_regexp = make_regexp(cond.keys())

def process_cond_field(mach_code, tok):
   //생략

def process_S_flag(mach_code, tok):
   //생략

// process_2_args 변형 함수들
def process_1_args(mach_code, args): // swi 때 호출 , args로 들어오는 값을 2진수로 바꾸어서 |= 연산후 반환
    tmp = bin(int(args[0]))
    tmp_s= int(tmp[2:],2)
    mach_code |= tmp_s
    return mach_code

def process_2_args(mach_code, args): // 상수 값이 들어올때를 고려하여 작성, mov때 호출
   //중략

    if args[2] in registers:
        mach_code |= registers[args[2]]
    elif args[2][0] == '#':
        mach_code |= 1<< 25
        tmp = bin(int(args[2][1:]))
        if(len(tmp)<=8): // 8bit 이내의 값이면 그대로 mach_code 로 반영
            tmp_s= int(tmp[2:],2)
            mach_code |= tmp_s
        else: //8bit 이내의 값이 아닌 경우 rot를 통한 표현(rot가 불가능한 값은 들어오지 않는다고 가정)
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
    if(len(args)==6): //만일 시프트 연산이 있을경우
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

def process_3_args(mach_code, args)://가장 많은 opcode에서 쓰인 변환 코드, 레지스터 3개 입력 고려, 2개 입력시 자동으로 결과 레지스터 설정. 
    //중략
    if(len(args)==3):// 입력이 2개인 경우
        if args[2] in registers: //레지스터면 자동으로 결과 레지스터 설정
            mach_code |= registers[args[2]]
            mach_code |= registers[args[0]]<<16
        elif args[2][0] == '#': // 상수여도 결과 레지스터 설정 (이 경우 레지스터가 1개이므로)
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
            if(len(args)==6): // 2개의 레지스터와 시프트 연산시 
                if args[5] in registers: //시프트로 들어온게 레지스터일때
                    mach_code |= sh[args[4]] << 5
                    mach_code |= registers[args[5]]<<8
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    mach_code |= 1 << 4
                else:// 상수 일때
                    mach_code |= sh[args[4]] << 5
                    mach_code -= registers[args[2]]<<16
                    mach_code |= registers[args[2]]
                    mach_code |= registers[args[0]]<<16
                    tmp = bin(int(args[5][1:]))
                    tmp_s= int(tmp[2:],2)
                    mach_code |= tmp_s << 7
        if(len(args)==8):// 3개의 레지스터와 시프트 연산시..
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

def process_t_args(mach_code, args): // 일부 코드의 입력순번에 따른 mach_code가 순서변경이 있어 따로 작성, 바뀐 포인트만 남겨놓고 생략
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 16
    //중략
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
       //중략

        if args[4] in registers:
            mach_code |= registers[args[4]]
            //생략
              

def process_cmp_args(mach_code, args): //cmp도 별도작성. 
    # match_reg is list of matching register
    if args[0] in registers:
        mach_code |= registers[args[0]] << 16
   //중략

    if args[2] in registers:
        mach_code |= registers[args[2]]
    //중략	
    if(len(args)==6)://안쪽 내용이 process_3_arg과 통일하기 힘듬.
    //생략
       

def process_mvn_args(mach_code, args)://mvn도 별도작성. cmp쪽이랑 비슷
  
  //중략
    if(len(args)==6)://안쪽 내용이 process_3_arg과 통일하기 힘듬.
        //생략

def process_mul_args(mach_code, args)://mul은 mach_code가 별도. 입력값은 무조건 레지스터
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

   // ***_re를 통해 밑의 비교가능, 기존의 mov_re 구문으로 통일함. 
    and_re = 'and' + cond_regexp + '?' + 's' + '?'
    eor_re ,sub_re, rsb_re ..... //생략

    swi_re = 'swi' + cond_regexp + '?' + 's' + '?'
    
    mul_re = 'mul' + cond_regexp + '?' + 's' + '?'

    if re.match(and_re, tok): //and를 입력으로 받았을 때.. process_3_args 호출
        print('\tAND FAMILY')
        mach_code = 0b0000 << 21
        tok = tok[3:]
        
        if (len(tok)!=0): //조건이 추가로 붙어 있다면
            if('s'== tok[0]): //s가 있다면 플래그를 세운 후, s를 빼고 cond코드 읽기 
                tmps=''
                (mach_code, tmps) = process_S_flag(mach_code, 's')
               
                if(len(tok)>1): //s를 포함하고 cond 지정시
                    tok = tok[1:]
                    (mach_code, tok) = process_cond_field(mach_code, tok)
            else: //s 없이 cond 지정시
                (mach_code, tok) = process_cond_field(mach_code, tok)
        else: //따로 조건이 없을시
            (mach_code, tok) = process_cond_field(mach_code, tok)
        
        mach_code = process_3_args(mach_code, args)
    
    if re.match(eor_re, tok): //eor를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(sub_re, tok): //sub를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(rsb_re, tok): //rsb를 입력으로 받았을 때.. process_3_args 호출
       	//생략
    if re.match(add_re, tok): //add를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(adc_re, tok): //adc를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(sbc_re, tok): //sbc를 입력으로 받았을 때.. process_3_args 호출
      	//생략
    if re.match(rsc_re, tok): //rsc를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(tst_re, tok): //tst를 입력으로 받았을 때.. process_t_args 호출
      	//생략
    if re.match(teq_re, tok): //teq를 입력으로 받았을 때.. process_t_args 호출
        //생략
    if re.match(cmp_re, tok): //cmp를 입력으로 받았을 때.. process_cmp_args 호출
        print('\tCMP FAMILY')
        mach_code = 0b1010 << 21
        tok = tok[3:]
        tmps=''
        (mach_code, tmps) = process_S_flag(mach_code, 's') //cmp는 s를 입력받지 않아도 s 플래그가 세워지므로... 해당 코드 말고도 s 입력 없이 s 플래그가 세워지는 코드는 해당 코드를 사용하여 세움.
        //생략
    if re.match(cmn_re, tok): //cmn를 입력으로 받았을 때.. process_cmp_args 호출
        //생략
    if re.match(orr_re, tok): //orr를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(mov_re, tok): //mov를 입력으로 받았을 때.. process_2_args 호출
        //생략
    if re.match(bic_re, tok): //bic를 입력으로 받았을 때.. process_3_args 호출
        //생략
    if re.match(mvn_re, tok): //mvn를 입력으로 받았을 때.. process_mvn_args 호출
      	//생략
    if re.match(swi_re, tok): //swi를 입력으로 받았을 때.. process_1_args 호출 
	//생략
    if re.match(mul_re, tok): mul을 입력으로 받았을 때.. process_mul_args 호출
       //생략
### main() starts here ###
lines = sys.stdin.readlines()
splitter = re.compile(r'([ \t\n,])')
ip=0x8080 //임시 pc 출력코드.. b와 같은 것들 아직 미구현
data=[['0',0]]
for line in lines:
    tokens = splitter.split(line)
    tokens = [tok for tok in tokens
              if re.match('\s*$', tok) == None]
    mach_code = 0
    while len(tokens) > 0:
	//현재 위치 및 입력받은 코드 출력
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
            print(hex(mach_code) + ' : Machine Instruction\n')// hex 코드 출력
            print()
            #print (struct.pack('I', mach_code))
            break
