
tableOfLanguageTokens = {'entry': 'keyword', 'if': 'keyword', 'then': 'keyword', 'for': 'keyword',
                         'by': 'keyword', 'to': 'keyword', 'do': 'keyword', 'rof': 'keyword', 'scan': 'keyword',
                         'print': 'keyword', 'integer': 'keyword', 'real': 'keyword',
                         'boolean': 'keyword', 'true': 'bool',
                         'false': 'bool', '=': 'assign_op', '.': 'dot', ' ': 'ws', '\t': 'ws', '\n': 'nl',
                         '-': 'add_op', '+': 'add_op', ',': 'punct',
                         '*': 'mult_op', '/': 'mult_op', '^': 'pow_op', '(': 'par_op', ')': 'par_op',
                         '{': 'start_block', '}': 'end_block', ';': 'op_end', '<': 'rel_op', '>': 'rel_op',
                         '==': 'rel_op',
                         '<=': 'rel_op', '>=': 'rel_op', '!=': 'rel_op', '&&': 'bool_op',
                         '||': 'bool_op', '!': 'bool_op', }

tableIdentFloatInt = {2: 'id', 6: 'real', 9: 'integer'}

stf = {(0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
       (0, 'Digit'): 4, (4, 'Digit'): 4, (4, 'dot'): 5, (4, 'other'): 9, (5, 'Digit'): 5, (5, 'other'): 6,
       (0, 'Assign'): 7, (7, 'Assign'): 14, (7, 'other'): 12,
       (0, 'ws'): 0,
       (0, 'nl'): 13,
       (0, '+'): 14, (0, '^'): 14, (0, '*'): 14, (0, '/'): 14, (0, '('): 14, (0, ')'): 14,
       (0, '{'): 14, (0, '}'): 14, (0, ','): 14, (0, ';'): 14,
       (0, '-'): 40, (40, 'Digit'): 4, (40, 'other'): 12,
       (0, '<'): 7, (0, '>'): 7, (0, '!'): 7,
       (0, '&'): 8, (8, '&'): 14,
       (0, '|'): 16, (16, '|'): 14,
       (8, 'other'): 102,
       (16, 'other'): 103,
       (0, 'other'): 101
       }

initState = 0  # q0 - стартовий стан
F = {2, 6, 9, 12, 13, 14, 101, 102, 103}
Fstar = {2, 6, 9}  # зірочка
Ferror = {101, 102, 103}  # обробка помилок

tableOfId = {}  # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиць констант
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)
tableOfLabel={}

state = initState  # поточний стан

f = open('test.my_lang', 'r')
sourceCode = f.read()
f.close()

# FSuccess - ознака успішності розбору
FSuccess = (True, 'ZharaLexer')

lenCode = len(sourceCode) - 1  # номер останнього символа у файлі з кодом програми
numLine = 1  # лексичний аналіз починаємо з першого рядка
numChar = -1  # з першого символа (в Python'і нумерація - з 0)
char = ''  # ще не брали жодного символа
lexeme = ''  # ще не починали розпізнавати лексеми


def lex():
    global state, numLine, char, lexeme, numChar, FSuccess
    try:
        while numChar < lenCode:
            char = nextChar()  # прочитати наступний символ
            classCh = classOfChar(char)  # до якого класу належить
            state = nextState(state, classCh)  # обчислити наступний стан
            if is_final(state):  # якщо стан заключний
                processing()  # виконати семантичні процедури
            # if state in Ferror:	    # якщо це стан обробки помилки
            # break					#      то припинити подальшу обробку
            elif state == initState:
                lexeme = ''  # якщо стан НЕ заключний, а стартовий - нова лексема
            else:
                lexeme += char  # якщо стан НЕ закл. і не стартовий - додати символ до лексеми
        print('ZharaLexer: Лексичний аналіз завершено успішно')
        return FSuccess
    except SystemExit as e:
        # Встановити ознаку неуспішності
        FSuccess = (False, 'ZharaLexer')
        # Повідомити про факт виявлення помилки
        print('ZharaLexer: Аварійне завершення програми з кодом {0}'.format(e))


def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb
    if state == 13:  # \n
        numLine += 1
        state = initState
    if state in (2, 6, 9):  # keyword, ident, float, int
        token = getToken(state, lexeme)
        if token != 'keyword':
            index = indexIdConst(state, lexeme, token)
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:  # якщо keyword
            # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
    if state == 12:  # 12:
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
    if state == 14:  # 12:         # assign_op # in (12,14):
        lexeme += char
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
    if state in Ferror:
        fail()


def fail():
    global state, numLine, char
    if state == 101:
        print('ZharaLexer: у рядку ', numLine, ' неочікуваний символ \'' + char + '\'')
        exit(101)
    if state == 102:
        print('ZharaLexer: у рядку ', numLine, ' очікувався символ &&, а не &')
        exit(102)
    if state == 103:
        print('ZharaLexer: у рядку ', numLine, ' очікувався символ ||, а не |')
        exit(103)


def is_final(state):
    if (state in F):
        return True
    else:
        return False


def nextState(state, classCh):
    try:
        return stf[(state, classCh)]
    except KeyError:
        return stf[(state, 'other')]


def nextChar():
    global numChar
    numChar += 1
    return sourceCode[numChar]


def putCharBack(numChar):
    return numChar - 1


def classOfChar(char):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    letters = letters + letters.upper() + '_'
    if char in '.':
        res = "dot"
    elif char in letters:
        res = "Letter"
    elif char in "0123456789":
        res = "Digit"
    elif char in " \t":
        res = "ws"
    elif char in "\n":
        res = "nl"
    elif char in "=":
        res = "Assign"
    elif char in "+-*/(){}^&|<>,;!":
        res = char
    else:
        res = 'символ не належить алфавіту'
    return res


def getToken(state, lexeme):
    try:
        return tableOfLanguageTokens[lexeme]
    except KeyError:
        return tableIdentFloatInt[state]


def indexIdConst(state, lexeme, token):
    indx = 0
    if token == 'bool':
        indx1 = tableOfConst.get(lexeme)
        if indx1 is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = (indx, token, lexeme)
    elif state == 2:
        indx1 = tableOfId.get(lexeme)
        if indx1 is None:
            indx = len(tableOfId) + 1
            tableOfId[lexeme] = (indx, 'type_undef', 'val_undef')
    elif state in (6, 9):
        indx1 = tableOfConst.get(lexeme)
        if indx1 is None:
            indx = len(tableOfConst) + 1
            if state == 6:
                val = float(lexeme)
            elif state == 9:
                val = int(lexeme)
            tableOfConst[lexeme] = (indx, token, val)
    if not (indx1 is None):
        if len(indx1) == 2:
            indx, _ = indx1
        else:
            indx, _, _ = indx1
    return indx


def tableToPrint(Tbl):
    if Tbl == "Symb":
        tableOfSymbToPrint()
    elif Tbl == "Id":
        tableOfIdToPrint()
        pass
    elif Tbl == "Const":
        tableOfConstToPrint()
    elif Tbl == "Label":
        tableOfLabelToPrint()
    else:
        tableOfSymbToPrint()
        tableOfIdToPrint()
        tableOfConstToPrint()
        tableOfLabelToPrint()
    return True


def tableOfSymbToPrint():
    print("\n Таблиця символів")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
    s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
    print(s1.format("numRec", "numLine", "lexeme", "token", "index"))
    for numRec in tableOfSymb:  # range(1,lns+1):
        numLine, lexeme, token, index = tableOfSymb[numRec]
        print(s2.format(numRec, numLine, lexeme, token, str(index)))


def tableOfIdToPrint():
    print("\n Таблиця ідентифікаторів")
    s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
    print(s1.format("Ident", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10d} '
    for id in tableOfId:
        index, type, val = tableOfId[id]
        print(s2.format(id, index, type, str(val)))


def tableOfConstToPrint():
    print("\n Таблиця констант")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} '
    print(s1.format("Const", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<10s} {3:<10} {1:<10d} '
    for cnst in tableOfConst:
        index, type, val = tableOfConst[cnst]
        print(s2.format(str(cnst), index, type, val))


def tableOfLabelToPrint():
    if len(tableOfLabel) == 0:
        print("\n Таблиця міток - порожня")
    else:
        s1 = '{0:<10s} {1:<10s} '
        print("\n Таблиця міток")
        print(s1.format("Label", "Value"))
        s2 = '{0:<10s} {1:<10d} '
        for lbl in tableOfLabel:
            val = tableOfLabel[lbl]
            print(s2.format(lbl, val))


