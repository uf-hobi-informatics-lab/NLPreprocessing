SYMBOLS = {',', '?', '!', ':', '\'', '"', '(', ')', ';', '@', '^', '^', '&', '&', '$', '$', '£',
           '[', ']', '{', '}', '<', '>', '+', '-', "*", "#", "%", "=", "~", '/', "_"}

PREP = {'about', 'above', 'across', 'after', 'against', 'aka', 'along', 'and', 'anti', 'apart', 'around', 'as',
         'astride', 'at', 'away', 'because', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond',
         'but', 'by', 'contra', 'down', 'due to', 'during', 'ex', 'except', 'excluding', 'following', 'for', 'from',
         'given', 'in', 'including', 'inside', 'into', 'like', 'near', 'nearby', 'neath', 'of', 'off', 'on', 'onto',
         'or', 'out', 'over', 'past', 'per', 'plus', 'since', 'so', 'than', 'though', 'through', 'til', 'to',
         'toward', 'towards', 'under', 'underneath', 'versus', 'via', 'where', 'while', 'with', 'within', 'without',
         'also'}

DET = {'a', 'an', 'the'}

NON_STOP_PUNCT = {',', ';'}

STOP_PUNCT = {'.', '?', '!'}

SENT_WORD = {'we', 'us', 'patient', 'denies', 'reveals', 'no', 'none', 'he', 'she', 'his', 'her', 'they', 'them', 'is',
             'was', 'who', 'when', 'where', 'which', 'are', 'be', 'have', 'had', 'has', 'this', 'will', 'that', 'the',
             'to', 'in', 'with', 'for', 'an', 'and', 'but', 'or', 'as', 'at', 'of', 'have', 'it', 'that', 'by', 'from',
             'on', 'include', 'other', 'another'}

UNIT = {'mg', 'lb', 'kg', 'mm', 'cm', 'm', 'doz', 'am', 'pm', 'mph', 'oz', 'ml', 'l', 'mb', 'mmHg', 'min', 'cm2', 'm2', 'M2',
        'mm2', 'mL', 'F', 'ppd', 'L', 'g', 'cc', "MG", "Munits", "pack", "mcg", "K", "hrs", "N", "inch", "d",
        "AM", "PM", "HS", "QAM", "QPM", "BID", "mEq", "hr", "cGy", "mGy", "mLs", "mOsm"}

MIMICIII_DEID_PATTERN = "\[\*\*|\*\*\]"

NAME_PREFIX_SUFFIX = {
    'Dr', 'Mr', 'Mrs', 'Jr', 'Ms', 'Prof'
}

PROFESSIONAL_TITLE = {
    'M.D.', 'Ph.D.', 'Pharm.D.'
}

SPECIAL_ABBV = {
    'B.I.D.', 'E.C.', 'p.o.', 'P.O.', 'b.i.d.', 'p.r.n.'
}

ROMAN_NUM = {
    'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'
}

WHITE_LIST = {
    'NaCl', 'KCl', 'HandiHaler', 'MetroCream', 'ChloraPrep', 'NovoLog', 'FlexPen', 'EpiPen', 'CellCept', 'iPad', 'eConsult', 'PreserVision'
}