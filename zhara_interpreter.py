from zhara_lex import lex, tableToPrint
from zhara_lex import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, sourceCode, tableOfLanguageTokens
from zhara_translator import postfixTranslator, postfixCode, FSuccess, tableOfForHiddenId
from stack import Stack

stack = Stack()

toView = True

instrNum = 0


def postfixInterpreter():
    FSuccess = postfixTranslator()
    if (True, 'Translator') == FSuccess:
        return postfixProcessing()
    else:
        print('Interpreter: Translator завершив роботу аварійно')
        return False


commandTrack = []


def postfixProcessing():
    global stack, postfixCode, instrNum, commandTrack
    cyclesNumb = 0
    maxNumb = len(postfixCode)
    try:
        while instrNum < maxNumb and cyclesNumb < 100000:
            cyclesNumb += 1
            lex, tok = postfixCode[instrNum]
            commandTrack.append((instrNum, lex, tok))
            if tok in ('integer', 'real', 'id', 'bool', 'label'):
                stack.push((lex, tok))
                nextInstr = instrNum + 1
            elif tok in ('jump', 'jf', 'colon'):
                nextInstr = doJumps(tok)
            else:
                doIt(lex, tok)
                nextInstr = instrNum + 1
            instrNum = nextInstr
        return commandTrack
    except SystemExit as e:
        print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
    return True


def doJumps(tok):
    if tok == 'colon':
        next = processing_colon()
    elif tok == 'jf':
        next = processing_JF()

    elif tok == 'jump':
        next = processing_JUMP()
    return next


def processing_JUMP():
    global instrNum
    m = stack.pop()
    return tableOfLabel[m[0]]


def processing_JF():
    global instrNum
    m = stack.pop()
    bool_expr = stack.pop()
    if getBoolValue(bool_expr[0]):
        return instrNum + 1
    else:
        return tableOfLabel[m[0]]


def processing_colon():
    global instrNum
    m = stack.pop()
    return instrNum + 1


def configToPrint(step, lex, tok, maxN):
    if step == 1:
        print('=' * 30 + '\nInterpreter run\n')
        tableToPrint('All')

    print('\nКрок інтерпретації: {0}'.format(step))
    if tok in ('integer', 'real'):
        print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('id'):
        print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
    else:
        print('Лексема: {0}'.format((lex, tok)))

    print('postfixCode={0}'.format(postfixCode))
    stack.print()

    if step == maxN:
        for Tbl in ('Id', 'Const', 'Label'):
            tableToPrint(Tbl)
    return True


def checkId():
    global tableOfId
    for elem in tableOfId:
        if tableOfId[elem][1] == 'type_undef':
            failRunTime('неоголошена змінна', (elem, tableOfId[elem], None, None, (None, None)))


def doIt(lex, tok):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    checkId()
    if (lex, tok) == ('=', 'assign_op'):
        (lexL, tokL) = stack.pop()
        (lexR, tokR) = stack.pop()
        if (tokL, tableOfId[lexR][1]) == ('integer', 'real'):
            tableOfId[lexR] = (tableOfId[lexR][0], tableOfId[lexR][1], float(tableOfConst[lexL][2]))
        elif (tokL, tableOfId[lexR][1]) == ('real', 'integer'):
            failRunTime('невідповідність типів', ((lexL, tokL), lex, (lexR, tokR)))
        elif tableOfId[lexR][1] == 'bool' and tokL != 'bool':
            failRunTime('невідповідність типів', ((lexL, tokL), lex, (lexR, tokR)))
        else:
            tableOfId[lexR] = (tableOfId[lexR][0], tableOfId[lexR][1], tableOfConst[lexL][2])
    elif tok in ('add_op', 'mult_op', 'pow_op', 'rel_op', 'bool_op'):
        if lex == 'NEG':
            (lexR, tokR) = stack.pop()
            processing_NEG((lexR, tokR))
        elif lex == '!':
            (lexR, tokR) = stack.pop()
            processing_not((lexR, tokR))
        else:
            (lexR, tokR) = stack.pop()
            (lexL, tokL) = stack.pop()
            processing_add_mult_rel_bool_op((lexL, tokL), lex, (lexR, tokR))
    elif lex == 'print':
        (lexR, tokR) = stack.pop()
        processing_print((lexR, tokR))
    elif lex == 'scan':
        (lexR, tokR) = stack.pop()
        processing_scan((lexR, tokR))
    return True


def processing_print(lt):
    lexL, tokL = lt
    if tokL == 'id':
        if tableOfId[lexL][2] == 'val_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (None, None)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    print(valL)
    toTableOfConst(valL, tokL)


def processing_scan(lt):
    lexL, tokL = lt
    if tokL == 'id':
        valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        failRunTime('неочікуваний аргумент у scan', (lexL, tableOfId[lexL], (lexL, tokL), lex, (None, None)))
    if tokL == 'integer':
        f = int
    elif tokL == 'real':
        f = float
    else:
        f = getBoolValue
    try:
        input_val = input()
        valL = f(input_val)
        if tokL == 'bool':
            valL = str(valL).lower()
    except ValueError:
        failRunTime('невідповідність типів', ((lexL, tokL), 'та ', ('input_val', input_val)))
    tableOfId[lexL] = (tableOfId[lexL][0], tableOfId[lexL][1], valL)
    toTableOfConst(valL, tokL)


def processing_not(lt):
    lexL, tokL = lt
    if tokL == 'id':
        if tableOfId[lexL][2] == 'val_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (None, None)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    value = str(not getBoolValue(valL)).lower()
    stack.push((str(value), tokL))
    toTableOfConst(value, tokL)


def processing_NEG(lt):
    lexL, tokL = lt
    if tokL == 'id':
        if tableOfId[lexL][2] == 'val_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (None, None)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    value = -valL
    stack.push((str(value), tokL))
    toTableOfConst(value, tokL)


def processing_add_mult_rel_bool_op(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR
    if tokL == 'id':

        if tableOfId[lexL][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        elif tableOfId[lexL][2] == 'val_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    if tokR == 'id':

        if tableOfId[lexR][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
    else:
        valR = tableOfConst[lexR][2]
    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


def getValue(vtL, lex, vtR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR
    if lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '^':
        value = valL ** valR
    elif lex == '*':
        value = valL * valR
    elif lex == '/' and valR == 0:
        failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/' and tokL == 'integer' and tokR == 'integer':
        value = int(valL / valR)
    elif lex == '/':
        value = valL / valR
    elif lex == '>':
        value = str(valL > valR).lower()
    elif lex == '<':
        value = str(valL < valR).lower()
    elif lex == '>=':
        value = str(valL >= valR).lower()
    elif lex == '<=':
        value = str(valL <= valR).lower()
    elif lex == '==':
        value = str(valL == valR).lower()
    elif lex == '!=':
        value = str(valL != valR).lower()
    elif lex == '||':
        if (tokL, tokR) == ('bool', 'bool'):
            value = str(getBoolValue(valL) or getBoolValue(valR)).lower()
        else:
            failRunTime('невiдповiднiсть типiв', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '&&':
        if (tokL, tokR) == ('bool', 'bool'):
            value = str(getBoolValue(valL) and getBoolValue(valR)).lower()
        else:
            failRunTime('невiдповiднiсть типiв', ((lexL, tokL), lex, (lexR, tokR)))
    else:
        pass
    if tableOfLanguageTokens[lex] == 'rel_op':
        toTableOfConst(value, 'bool')
        stack.push((str(value), 'bool'))
    elif tokL == 'real' or tokR == 'real':
        toTableOfConst(value, 'real')
        stack.push((str(value), 'real'))
    else:
        toTableOfConst(value, tokL)
        stack.push((str(value), tokL))

    # tableOfId[lexR] = (tableOfId[lexR][0],  tableOfConst[lexL][1], tableOfConst[lexL][2])


def getBoolValue(str_bool):
    if str_bool == 'true':
        return True
    elif str_bool == 'false':
        return False
    else:
        raise ValueError


def toTableOfConst(val, tok):
    lexeme = str(val)
    indx1 = tableOfConst.get(lexeme)
    if indx1 is None:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (indx, tok, val)


def failRunTime(str, tuple):
    if str == 'невідповідність типів':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Типи операндів відрізняються у {0} {1} {2}'.format((lexL, tokL), lex, (lexR, tokR)))
        exit(1)
    elif str == 'неініціалізована змінна':
        (lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Значення змінної {0}:{1} не визначене. Зустрылось у {2} {3} {4}'.format(lx, rec,
                                                                                                           (lexL, tokL),
                                                                                                           lex, (
                                                                                                               lexR,
                                                                                                               tokR)))
        exit(2)
    elif str == 'ділення на нуль':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
        exit(3)
    elif str == 'неоголошена змінна':
        (lx, rec, _, lex, _) = tuple
        print('RunTime ERROR: \n\t Використання неоголошеної змінної {0}:{1}'.format(lx, rec))
        exit(4)

    elif str == 'неочікуваний аргумент у scan':
        (lx, rec, _, lex, _) = tuple
        print('RunTime ERROR: \n\t Використання неоголошеної змінної {0}:{1}'.format(lx, rec))
        exit(5)


postfixInterpreter()
