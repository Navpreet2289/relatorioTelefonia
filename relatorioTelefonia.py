#!/usr/bin/env python

from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
# import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
# from requests_file import FileAdapter
# import requests
import pandas as pd
import math as m
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
PATTERN_URA = r's'
PATTERN_CONFERENCE = r'STARTMEETME'

PATTERNS = {
    PATTERN_CONFERENCE: 'Conferencia',
    PATTERN_URA: 'URA',
    PATTERN_EXTENSION: 'Interna',
    PATTERN_FIX_RJ: 'Fixo RJ',
    PATTERN_FIX_SP: 'Fixo SP',
    PATTERN_FIX_OTHERS: 'Fixo DDD',
    PATTERN_CELL_RJ: 'Cell RJ',
    PATTERN_CELL_SP: 'Cell SP',
    PATTERN_CELL_OTHERS: 'Cell DDD',
    PATTERN_0800: '0800',
    PATTERN_INTERNATIONAL: 'Internacional',
    PATTERN_1DIGIT: 'Numero 1 Digito',
    PATTERN_3DIGITS: 'Numero 3 Dgitos ',
    PATTERN_5DIGITS: 'Numero 5 Digitos'
}
CALL_POSSIBILITIES = {
    ('Cell DDD',            'T. Claro - Mobile', 'Cell DDD'):       'Mobile -> Cell DDD',
    ('Cell RJ',             'T. Claro - Mobile', 'Cell Local'):     'Mobile -> Celular RJ',
    ('Cell SP',             'T. Claro - Mobile', 'Cell DDD'):       'Mobile -> Celular SP',
    ('Fixo DDD',            'T. Claro - Mobile', 'Fixo DDD'):       'Mobile -> Fixo Demais Regioes',
    ('Fixo RJ',             'T. Claro - Mobile', 'Fixo Local'):     'Mobile -> Fixo RJ',
    ('Fixo SP',             'T. Claro - Mobile', 'Fixo DDD'):       'Mobile -> Fixo SP',
    ('Numero 1 Digito',     'T. Claro - Mobile', 'Gratis'):         'Mobile -> 1 Digito',
    ('Numero 2 Digitos',    'T. Claro - Mobile', 'Gratis'):         'Mobile -> 2 Digitos',
    ('Numero 3 Digitos',    'T. Claro - Mobile', 'Gratis'):         'Mobile -> 3 Digitos',
    ('Numero 5 Digitos',    'T. Claro - Mobile', 'Fixo Local'):     'Mobile -> 5 Digitos',
    ('0800',                'T. Claro - Mobile', 'Gratis'):         'Mobile -> 0800',

    ('Cell DDD',            'T. Vivo - Fixo', 'Cell DDD'):          'Vivo -> Cell DDD',
    ('Cell RJ',             'T. Vivo - Fixo', 'Cell Local'):        'Vivo -> Celular RJ',
    ('Cell SP',             'T. Vivo - Fixo', 'Cell DDD'):          'Vivo -> Celular SP',
    ('Fixo DDD',            'T. Vivo - Fixo', 'Fixo DDD'):          'Vivo -> Fixo Demais Regioes',
    ('Fixo RJ',             'T. Vivo - Fixo', 'Fixo Local'):        'Vivo -> Fixo RJ',
    ('Fixo SP',             'T. Vivo - Fixo', 'Fixo DDD'):          'Vivo -> Fixo SP',
    ('Numero 1 Digito',     'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 1 Digito',
    ('Numero 2 Digitos',    'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 2 Digitos',
    ('Numero 3 Digitos',    'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 3 Digitos',
    ('Numero 5 Digitos',    'T. Vivo - Fixo', 'Fixo Local'):        'Vivo -> 5 Digitos',
    ('0800',                'T. Vivo - Fixo', 'Gratis'):            'Vivo -> 0800',

    ('Cell DDD',            'T. DirectCall - SP', 'Cell DDD'):      'DirectCall SP -> Cell DDD',
    ('Cell RJ',             'T. DirectCall - SP', 'Cell DDD'):      'DirectCall SP -> Celular RJ',
    ('Cell SP',             'T. DirectCall - SP', 'Cell Local'):    'DirectCall SP -> Celular SP',
    ('Fixo DDD',            'T. DirectCall - SP', 'Fixo DDD'):      'DirectCall SP -> Fixo Demais Regioes',
    ('Fixo RJ',             'T. DirectCall - SP', 'Fixo DDD'):      'DirectCall SP -> Fixo RJ',
    ('Fixo SP',             'T. DirectCall - SP', 'Fixo Local'):    'DirectCall SP -> Fixo SP',
    ('Numero 1 Digito',     'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 1 Digito',
    ('Numero 2 Digitos',    'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 2 Digitos',
    ('Numero 3 Digitos',    'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 3 Digitos',
    ('Numero 5 Digitos',    'T. DirectCall - SP', 'Fixo Local'):    'DirectCall SP -> 5 Digitos',
    ('0800',                'T. DirectCall - SP', 'Gratis'):        'DirectCall SP -> 0800',

    ('Cell DDD',            'T. DirectCall - RJ', 'Cell DDD'):      'DirectCall RJ -> Cell DDD',
    ('Cell RJ',             'T. DirectCall - RJ', 'Cell Local'):    'DirectCall RJ -> Celular RJ',
    ('Cell SP',             'T. DirectCall - RJ', 'Cell DDD'):      'DirectCall RJ -> Celular SP',
    ('Fixo DDD',            'T. DirectCall - RJ', 'Fixo DDD'):      'DirectCall RJ -> Fixo Demais Regioes',
    ('Fixo RJ',             'T. DirectCall - RJ', 'Fixo Local'):    'DirectCall RJ -> Fixo RJ',
    ('Fixo SP',             'T. DirectCall - RJ', 'Fixo DDD'):      'DirectCall RJ -> Fixo SP',
    ('Numero 1 Digito',     'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 1 Digito',
    ('Numero 2 Digitos',    'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 2 Digitos',
    ('Numero 3 Digitos',    'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 3 Digitos',
    ('Numero 5 Digitos',    'T. DirectCall - RJ', 'Fixo Local'):    'DirectCall RJ -> 5 Digitos',
    ('0800',                'T. DirectCall - RJ', 'Gratis'):        'DirectCall RJ -> 0800',
}


# Colors:
BI_COLOR = ['#4286F4', '#6BC924']
QUAD_COLOR = ['#E031C9', '#4286F4', '#ED6E34', '#6BC924']

# Trunks:
TRUNKS_UPDATED = {'DirectCall - RJ': 'T. DirectCall - RJ',
                  'DirectCall - SP': 'T. DirectCall - SP',
                  '22405157':        'T. Vivo - Fixo',
                  'Mobile':          'T. Claro - Mobile',
                  }
TRUNKS_OUTDATED = {'DirectCall': 'T. DirectCall - RJ',
                   '22405157':   'T. Vivo - Fixo',
                   'Mobile':     'T. Claro - Mobile'
                   }
# Extensions:
EXTENSIONS = {
    's':    'URA',
    '100': '100',
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
    '9801': 'Sala de Conf.',
    '9802': 'Sala de Conf.',
    'STARTMEETME': 'Sala de Conf.'
}

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
        date_time = datetime.strptime(data_frame['callDate'][i], '%Y-%m-%d %H:%M:%S')
        if i == 0:
            month = date_time.strftime('%B')
            month_num = date_time.strftime('%m')
            year = date_time.strftime('%Y')
            output_name = '{0}-({1})-{2}.pdf'.format(year, month_num, month)
        if date_time.strftime('%w') is '0' or date_time.strftime('%w') is '6':
            date_string = date_time.strftime('%d/%m/%Y - %a')
        else:
            date_string = date_time.strftime('%d/%m/%Y')
        data_frame.set_value(i, 'callDate', date_string)
    return output_name


# Set call type:
def set_call_type(phone_type, trunk_type, data_frame, df_line, df_claro_cost, df_directcall_cost, df_vivo_cost):
    for cpk, cpv in CALL_POSSIBILITIES.iteritems():
        if (phone_type in cpk) and (trunk_type in cpk):
            data_frame.set_value(df_line, 'callRoute', cpv)
            if re.match('T. Claro - Mobile', cpk[1]):
                cost = df_claro_cost['plano-1'][cpk[2]] * data_frame['billMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost)
                data_frame.set_value(df_line, 'callCost2', cost)
                data_frame.set_value(df_line, 'callCost3', cost)

            elif re.match('T. Vivo - Fixo', cpk[1]):
                cost = df_vivo_cost['plano-1'][cpk[2]] * data_frame['billMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost)
                data_frame.set_value(df_line, 'callCost2', cost)
                data_frame.set_value(df_line, 'callCost3', cost)

            elif re.match('T. DirectCall - SP', cpk[1]):
                cost1 = df_directcall_cost['plano-1'][cpk[2]] * data_frame['billMinutes'][df_line]
                cost2 = df_directcall_cost['plano-2'][cpk[2]] * data_frame['billMinutes'][df_line]
                cost3 = df_directcall_cost['plano-3'][cpk[2]] * data_frame['billMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost1)
                data_frame.set_value(df_line, 'callCost2', cost2)
                data_frame.set_value(df_line, 'callCost3', cost3)

            elif re.match('T. DirectCall - RJ', cpk[1]):
                cost1 = df_directcall_cost['plano-1'][cpk[2]] * data_frame['billMinutes'][df_line]
                cost2 = df_directcall_cost['plano-2'][cpk[2]] * data_frame['billMinutes'][df_line]
                cost3 = df_directcall_cost['plano-3'][cpk[2]] * data_frame['billMinutes'][df_line]

                data_frame.set_value(df_line, 'callCost1', cost1)
                data_frame.set_value(df_line, 'callCost2', cost2)
                data_frame.set_value(df_line, 'callCost3', cost3)
            break
    return


# Dst Formatter:
def destination_formatter(data_frame, df_claro_cost, df_directcall_cost, df_vivo_cost):
    # save_db = False  # flag to control data base save
    for df_line in range(0, len(data_frame)):  # read all lines from data frame
        phone = str(data_frame['callDest'][df_line])  # get all phone numbers from column 'callDest' line by line
        for pk, pv in PATTERNS.iteritems():
            if re.match(pk, phone):
                data_frame.set_value(df_line, 'callDest', pv)
                set_call_type(pv, 
                              data_frame['trunkUsed'][df_line],
                              data_frame, 
                              df_line, 
                              df_claro_cost, 
                              df_directcall_cost, 
                              df_vivo_cost)
                break
        else:
            data_frame.set_value(df_line, 'callRoute', phone)
    return


# Trunk Formatter:
def trunk_formatter(data_frame):
    for df_line in range(0, len(data_frame)):
        trunk_value = str(data_frame['trunkUsed'][df_line])
        for k, v in TRUNKS_UPDATED.iteritems():
            if trunk_value.find(k) >= 0:
                data_frame.set_value(df_line, 'trunkUsed', v)
                data_frame.set_value(df_line, 'callRoute', v)
                data_frame.set_value(df_line, 'callType', 'Externa')
                break
        else:
            for k, v in EXTENSIONS.iteritems():
                if trunk_value.find(k) >= 0:
                    data_frame.set_value(df_line, 'trunkUsed', v)
                    data_frame.set_value(df_line, 'callRoute', 'Interna')
                    data_frame.set_value(df_line, 'callType', 'Interna')
                    data_frame.set_value(df_line, 'callCost1', 0)
                    data_frame.set_value(df_line, 'callCost2', 0)
                    data_frame.set_value(df_line, 'callCost3', 0)
                    break
            else:
                for k, v in TRUNKS_OUTDATED.iteritems():
                    if trunk_value.find(k) >= 0:
                        data_frame.set_value(df_line, 'trunkUsed', v)
                        data_frame.set_value(df_line, 'callRoute', v)
                        data_frame.set_value(df_line, 'callType', 'Externa')
                        break
    return


# Billsec Formatter:
def billsec_formatter(data_frame):
    for i in range(0, len(data_frame)):
        data_frame.set_value(i, 'billMinutes', round(data_frame['billSec'][i] / MINUTE, 3))
    return


# if len(sys.argv) < NUM_ARGUMENTS:
#     print r'Usage: ./relatorioTelefonia PATH/input.csv]'
#     exit(NUM_ARG_INVALID)

print 'Iniciando Relatorio...'
# save_dbase = False

# Read .csv data
print 'Lendo dados de ligacoes...'
df_call = pd.read_csv(FILE_LOCATION[0])
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
# callDate
# billSec
# callDest (call destinations)
# trunkUsed (trunk used)
# billMinutes
# dstPlace (call destinations translated for internal users)
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

print 'Formatando nome das colunas...'
df_call = df_call.rename_axis({'calldate': 'callDate',
                               'billsec': 'billSec',
                               'dst': 'callDest',
                               'dstchannel': 'trunkUsed'}, axis='columns')
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

print df_call
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
group_day_minutes = df_call.groupby(['callDate', 'callType'])['billMinutes'].sum()
print group_day_minutes
# group_day_minutes_internal = df_call[df_call['callRoute'] == 'Interna'].groupby(['callDate'])['billMinutes'].sum()
# print group_day_minutes_external['billMinutes']
# print group_day_minutes_internal
# print '.loc[column == exp, columns to return]:'
# print df_call.loc[df_call['callRoute'] == 'Interna',
#                   ['callDate', 'callRoute', 'billMinutes']].groupby(['callDate'])['billMinutes'].sum()

print 'Agrupando minutos por destino...'
group_destination_minutes = df_call.groupby(['callDest'])['billMinutes'].sum()

print 'Agrupando minutos por rota...'
group_route_minutes = df_call.groupby(['callRoute'])['billMinutes'].sum()

print 'Agrupando minutos por tronco...'
group_trunk_minutes = df_call.groupby(['trunkUsed'])['billMinutes'].sum()

print 'Agrupando custo das ligacoes...'
group_call_cost = df_call.groupby(['callRoute'])['callCost1'].sum()

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
plt.text(0, 601, output_pdf_name)
bars = ax.patches
# Center bar values:
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
plt.text(0, 201, output_pdf_name)
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
plt.text(0, 3001, output_pdf_name)
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
pdf_info = pdf.infodict()
pdf_info['Title'] = 'Relatorio ' + \
                    output_pdf_name[:output_pdf_name.find('-')] + \
                    output_pdf_name[output_pdf_name.find('-')+1:output_pdf_name.find('-')]
pdf_info['Author'] = 'Alexandre Paes'
pdf_info['Subject'] = 'Relatorio das ligacoes registradas pelo Asterisk do mes em questao.'
pdf_info['CreationDate'] = datetime.today()
pdf_info['ModDate'] = datetime.today()

# Save Figures:
for fig_num in range(0, len(figureList)):
    print 'Salvando figura {0} - {1}...'.format(fig_num, FIGURE_NUMBER[fig_num])
    pdf.attach_note('Teste note')
    pdf.savefig(figureList[fig_num], bbox_inches='tight')

pdf.close()
print 'PDF {0}{1} criado com sucesso.'.format(REPORTS_PATH, output_pdf_name)
# Save DB
# if save_dbase is True:
#     print 'Atualizando o banco de numeros...'
#     df_db.to_csv(DB_LOCATION, index=False, index_label=False)
#     print df_db
#     print df_db.dtypes
