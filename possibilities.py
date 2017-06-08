# Number patterns:
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

TRUNKS_UPDATED = {'DirectCall - RJ': 'T. DirectCall - RJ',
                  'DirectCall - SP': 'T. DirectCall - SP',
                  '22405157': 'T. Vivo - Fixo',
                  'Mobile': 'T. Claro - Mobile'
}

for tk, tv in TRUNKS_UPDATED.iteritems():
    for pk, pv in PATTERNS.iteritems():
        print '(\'{0}\', \'{1}\'): \'\','.format(pv, tv)

