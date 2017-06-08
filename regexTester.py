import re

strings = ['s',
           '1',
           '9400',
           '30225989',
           '2130225989',
           '02130225989',
           '2430225989',
           '02430225989',
           '1130225989',
           '01130225989',
           '1430225989',
           '01430225989',
           '3130225989',
           '03130225989',
           '995792617',
           '21995792617',
           '021995792617',
           '24995792617',
           '024995792617',
           '11995792617',
           '011995792617',
           '14995792617',
           '014995792617',
           '31995792617',
           '031995792617',
           '993171541',
           '08007752586',
           '40636449',
           '27925000',
           '39899311',
           '10325',
           '986292684',
           '0017818766295',
           '17818766295'
           ]

PATTERN_EXTENSION = r'^\d{4}$'
PATTERN_FIX = r'^\d{8}$'
PATTERN_FIX_RJ = r'^0?2?[0-8]\d{7,8}$'
PATTERN_FIX_SP = r'^0?1[0-8]\d{7,8}$'
PATTERN_FIX_OTHERS = r'^0?[^12(0800)]\d{9}$'
PATTERN_CELL = r'^\d{0,2}(9|8)\d{8}$'
PATTERN_CELL_RJ = r'^0?2?\d?(9|8)\d{8}$'
PATTERN_CELL_SP = r'^0?1\d?(9|8)\d{8}$'
PATTERN_CELL_OTHERS = r'^0?[^12]\d(9|8)\d{8}$'
PATTERN_0800 = r'^(0800)\d{0,7}$'
PATTERN_INTERNATIONAL = r'^(00)?17818766295$'
PATTERN_1DIGIT = r'^\d{1}$'
PATTERN_3DIGITS = r'^\d{3}$'
PATTERN_5DIGITS = r'^\d{5}$'

PATTERNS = {
    PATTERN_EXTENSION: 'EXTENSION',
    # PATTERN_FIX_DDD: 'FIXO DDD',
    PATTERN_FIX_RJ: 'FIXO RJ',
    PATTERN_FIX_SP: 'FIXO SP',
    PATTERN_FIX_OTHERS: 'FIXO DEMAIS REGIOES',
    # PATTERN_CELL: 'CELULAR',
    PATTERN_CELL_RJ: 'CELULAR RJ',
    PATTERN_CELL_SP: 'CELULAR SP',
    PATTERN_CELL_OTHERS: 'CELULAR DEMAIS REGIOES',
    PATTERN_0800: '0800',
    PATTERN_INTERNATIONAL: 'INTERNACIONAL',
    PATTERN_1DIGIT: 'Numero 1 Digito',
    PATTERN_3DIGITS: 'Numero 3 Dgitos ',
    PATTERN_5DIGITS: 'Numero 5 Digitos'
}

for s in strings:
    printed = False
    for pk, pv in PATTERNS.iteritems():
        if re.match(pk, s):
            print 'string: {0} matched: {1}'.format(s, pv)
            printed = True
    if printed is False:
        print 'No match for string: {0}'.format(s)