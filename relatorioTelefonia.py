#!/usr/bin/env python

from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
# from bs4 import BeautifulSoup
# from requests_file import FileAdapter
import matplotlib.pyplot as plt
import pandas as pd
import math as m
# import requests
# import sys
import re

# Constants:
NUM_ARGUMENTS = 2
NUM_ARG_INVALID = 1
MIN_PHONE_NUMBER = 8
MAX_PHONE_NUMBER = 14
MINUTE = 60.0
HTTP_OK = 200
URL = 'http://www.qualoperadora.net'
ERROR_STRING = 'Erro'
FIX_STRING = 'Fixo'
CELL_STRING = 'Celular'
PLOT_STYLE = 'ggplot'
FONT_SIZE = 14
FIGURE_SIZE = (20, 8)
Y_LIM = {
    'day_plot': (0, 601),
    'trunk_plot': (0, 2001),
    'route_plot': (0, 3001),
    'destination_plot': (0, 3001),
    'cost_plot': (0, 201)
}
FIGURE_NUMBER = {0: 'Minutos por dia',
                 1: 'Minutos por tronco',
                 2: 'Minutos por rota',
                 3: 'Minutos por destino',
                 4: 'Custos por rota'
                 }

# Paths, Files and Locations:

# Paths:
DATA_PATH = './csv/'
DB_PATH = './csv/bd/'
COST_PATH = './csv/cost/'
HTML_PATH = '/home/helpdesk/Downloads/telefonia/html/'
REPORTS_PATH = './reports/'

# CSV:
DATA_FILE = {0: 'cdr__1495652338voip.prilltc.csv',  # Jan
             1: 'cdr__1495652351voip.prilltc.csv',  # Feb
             2: 'cdr__1495636532voip.prilltc.csv',  # Mar
             3: 'cdr__1495636628voip.prilltc.csv',  # Apr
             4: '',  # May
             5: '',  # Jun
             6: '',  # Jul
             7: '',  # Aug
             8: '',  # Sep
             9: '',  # Oct
             10: '',  # Nov
             11: 'cdr__1495652367voip.prilltc.csv'}  # Dec
DB_FILE = 'bd.csv'
CLARO_COST_FILE = 'claro-cost/tabela_de_preco_Claro.csv'
VIVO_COST_FILE = 'vivo-cost/tabela_de_preco_Vivo.csv'
DIRECTCALL_COST_FILE = 'directcall-cost/tabela_de_preco_Directcall.csv'
DIRECTCALL_CITIES_FILE = 'directcall-cities/cidades_Directcall.csv'

# HTML:
# HTML_FILE = 'bloqueio.html'
# HTML_FILE = 'resultado_fixo.html'
# HTML_FILE = 'resultado_celular.html'
HTML_PARSER = 'html5lib'
HTML_DATA_ID = 'telefone'

# File locations:
FILE_LOCATION = {0: DATA_PATH + DATA_FILE[0],
                 1: DATA_PATH + DATA_FILE[1],
                 2: DATA_PATH + DATA_FILE[2],
                 3: DATA_PATH + DATA_FILE[3],
                 4: DATA_PATH + DATA_FILE[4],
                 5: DATA_PATH + DATA_FILE[5],
                 6: DATA_PATH + DATA_FILE[6],
                 7: DATA_PATH + DATA_FILE[7],
                 8: DATA_PATH + DATA_FILE[8],
                 9: DATA_PATH + DATA_FILE[9],
                 10: DATA_PATH + DATA_FILE[10],
                 11: DATA_PATH + DATA_FILE[11]}
DB_LOCATION = DB_PATH + DB_FILE
CLARO_COST_LOCATION = COST_PATH + CLARO_COST_FILE
VIVO_COST_LOCATION = COST_PATH + VIVO_COST_FILE
DIRECTCALL_COST_LOCATION = COST_PATH + DIRECTCALL_COST_FILE
DIRECTCALL_CITIES_LOCATION = DATA_PATH + DIRECTCALL_CITIES_FILE
# HTML_LOCATION = 'file://' + HTML_PATH + HTML_FILE

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
CALL_POSSIBILITIES = {
    ('CELULAR DEMAIS REGIOES',  'T. Claro - Mobile', 'Cell DDD'):       'Mobile -> Celular Demais Regioes',
    ('CELULAR RJ',              'T. Claro - Mobile', 'Cell Local'):     'Mobile -> Celular RJ',
    ('CELULAR SP',              'T. Claro - Mobile', 'Cell DDD'):       'Mobile -> Celular SP',
    ('FIXO DEMAIS REGIOES',     'T. Claro - Mobile', 'Fixo DDD'):       'Mobile -> Fixo Demais Regioes',
    ('FIXO RJ',                 'T. Claro - Mobile', 'Fixo Local'):     'Mobile -> Fixo RJ',
    ('FIXO SP',                 'T. Claro - Mobile', 'Fixo DDD'):       'Mobile -> Fixo SP',
    ('NUMERO 1 DIGITO',         'T. Claro - Mobile', 'Gratis'):         'Mobile -> 1 Digito',
    ('NUMERO 2 DIGITOS',        'T. Claro - Mobile', 'Gratis'):         'Mobile -> 2 Digitos',
    ('NUMERO 3 DIGITOS',        'T. Claro - Mobile', 'Gratis'):         'Mobile -> 3 Digitos',
    ('NUMERO 5 DIGITOS',        'T. Claro - Mobile', 'Fixo Local'):     'Mobile -> 5 Digitos',
    ('0800',                    'T. Claro - Mobile', 'Gratis'):         'Mobile -> 0800',

    ('CELULAR DEMAIS REGIOES',  'T. Vivo - Fixo', 'Cell DDD'):          'Vivo -> Celular Demais Regioes',
    ('CELULAR RJ',              'T. Vivo - Fixo', 'Cell Local'):        'Vivo -> Celular RJ',
    ('CELULAR SP',              'T. Vivo - Fixo', 'Cell DDD'):          'Vivo -> Celular SP',
    ('FIXO DEMAIS REGIOES',     'T. Vivo - Fixo', 'Fixo DDD'):          'Vivo -> Fixo Demais Regioes',
    ('FIXO RJ',                 'T. Vivo - Fixo', 'Fixo Local'):        'Vivo -> Fixo RJ',
    ('FIXO SP',                 'T. Vivo - Fixo', 'Fixo DDD'):          'Vivo -> Fixo SP',
    ('NUMERO 1 DIGITO',         'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 1 Digito',
    ('NUMERO 2 DIGITOS',        'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 2 Digitos',
    ('NUMERO 3 DIGITOS',        'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 3 Digitos',
    ('NUMERO 5 DIGITOS',        'T. Vivo - Fixo', 'Fixo Local'):        'Vivo -> 5 Digitos',
    ('0800',                    'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 0800',

    ('CELULAR DEMAIS REGIOES',  'T. DirectCall - SP', 'Cell DDD'):      'DirectCall SP -> Celular Demais Regioes',
    ('CELULAR RJ',              'T. DirectCall - SP', 'Cell DDD'):      'DirectCall SP -> Celular RJ',
    ('CELULAR SP',              'T. DirectCall - SP', 'Cell Local'):    'DirectCall SP -> Celular SP',
    ('FIXO DEMAIS REGIOES',     'T. DirectCall - SP', 'Fixo DDD'):      'DirectCall SP -> Fixo Demais Regioes',
    ('FIXO RJ',                 'T. DirectCall - SP', 'Fixo DDD'):      'DirectCall SP -> Fixo RJ',
    ('FIXO SP',                 'T. DirectCall - SP', 'Fixo Local'):    'DirectCall SP -> Fixo SP',
    ('NUMERO 1 DIGITO',         'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 1 Digito',
    ('NUMERO 2 DIGITOS',        'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 2 Digitos',
    ('NUMERO 3 DIGITOS',        'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 3 Digitos',
    ('NUMERO 5 DIGITOS',        'T. DirectCall - SP', 'Fixo Local'):    'DirectCall SP -> 5 Digitos',
    ('0800',                    'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 0800',

    ('CELULAR DEMAIS REGIOES',  'T. DirectCall - RJ', 'Cell DDD'):      'DirectCall RJ -> Celular Demais Regioes',
    ('CELULAR RJ',              'T. DirectCall - RJ', 'Cell Local'):    'DirectCall RJ -> Celular RJ',
    ('CELULAR SP',              'T. DirectCall - RJ', 'Cell DDD'):      'DirectCall RJ -> Celular SP',
    ('FIXO DEMAIS REGIOES',     'T. DirectCall - RJ', 'Fixo DDD'):      'DirectCall RJ -> Fixo Demais Regioes',
    ('FIXO RJ',                 'T. DirectCall - RJ', 'Fixo Local'):    'DirectCall RJ -> Fixo RJ',
    ('FIXO SP',                 'T. DirectCall - RJ', 'Fixo DDD'):      'DirectCall RJ -> Fixo SP',
    ('NUMERO 1 DIGITO',         'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 1 Digito',
    ('NUMERO 2 DIGITOS',        'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 2 Digitos',
    ('NUMERO 3 DIGITOS',        'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 3 Digitos',
    ('NUMERO 5 DIGITOS',        'T. DirectCall - RJ', 'Fixo Local'):    'DirectCall RJ -> 5 Digitos',
    ('0800',                    'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 0800',
}


# Colors:
BI_COLOR = ['#4286F4', '#6BC924']
QUAD_COLOR = ['#E031C9', '#4286F4', '#ED6E34', '#6BC924']

# Trunks:
TRUNKS_UPDATED = {'DirectCall - RJ': 'T. DirectCall - RJ',
                  'DirectCall - SP': 'T. DirectCall - SP',
                  '22405157': 'T. Vivo - Fixo',
                  'Mobile': 'T. Claro - Mobile',
                  }
TRUNKS_OUTDATED = {'DirectCall': 'T. DirectCall - RJ',
                   '22405157': 'T. Vivo - Fixo',
                   'Mobile': 'T. Claro - Mobile'
                   }
# Extensions:
EXTENSIONS = {'100': '100',
              '8000': 'Porteiro',
              '8300': 'Empresa SP',
              '8301': 'Ramal SP',
              # Personnel Extensions - SP:
              '8701': 'David Ferreira',
              '8702': 'Gustavo Rey',
              '8703': 'Daniele Gomes',
              '9000': 'Empresa RJ',
              # Meeting Room:
              '9002': 'Sala de Reuniao',
              # Commercial:
              '9100': 'A. Comercial',
              '9101': 'Com. - Eduardo',
              '9102': 'Com. - Demetrius',
              # Support:
              '9200': 'A Suporte',
              '9205': 'A. Suporte T1',
              # Technical Area:
              '9300': 'A. Tecnica',
              '9301': '9301',
              '9302': 'A. Tecnica - B. 4',
              '9303': 'A. Tecnica - B. 2 T1',
              '9304': 'A. Tecnica - B. 2 T2',
              '9305': 'A. Tecnica - B. 3',
              '9306': 'A. Tecnica - Mesa 2',
              '9307': 'A. Tecnica - Mesa 1',
              '9308': 'Tel. teste nuvem',
              # Administrative Area:
              '9400': 'A. Adm',
              '9401': 'A. Adm. - T1',
              '9402': 'A. Adm. - T2',
              '9403': 'A. Adm. - T3',
              # Personnel Extensions - RJ:
              '9701': 'Alexandre Paes',
              '9702': 'Piettro Torres',
              '9703': 'Claudia Costa',
              '9704': 'Gustavo Fournier',
              '9705': 'Marcio Peres',
              '9706': 'Luiz Mariath',
              '9707': 'Gabriel Oliveira',
              '9708': 'Erick Nery',
              '9709': 'Pedro Rodrigues',
              '9710': 'Antonio Junior',
              '9711': 'David Ferreira',
              '9712': 'Demetrius Medrado',
              '9713': 'Eduardo Prillwitz',
              '9714': 'Tutmes Tsuda',
              '9715': 'Iwyson Thuller',
              '9716': 'Leonardo Pacheco',
              '9717': 'Lucas Antunes',
              '9718': 'Julia Costa',
              '9719': 'Rafael Vieira',
              '9720': 'Rodrigo Rocco',
              '9721': 'Vanderson Santos',
              '9722': 'Victor Cavalcante',
              '9723': '9723',
              '9724': 'Jessica Castro',
              '9725': 'Lucimar Ranna',
              '9726': 'Vania Pereira',
              '9727': 'Felipe Gomes',
              '9728': 'Raphael Santos',
              '9729': 'Diego Rocha',
              '9730': 'Tatiana Nassi',
              '9731': 'Washington Pereira',
              '9732': 'Luiz Valmont',
              '9733': 'Elizabeth Carvalho',
              '9734': 'Andre Costa',
              '9735': '9735',
              '9736': 'Adauto Serpa',
              # Conference Room:
              '9801': 'Sala de Conf. 1',
              '9802': 'Sala de Conf. 2'}

# class ReturnCodes:
#     OK, NUM_ARG_INVALID = range(2)


# Formatter:

# Parsers:
# parser = lambda datetime: dateutil.parser.parse(datetime).date()
# parserString = lambda string: datetime.datetime.strptime(string, '%Y-%m-%d').strftime('%d/%m/%y')

# Date Formatter DD/MM/YYYY:
def date_formatter(data_frame):
    output_name = ''
    for i in range(0, len(data_frame)):
        date_time = datetime.strptime(data_frame['calldate'][i], '%Y-%m-%d %H:%M:%S')
        if i == 0:
            month = date_time.strftime('%B')
            month_num = date_time.strftime('%m')
            year = date_time.strftime('%Y')
            output_name = '{0}-({1})-{2}.pdf'.format(year, month_num, month)
        if date_time.strftime('%w') is '0' or date_time.strftime('%w') is '6':
            date_string = date_time.strftime('%d/%m/%Y - %a')
        else:
            date_string = date_time.strftime('%d/%m/%Y')
        data_frame.set_value(i, 'calldate', date_string)
    return output_name


# Set call type:
def set_call_type(phone_type, trunk_type, data_frame, df_line, df_claro_cost, df_directcall_cost, df_vivo_cost):
    for cpk, cpv in CALL_POSSIBILITIES.iteritems():
        if (phone_type in cpk) and (trunk_type in cpk):
            data_frame.set_value(df_line, 'callType', cpv)
            if re.match('T. Claro - Mobile', cpk[1]):
                cost = df_claro_cost['plano-1'][cpk[2]] * data_frame['billsecInMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost)
                data_frame.set_value(df_line, 'callCost2', cost)
                data_frame.set_value(df_line, 'callCost3', cost)

            elif re.match('T. Vivo - Fixo', cpk[1]):
                cost = df_vivo_cost['plano-1'][cpk[2]] * data_frame['billsecInMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost)
                data_frame.set_value(df_line, 'callCost2', cost)
                data_frame.set_value(df_line, 'callCost3', cost)

            elif re.match('T. DirectCall - SP', cpk[1]):
                cost1 = df_directcall_cost['plano-1'][cpk[2]] * data_frame['billsecInMinutes'][df_line]
                cost2 = df_directcall_cost['plano-2'][cpk[2]] * data_frame['billsecInMinutes'][df_line]
                cost3 = df_directcall_cost['plano-3'][cpk[2]] * data_frame['billsecInMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost1)
                data_frame.set_value(df_line, 'callCost2', cost2)
                data_frame.set_value(df_line, 'callCost3', cost3)

            elif re.match('T. DirectCall - RJ', cpk[1]):
                cost1 = df_directcall_cost['plano-1'][cpk[2]] * data_frame['billsecInMinutes'][df_line]
                cost2 = df_directcall_cost['plano-2'][cpk[2]] * data_frame['billsecInMinutes'][df_line]
                cost3 = df_directcall_cost['plano-3'][cpk[2]] * data_frame['billsecInMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost1)
                data_frame.set_value(df_line, 'callCost2', cost2)
                data_frame.set_value(df_line, 'callCost3', cost3)
            break
    return


# Dst Formatter:
def destination_formatter(data_frame, df_claro_cost, df_directcall_cost, df_vivo_cost):
    # save_db = False  # flag to control data base save
    for df_line in range(0, len(data_frame)):  # read all lines from data frame
        phone = str(data_frame['dst'][df_line])  # get all phone numbers from column 'dst' line by line
        # for k, v in EXTENSIONS.iteritems():  # search if the phone number is an internal extension
        #     if k.find(phone) >= 0:
        #         data_frame.set_value(df_line, 'dst', v)
        #         data_frame.set_value(df_line, 'callType', 'Interna')
        #         break
        # else:
        for pk, pv in PATTERNS.iteritems():
            if re.match(pk, phone):
                data_frame.set_value(df_line, 'dst', pv)
                set_call_type(pv, 
                              data_frame['dstchannel'][df_line], 
                              data_frame, 
                              df_line, 
                              df_claro_cost, 
                              df_directcall_cost, 
                              df_vivo_cost)
                break
        else:
            data_frame.set_value(df_line, 'callType', phone)

        # else:
        #     for

        # else:
        #     for bd_line in range(0, len(data_base)):  # search if the phone number is already in our data base
        #         if str(data_base['phone'][bd_line]).find(phone) >= 0:
        #             data_frame.set_value(df_line, 'callType', 'External')
        #             data_frame.set_value(df_line, 'dst', data_base['fphone'][bd_line])
        #             data_frame.set_value(df_line, 'city', data_base['city'][bd_line])
        #             data_frame.set_value(df_line, 'state', data_base['state'][bd_line])
        #             data_frame.set_value(df_line, 'device', data_base['device'][bd_line])
        #             data_frame.set_value(df_line, 'operator', data_base['operator'][bd_line])
        #             break
        #     else:
        #         if MIN_PHONE_NUMBER <= len(phone) <= MAX_PHONE_NUMBER:
        #             WEB:  # web search for the phone number info
        #             Session/Request
        #             session = requests.Session()
        #             session.mount('file://', FileAdapter())
        #             Send Data
        #             web_data = {HTML_DATA_ID: phone}
        #             response = requests.post(URL, web_data)
        #             response = session.get(HTML_LOCATION)
        #             check status code, if OK then continue
        #             if response.status_code == HTTP_OK:
        #                 soup = BeautifulSoup(response.text, HTML_PARSER)
        #                 title = soup.title.string
        #                 # Possible titles:
        #                 # Erro 1407 - Consulta Bloqueada! - 21995792617
        #                 # Resultado: (11) 3285-9020 * Operadora: CTBC - Fixo - Sao Paulo - SP
        #                 # Resultado: (21) 99579-2617 - Operadora: Vivo - Celular - Rio de Janeiro
        #                 if title.find(ERROR_STRING) >= 0:
        #                     # Web Request Error (W.R.E.)
        #                     print 'Nao foi possivel acessar o site.'
        #                     data_frame.set_value(df_line, 'city', 'W.R.E.')
        #                     data_frame.set_value(df_line, 'state', 'W.R.E.')
        #                     data_frame.set_value(df_line, 'device', 'W.R.E.')
        #                     data_frame.set_value(df_line, 'operator', 'W.R.E.')
        #
        #                 elif title.find(FIX_STRING) >= 0:
        #                     # Web returned Fix phone
        #                     title_index_1 = title.find('(')
        #                     title_index_2 = title.find(' * ')
        #                     title_index_3 = title.find(':', title_index_2)
        #                     title_index_4 = title.find(' - ', title_index_3 + 1)
        #                     title_index_5 = title.find(' - ', title_index_4 + 1)
        #                     title_index_6 = title.find(' - ', title_index_5 + 1)
        #                     # Get information from web title answer
        #                     fphone = title[title_index_1: title_index_2]
        #                     operator = title[title_index_3 + 2: title_index_4]
        #                     device = title[title_index_4 + 3: title_index_5]
        #                     city = title[title_index_5 + 3: title_index_6]
        #                     state = title[title_index_6 + 3:]
        #                     # Update Data Frame
        #                     data_frame.set_value(df_line, 'callType', 'External')
        #                     data_frame.set_value(df_line, 'dst', fphone)
        #                     data_frame.set_value(df_line, 'city', city)
        #                     data_frame.set_value(df_line, 'state', state)
        #                     data_frame.set_value(df_line, 'device', device)
        #                     data_frame.set_value(df_line, 'operator', operator)
        #                     # Update Data Base
        #                     df_db.set_value(df_line, 'phone', phone)
        #                     df_db.set_value(df_line, 'fphone', fphone)
        #                     df_db.set_value(df_line, 'city', city)
        #                     df_db.set_value(df_line, 'state', state)
        #                     df_db.set_value(df_line, 'device', device)
        #                     df_db.set_value(df_line, 'operator', operator)
        #                     save_db = True
        #
        #                 elif title.find(CELL_STRING) >= 0:
        #                     # Web returned Cell phone
        #                     title_index_1 = title.find('(')
        #                     title_index_2 = title.find(' - ')
        #                     title_index_3 = title.find(':', title_index_2)
        #                     title_index_4 = title.find(' - ', title_index_3 + 1)
        #                     title_index_5 = title.find(' - ', title_index_4 + 1)
        #                     # Get information from web title answer
        #                     fphone = title[title_index_1: title_index_2]
        #                     operator = title[title_index_3 + 2: title_index_4]
        #                     device = title[title_index_4 + 3: title_index_5]
        #                     state = title[title_index_5 + 3:]
        #                     # Update Data Frame
        #                     data_frame.set_value(df_line, 'callType', 'External')
        #                     data_frame.set_value(df_line, 'dst', fphone)
        #                     data_frame.set_value(df_line, 'city', city)
        #                     data_frame.set_value(df_line, 'state', state)
        #                     data_frame.set_value(df_line, 'device', device)
        #                     data_frame.set_value(df_line, 'operator', operator)
        #                     # Update Data Base
        #                     df_db.set_value(df_line, 'phone', phone)
        #                     df_db.set_value(df_line, 'fphone', fphone)
        #                     df_db.set_value(df_line, 'city', city)
        #                     df_db.set_value(df_line, 'state', state)
        #                     df_db.set_value(df_line, 'device', device)
        #                     df_db.set_value(df_line, 'operator', operator)
        #                     save_db = True
        #                 else:
        #                     print response.status_code

    return  # save_db


# Trunk Formatter:
def trunk_formatter(data_frame):
    for df_line in range(0, len(data_frame)):
        trunk_value = str(data_frame['dstchannel'][df_line])
        for k, v in TRUNKS_UPDATED.iteritems():
            if trunk_value.find(k) >= 0:
                data_frame.set_value(df_line, 'dstchannel', v)
                data_frame.set_value(df_line, 'callType', v)
                break
        else:
            for k, v in EXTENSIONS.iteritems():
                if trunk_value.find(k) >= 0:
                    data_frame.set_value(df_line, 'dstchannel', v)
                    data_frame.set_value(df_line, 'callType', 'Interna')
                    data_frame.set_value(df_line, 'callCost1', 0)
                    data_frame.set_value(df_line, 'callCost2', 0)
                    data_frame.set_value(df_line, 'callCost3', 0)
                    break
            else:
                for k, v in TRUNKS_OUTDATED.iteritems():
                    if trunk_value.find(k) >= 0:
                        data_frame.set_value(df_line, 'dstchannel', v)
                        data_frame.set_value(df_line, 'callType', v)
                        break
                # else:
                #     print data_frame.get_value(df_line, 'dst')
    return


# Billsec Formatter:
def billsec_formatter(data_frame):
    for i in range(0, len(data_frame)):
        data_frame.set_value(i, 'billsecInMinutes', round(data_frame['billsec'][i] / MINUTE, 3))
    return


# if len(sys.argv) < NUM_ARGUMENTS:
#     print r'Usage: ./relatorioTelefonia PATH/input.csv]'
#     exit(NUM_ARG_INVALID)

print 'Iniciando Relatorio...'
# save_dbase = False

# Read .csv data
print 'Lendo dados de ligacoes...'
df_call = pd.read_csv(FILE_LOCATION[2])
# df_call = pd.read_csv(sys.argv[1])
# print 'Lendo banco de numeros...'
# df_db = pd.read_csv(DB_LOCATION)
print 'Lendo tabela de custos CLARO...'
df_claro = pd.read_csv(CLARO_COST_LOCATION, index_col=0)
print 'Lendo tabela de custos DIRECTCALL...'
df_directcall = pd.read_csv(DIRECTCALL_COST_LOCATION, index_col=0)
print 'Lendo tabela de custos VIVO...'
df_vivo = pd.read_csv(VIVO_COST_LOCATION, index_col=0)
# print 'Lendo tabela de cidades cobertas por DIRECTCALL...'
# df_dc_cities = pd.read_csv(DIRECTCALL_CITIES_LOCATION)

print 'Deletando colunas excedentes...'
# important columns:
# billsec
# calldate
# dst (call destinations)
# dstchannel (trunk used)
# billsecInMinutes
# dstPlace (call destinations translated for internal users)
# city
# state
# device
# operator
# cost

# delete columns:
del df_call['clid']
del df_call['src']
del df_call['dcontext']
del df_call['duration']
del df_call['channel']
del df_call['lastapp']
del df_call['lastdata']
del df_call['disposition']
del df_call['amaflags']
del df_call['accountcode']
del df_call['uniqueid']
del df_call['userfield']

print 'Formatando coluna de datas...'
output_pdf_name = date_formatter(df_call)
print 'Formatando coluna de troncos...'
trunk_formatter(df_call)
print 'Formatando coluna de duracao...'
billsec_formatter(df_call)
print 'Formatando coluna de destino...'
destination_formatter(df_call, df_claro, df_directcall, df_vivo)
# print 'Calculando custos...'
# cost_calculator(df_call, df_dc_cost)

# print df_call
# print df_call.dtypes
# print df_db
# print df_db.dtypes
# print df_directcall
# print df_directcall.dtypes
# print df_claro
# print df_claro.dtypes
# print df_vivo
# print df_vivo.dtypes


# Groups

print 'Agrupando minutos por data...'
group_day_minutes = df_call.groupby(['calldate'])['billsecInMinutes'].sum()

print 'Agrupando minutos por destino...'
group_destination_minutes = df_call.groupby(['dst'])['billsecInMinutes'].sum()

print 'Agrupando minutos por rota...'
group_route_minutes = df_call.groupby(['callType'])['billsecInMinutes'].sum()

print 'Agrupando minutos por tronco...'
group_trunk_minutes = df_call.groupby(['dstchannel'])['billsecInMinutes'].sum()

print 'Agrupando custo das ligacoes...'
group_call_cost = df_call.groupby(['callType'])['callCost1'].sum()

print 'Configurando grafico...'
# Plotting:
# Graph style
plt.style.use(PLOT_STYLE)
figureList = []
fig_num = 0
print 'Plotando minutos diarios...'
# Day Minutes:
plt.figure(fig_num)
ax = group_day_minutes.plot(kind='bar', color=BI_COLOR, figsize=FIGURE_SIZE, fontsize=FONT_SIZE)
plt.ylim(Y_LIM['day_plot'])
plt.title('Minutos Diarios', fontsize=20)
plt.ylabel('Minutos', fontsize=16)
plt.xlabel('Dias', fontsize=16, verticalalignment='top', horizontalalignment='center')
bars = ax.patches
# Center bar values:
plt.text(0, 601, output_pdf_name)
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + Y_LIM['day_plot'][1] * 0.01,
                str(int(m.ceil(bar.get_height()))),
                horizontalalignment='center', verticalalignment='bottom')
fig_day_minutes = ax.get_figure()
fig_day_minutes.autofmt_xdate()
figureList.append(fig_day_minutes)
fig_num += 1

print 'Plotando minutos por tronco...'
# Trunk Minutes:
plt.figure(fig_num)
ax = group_trunk_minutes.plot(kind='bar', color=QUAD_COLOR, figsize=FIGURE_SIZE, fontsize=FONT_SIZE)
plt.ylim(Y_LIM['trunk_plot'])
plt.title('Minutos Saintes', fontsize=20)
plt.ylabel('Minutos', fontsize=16)
plt.xlabel('Tronco de Saida', fontsize=16)
plt.text(0, 2001, output_pdf_name)
# Center bar values:
bars = ax.patches
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + Y_LIM['trunk_plot'][1] * 0.01,
                str(int(m.ceil(bar.get_height()))),
                horizontalalignment='center', verticalalignment='bottom')
fig_trunk_minutes = ax.get_figure()
fig_trunk_minutes.autofmt_xdate()
figureList.append(fig_trunk_minutes)
fig_num += 1

print 'Plotando minutos por rota...'
# Routes Minutes:
plt.figure(fig_num)
ax = group_route_minutes.plot(kind='bar', color=QUAD_COLOR, figsize=FIGURE_SIZE, fontsize=FONT_SIZE)
plt.ylim(Y_LIM['route_plot'])
plt.title('Minutos por Rota', fontsize=20)
plt.ylabel('Minutos', fontsize=16)
plt.xlabel('Rotas de Saida', fontsize=16)
plt.text(0, 3001, output_pdf_name)
# Center bar values:
bars = ax.patches
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + Y_LIM['route_plot'][1] * 0.01,
                str(int(m.ceil(bar.get_height()))),
                horizontalalignment='center', verticalalignment='bottom')
fig_route_minutes = ax.get_figure()
fig_route_minutes.autofmt_xdate()
figureList.append(fig_route_minutes)
fig_num += 1

print 'Plotando custos por rota...'
# Routes Costs:
plt.figure(fig_num)
ax = group_call_cost.plot(kind='bar', color=QUAD_COLOR, figsize=FIGURE_SIZE, fontsize=FONT_SIZE)
plt.ylim(Y_LIM['cost_plot'])
plt.title('Custo Por Rota', fontsize=20)
plt.ylabel('Valor', fontsize=16)
plt.xlabel('Rotas de Saida', fontsize=16)
plt.text(0, 3001, output_pdf_name)
# Center bar values:
bars = ax.patches
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + Y_LIM['cost_plot'][1] * 0.01,
                'R$ ' + str(m.ceil(bar.get_height())),
                horizontalalignment='center', verticalalignment='bottom')
fig_call_cost = ax.get_figure()
fig_call_cost.autofmt_xdate()
figureList.append(fig_call_cost)
fig_num += 1

print 'Plotando minutos por destino...'
# Destination Minutes:
plt.figure(fig_num)
ax = group_destination_minutes.plot(kind='bar', color=QUAD_COLOR, figsize=FIGURE_SIZE, fontsize=FONT_SIZE)
plt.ylim(Y_LIM['destination_plot'])
plt.title('Minutos Por Destino', fontsize=20)
plt.ylabel('Minutos', fontsize=16)
plt.xlabel('Tipo de Numero', fontsize=16)
plt.text(0, 201, output_pdf_name)
# Center bar values:
bars = ax.patches
for bar in bars:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + Y_LIM['destination_plot'][1] * 0.01,
                str(int(m.ceil(bar.get_height()))),
                horizontalalignment='center', verticalalignment='bottom')
fig_destination_minutes = ax.get_figure()
fig_destination_minutes.autofmt_xdate()
figureList.append(fig_destination_minutes)
fig_num += 1

print 'Criando PDF...'
# Save fig
# Create PDF:
pdf = PdfPages(REPORTS_PATH + output_pdf_name)

# Save Figures:
for fig_num in range(0, len(figureList)):
    print 'Salvando figura {0} - {1}...'.format(fig_num, FIGURE_NUMBER[fig_num])
    pdf.savefig(figureList[fig_num], bbox_inches='tight')

pdf.close()
print 'PDF {0}{1} criado com sucesso.'.format(REPORTS_PATH, output_pdf_name)
# Save DB
# if save_dbase is True:
#     print 'Atualizando o banco de numeros...'
#     df_db.to_csv(DB_LOCATION, index=False, index_label=False)
#     print df_db
#     print df_db.dtypes
