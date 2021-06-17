from zhara_lex import lex, tableToPrint
from zhara_lex import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, sourceCode, FSuccess
import zhara_lex

# FSuccessTr = (False,'Translator')

lex()

postfixCode = []

numRow = 1

len_tableOfSymb = len(tableOfSymb)

toView = False

tableOfForHiddenId = {}


def postfixTranslator():
    if (True, 'ZharaLexer') == zhara_lex.FSuccess:
        return parseProgram()


def parseProgram():
    global FSuccess
    try:
        parseToken('entry', 'keyword', '')
        parseToken('{', 'start_block', '')
        parseStatementList()
        parseToken('}', 'end_block', '')
        print('ZharaTranslator: Переклад у ПОЛІЗ та синтаксичний аналіз завершились успішно')
        FSuccess = (True, 'Translator')
        return FSuccess
    except SystemExit as e:
        print('ZharaParser: Аварійне завершення програми з кодом {0}'.format(e))


def parseToken(lexeme, token, indent):
    global numRow
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))
    numLine, lex, tok = getSymb()

    numRow += 1

    if (lex, tok) == (lexeme, token):
        return True
    else:
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False


def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print(
            'ZharaParser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
            'номером {1}. \n\t Очікувалось - {0}'.format(
                (lexeme, token), numRow))
        exit(1001)
    if str == 'getSymb(): неочікуваний кінець програми':
        numRow = tuple
        print(
            'ZharaParser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
            'номером {0}. \n\t Останній запис - {1}'.format(
                numRow, tableOfSymb[numRow - 1]))
        exit(1002)
    elif str == 'переоголошення змінної':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t В рядку {0} переоголошення змінної ({1},{2}). \n\t'.format(numLine, lex, tok))
        exit(4)
    elif str == 'невідповідність токенів':
        (numLine, lexeme, token, lex, tok) = tuple
        print('ZharaParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
            numLine, lexeme, token, lex, tok))
        exit(1)
    elif str == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,
                                                                                                                lex,
                                                                                                                tok,
                                                                                                                expected))
        exit(2)
    elif str == 'невідповідність у Expression.Factor':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,
                                                                                                                lex,
                                                                                                                tok,
                                                                                                                expected))
        exit(3)

    elif str == 'невідповідність у Declaration':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,
                                                                                                                lex,
                                                                                                                tok,
                                                                                                                expected))
        exit(4)

    elif str == 'невідповідність у In':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,
                                                                                                                lex,
                                                                                                                tok,
                                                                                                                expected))
        exit(4)

    elif str == 'оголошення заброньованих слів':
        (numLine, lex, tok, expected) = tuple
        print(
            'ZharaParser ERROR: \n\t Оголошення заброньованого слова ({0},{1}).\n\t Будь ласка, '
            'не використовуйте це слово як ідентифікатор змінної у своїй програмі\n'.format(lex, tok))
        exit(99)


def parseStatementList():
    while parseStatement():
        pass
    return True


def parseStatement():
    numLine, lex, tok = getSymb()

    if tok == 'id':
        parseAssign()
        parseToken(';', 'op_end', '')
        return True

    elif lex in ('integer', 'real', 'boolean'):
        parseDeclaration()
        parseToken(';', 'op_end', '')
        return True

    elif (lex, tok) == ('for', 'keyword'):
        parseFor()
        return True

    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
        return True

    elif (lex, tok) == ('print', 'keyword'):
        parseOut()
        parseToken(';', 'op_end', '')
        return True

    elif (lex, tok) == ('scan', 'keyword'):
        parseIn()
        parseToken(';', 'op_end', '')
        return True


    elif (lex, tok) == ('}', 'end_block'):
        return False

    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'id, type, if або for'))
        return False


def parseAssign(is_in_for=False):
    global numRow
    numLine, lex, tok = getSymb()
    postfixCode.append((lex, tok))
    numRow += 1
    if parseToken('=', 'assign_op', ''):
        if is_in_for:
            parseExpression()
        else:
            if tableOfId[lex][1] == 'bool':
                parseBoolExpression()
            else:
                parseExpression()
        postfixCode.append(('=', 'assign_op'))
        return True
    else:
        return False


def parseDeclaration():
    global numRow
    numLine, lex, tok = getSymb()
    numRow += 1
    id_type = None
    if lex == 'integer':
        id_type = 'integer'
    elif lex == 'real':
        id_type = 'real'
    elif lex == 'boolean':
        id_type = 'bool'
    parseIdentList(id_type)
    return True


def parseIdentList(idtype):
    global numRow
    while True:
        numLine, lex, tok = getSymb()
        numRow += 1
        if tok == "id":
            temp = tableOfId.get(lex)
            if temp[1] != 'type_undef':
                failParse('переоголошення змінної', (numLine, lex, tok, 'id'))
            tableOfId[lex] = (tableOfId[lex][0], idtype, tableOfId[lex][2])
            numLine, lex, tok = getSymb()
            if (lex, tok) == (',', 'punct'):
                parseToken(lex, tok, '')
            elif (lex, tok) == (';', 'op_end'):
                return True
            else:
                failParse('невідповідність у Declaration', (numLine, lex, tok, ', або ;'))

        else:
            failParse('невідповідність у Declaration', (numLine, lex, tok, 'id'))


def parseIn():
    global numRow
    parseToken('scan', 'keyword', '')
    parseToken('(', 'par_op', '')
    numLine, lex, tok = getSymb()
    numRow += 1
    if tok == "id":
        postfixCode.append((lex, tok))
    else:
        failParse('невідповідність у In', (numLine, lex, tok, 'id'))
    parseToken(')', 'par_op', '')
    postfixCode.append(('scan', 'keyword'))
    return True


def parseOut():
    parseToken('print', 'keyword', '')
    parseToken('(', 'par_op', '')

    while True:
        parseExpression()
        numLine, lex, tok = getSymb()
        if lex == ')':
            break
        postfixCode.append(('print', 'keyword'))
        parseToken(lex, tok, '')
    parseToken(')', 'par_op', '')
    postfixCode.append(('print', 'keyword'))
    return True


def parseFor():
    global numRow
    parseToken('for', 'keyword', '')
    numLine, lex, tok = getSymb()
    parseAssign(is_in_for=True)
    for_id_type = 'real'
    if tok == 'id':
        for_id_type = tableOfId[lex][1]
    if tableOfConst.get('1') is None:
        tableOfConst['1'] = (len(tableOfConst)+1, 'integer', 1)
    if tableOfConst.get('0') is None:
        tableOfConst['0'] = (len(tableOfConst)+1, 'integer', 0)
    r1, r2 = generateForHiddenVar(for_id_type)
    parseToken('by', 'keyword', '')
    postfixCode.append(r1)
    postfixCode.append(('1', 'integer'))
    postfixCode.append(('=', 'assign_op'))
    m1 = createLabel()
    m2 = createLabel()
    m3 = createLabel()

    setValLabel(m1)
    postfixCode.append(m1)

    postfixCode.append((':', 'colon'))
    postfixCode.append(r2)
    parseExpression()
    parseToken('to', 'keyword', '')
    postfixCode.append(('=', 'assign_op'))
    postfixCode.append(r1)
    postfixCode.append(('0', 'integer'))
    postfixCode.append(('==', 'rel_op'))
    postfixCode.append(m2)
    postfixCode.append(('JF', 'jf'))
    postfixCode.append((lex, tok))
    postfixCode.append((lex, tok))
    postfixCode.append(r2)
    postfixCode.append(('+', 'add_op'))
    postfixCode.append(('=', 'assign_op'))

    setValLabel(m2)
    postfixCode.append(m2)

    postfixCode.append((':', 'colon'))
    postfixCode.append(r1)
    postfixCode.append(('0', 'integer'))
    postfixCode.append(('=', 'assign_op'))
    postfixCode.append((lex, tok))

    parseExpression()
    parseToken('do', 'keyword', '')

    postfixCode.append(('-', 'add_op'))
    postfixCode.append(r2)
    postfixCode.append(('*', 'mult_op'))
    postfixCode.append(('0', 'integer'))
    postfixCode.append(('<', 'rel_op'))

    postfixCode.append(m3)
    postfixCode.append(('JF', 'jf'))

    while True:
        numLine, lex, tok = getSymb()
        if lex == 'rof':
            break
        else:
            parseStatement()

    parseToken(lex, tok, '')

    postfixCode.append(m1)
    postfixCode.append(('JUMP', 'jump'))

    setValLabel(m3)
    postfixCode.append(m3)
    postfixCode.append((':', 'colon'))
    return True


def generateForHiddenVar(value_type):
    global tableOfForHiddenId
    n = len(tableOfForHiddenId)
    id_n = len(tableOfId) + 1
    r1 = 'isForFirstStepId' + str(n)
    r2 = 'forStepExpressionValue' + str(n)
    if tableOfId.get(r1) is None:
        tableOfId[r1] = (id_n, 'integer', 1)
    else:
        failParse('оголошення заброньованих слів', (1, r1, 'id', 'id'))
    if tableOfId.get(r2) is None:
        tableOfId[r2] = (id_n + 1, value_type, 'val_undef')
    else:
        failParse('оголошення заброньованих слів', (1, r2, 'id', 'id'))
    tableOfForHiddenId[n] = (r1, r2)
    return (r1, 'id'), (r2, 'id')

def parseIf():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'if' and tok == 'keyword':
        numRow += 1
        parseBoolExpression()
        parseToken('then', 'keyword', '')
        m1 = createLabel()
        postfixCode.append(m1)
        postfixCode.append(('JF', 'jf'))
        parseStatement()
        setValLabel(m1)
        postfixCode.append(m1)
        postfixCode.append((':', 'colon'))

        return True
    else:
        return False


def setValLabel(lbl):
    global tableOfLabel
    lex, _tok = lbl
    tableOfLabel[lex] = len(postfixCode)
    return True


def createLabel():
    global tableOfLabel
    nmb = len(tableOfLabel) + 1
    lexeme = "m" + str(nmb)
    val = tableOfLabel.get(lexeme)
    if val is None:
        tableOfLabel[lexeme] = 'val_undef'
        tok = 'label'
    else:
        tok = 'Конфлiкт мiток'
        print(tok)
        exit(1003)
    return lexeme, tok


def parseRelExpr():
    global numRow
    parseExpression()
    numLine, lex, tok = getSymb()
    numRow += 1
    parseExpression()
    if tok in ('rel_op'):
        postfixCode.append((lex, tok))
    else:
        failParse('mismatch in BoolExpr', (numLine, lex, tok, 'rel_op'))

    return True


def configToPrint(lex, numRow):
    stage = '\nКрок трансляції\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'tableOfSymb[{1}] = {2}\n'
    stage += 'postfixCode = {3}\n'
    print(stage.format(lex, numRow, str(tableOfSymb[numRow]), str(postfixCode)))


def parseBoolExpression():
    global numRow, postfixCode
    _numLine, lex, tok = getSymb()
    if lex in ('!'):
        parseToken(lex, tok, '')
        parseBoolTerm()
        postfixCode.append((lex, tok))
    else:
        parseBoolTerm()
    F = True
    while F:
        _numLine, lex, tok = getSymb()
        if lex in ('||'):
            numRow += 1
            parseBoolTerm()
            postfixCode.append((lex, tok))
        else:
            F = False
    return True


def parseBoolTerm():
    global numRow, postfixCode
    parseBoolFactor()
    F = True
    while F:
        _numLine, lex, tok = getSymb()
        if lex in ('&&'):
            numRow += 1
            parseBoolFactor()
            postfixCode.append((lex, tok))
        else:
            F = False
    return True


def parseBoolFactor():
    global numRow, postfixCode
    numLine, lex, tok = getSymb()
    if lex == 'true' or lex == 'false' or (tok == 'id' and tableOfId[lex][1] == 'bool'):
        numRow += 1
        postfixCode.append((lex, tok))
    elif lex == '(':
        numRow += 1
        parseBoolExpression()
        parseToken(')', 'par_op', '\t' * 7)
    else:
        parseRelExpr()
    return True


def parseExpression():
    global numRow, postfixCode
    _numLine, lex, tok = getSymb()
    if tok in ('add_op'):
        parseToken(lex, tok, '')
        parseTerm()
        postfixCode.append(('NEG', tok))
    else:
        parseTerm()
    F = True
    while F:
        _numLine, lex, tok = getSymb()
        if tok in ('add_op'):
            numRow += 1
            parseTerm()
            postfixCode.append((lex, tok))
        else:
            F = False
    return True


def parseTerm():
    global numRow, postfixCode
    parseFactor()

    F = True

    while F:
        _numLine, lex, tok = getSymb()
        if tok == 'mult_op':
            numRow += 1
            parseFactor()
            postfixCode.append((lex, tok))
        elif tok == 'pow_op':
            numRow += 1
            parseTerm()
            postfixCode.append((lex, tok))
        else:
            F = False
    return True


def parseFactor():
    global numRow, postfixCode
    numLine, lex, tok = getSymb()
    if tok in ('integer', 'real', 'id'):
        postfixCode.append((lex, tok))
        if toView: configToPrint(lex, numRow)

        numRow += 1
    elif lex == '(':
        numRow += 1
        parseExpression()
        parseToken(')', 'par_op', '\t' * 7)
    else:
        failParse('невідповідність у Expression.Factor',
                  (numLine, lex, tok, 'rel_op, int, float, ident або \'(\' Expression \')\''))
    return True
