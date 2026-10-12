# Generated from EvaParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,68,314,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,1,0,3,0,46,8,0,1,0,5,0,49,8,0,10,0,12,0,52,9,0,1,
        0,1,0,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,3,2,64,8,2,1,3,1,3,1,3,1,3,
        1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,5,6,84,8,
        6,10,6,12,6,87,9,6,1,6,3,6,90,8,6,1,7,1,7,1,7,1,7,1,7,3,7,97,8,7,
        1,8,1,8,5,8,101,8,8,10,8,12,8,104,9,8,1,8,1,8,1,9,1,9,1,9,5,9,111,
        8,9,10,9,12,9,114,9,9,1,10,1,10,3,10,118,8,10,1,11,1,11,1,11,1,11,
        1,11,5,11,125,8,11,10,11,12,11,128,9,11,1,11,3,11,131,8,11,1,12,
        1,12,1,12,1,12,3,12,137,8,12,1,13,1,13,1,13,1,13,1,13,1,13,1,13,
        1,13,1,13,5,13,148,8,13,10,13,12,13,151,9,13,1,13,1,13,1,13,1,13,
        1,13,5,13,158,8,13,10,13,12,13,161,9,13,1,13,1,13,1,13,1,13,1,13,
        1,13,1,13,1,13,5,13,171,8,13,10,13,12,13,174,9,13,1,13,1,13,1,13,
        1,13,1,13,3,13,181,8,13,1,13,1,13,1,13,3,13,186,8,13,1,13,1,13,1,
        13,1,13,1,13,1,13,1,13,5,13,195,8,13,10,13,12,13,198,9,13,1,13,1,
        13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,5,13,212,8,
        13,10,13,12,13,215,9,13,1,13,1,13,1,13,3,13,220,8,13,1,14,1,14,1,
        14,1,14,1,15,1,15,1,15,1,15,1,15,3,15,231,8,15,1,15,1,15,1,16,1,
        16,1,16,1,16,1,17,1,17,3,17,241,8,17,1,18,1,18,1,18,1,18,5,18,247,
        8,18,10,18,12,18,250,9,18,1,18,1,18,1,19,1,19,1,19,1,19,1,19,1,19,
        1,19,1,19,1,19,1,19,5,19,264,8,19,10,19,12,19,267,9,19,3,19,269,
        8,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,3,19,
        282,8,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,
        1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,5,19,305,8,19,
        10,19,12,19,308,9,19,1,20,1,20,1,21,1,21,1,21,0,1,38,22,0,2,4,6,
        8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,0,7,1,0,25,
        26,1,0,47,49,1,0,45,46,1,0,40,43,1,0,38,39,2,0,33,35,60,62,1,0,64,
        65,344,0,45,1,0,0,0,2,55,1,0,0,0,4,63,1,0,0,0,6,65,1,0,0,0,8,69,
        1,0,0,0,10,72,1,0,0,0,12,77,1,0,0,0,14,91,1,0,0,0,16,98,1,0,0,0,
        18,107,1,0,0,0,20,117,1,0,0,0,22,119,1,0,0,0,24,132,1,0,0,0,26,219,
        1,0,0,0,28,221,1,0,0,0,30,225,1,0,0,0,32,234,1,0,0,0,34,238,1,0,
        0,0,36,242,1,0,0,0,38,281,1,0,0,0,40,309,1,0,0,0,42,311,1,0,0,0,
        44,46,3,2,1,0,45,44,1,0,0,0,45,46,1,0,0,0,46,50,1,0,0,0,47,49,3,
        4,2,0,48,47,1,0,0,0,49,52,1,0,0,0,50,48,1,0,0,0,50,51,1,0,0,0,51,
        53,1,0,0,0,52,50,1,0,0,0,53,54,5,0,0,1,54,1,1,0,0,0,55,56,5,1,0,
        0,56,57,5,62,0,0,57,3,1,0,0,0,58,64,3,6,3,0,59,64,3,8,4,0,60,64,
        3,10,5,0,61,64,3,12,6,0,62,64,3,14,7,0,63,58,1,0,0,0,63,59,1,0,0,
        0,63,60,1,0,0,0,63,61,1,0,0,0,63,62,1,0,0,0,64,5,1,0,0,0,65,66,3,
        42,21,0,66,67,5,44,0,0,67,68,3,18,9,0,68,7,1,0,0,0,69,70,5,3,0,0,
        70,71,3,18,9,0,71,9,1,0,0,0,72,73,5,4,0,0,73,74,3,18,9,0,74,75,5,
        22,0,0,75,76,5,62,0,0,76,11,1,0,0,0,77,78,5,5,0,0,78,79,5,64,0,0,
        79,80,5,24,0,0,80,89,3,18,9,0,81,85,5,55,0,0,82,84,3,24,12,0,83,
        82,1,0,0,0,84,87,1,0,0,0,85,83,1,0,0,0,85,86,1,0,0,0,86,88,1,0,0,
        0,87,85,1,0,0,0,88,90,5,56,0,0,89,81,1,0,0,0,89,90,1,0,0,0,90,13,
        1,0,0,0,91,92,5,6,0,0,92,93,3,38,19,0,93,96,3,16,8,0,94,95,5,7,0,
        0,95,97,3,16,8,0,96,94,1,0,0,0,96,97,1,0,0,0,97,15,1,0,0,0,98,102,
        5,55,0,0,99,101,3,4,2,0,100,99,1,0,0,0,101,104,1,0,0,0,102,100,1,
        0,0,0,102,103,1,0,0,0,103,105,1,0,0,0,104,102,1,0,0,0,105,106,5,
        56,0,0,106,17,1,0,0,0,107,112,3,20,10,0,108,109,5,36,0,0,109,111,
        3,26,13,0,110,108,1,0,0,0,111,114,1,0,0,0,112,110,1,0,0,0,112,113,
        1,0,0,0,113,19,1,0,0,0,114,112,1,0,0,0,115,118,3,22,11,0,116,118,
        3,38,19,0,117,115,1,0,0,0,117,116,1,0,0,0,118,21,1,0,0,0,119,120,
        5,2,0,0,120,130,5,62,0,0,121,122,5,23,0,0,122,126,5,55,0,0,123,125,
        3,24,12,0,124,123,1,0,0,0,125,128,1,0,0,0,126,124,1,0,0,0,126,127,
        1,0,0,0,127,129,1,0,0,0,128,126,1,0,0,0,129,131,5,56,0,0,130,121,
        1,0,0,0,130,131,1,0,0,0,131,23,1,0,0,0,132,133,5,64,0,0,133,134,
        5,58,0,0,134,136,3,38,19,0,135,137,5,57,0,0,136,135,1,0,0,0,136,
        137,1,0,0,0,137,25,1,0,0,0,138,139,5,8,0,0,139,220,3,36,18,0,140,
        141,5,9,0,0,141,142,5,20,0,0,142,220,3,38,19,0,143,144,5,10,0,0,
        144,149,3,28,14,0,145,146,5,57,0,0,146,148,3,28,14,0,147,145,1,0,
        0,0,148,151,1,0,0,0,149,147,1,0,0,0,149,150,1,0,0,0,150,220,1,0,
        0,0,151,149,1,0,0,0,152,153,5,11,0,0,153,154,5,53,0,0,154,159,3,
        32,16,0,155,156,5,57,0,0,156,158,3,32,16,0,157,155,1,0,0,0,158,161,
        1,0,0,0,159,157,1,0,0,0,159,160,1,0,0,0,160,162,1,0,0,0,161,159,
        1,0,0,0,162,163,5,54,0,0,163,220,1,0,0,0,164,165,5,12,0,0,165,166,
        5,21,0,0,166,167,5,53,0,0,167,172,3,34,17,0,168,169,5,57,0,0,169,
        171,3,34,17,0,170,168,1,0,0,0,171,174,1,0,0,0,172,170,1,0,0,0,172,
        173,1,0,0,0,173,175,1,0,0,0,174,172,1,0,0,0,175,176,5,54,0,0,176,
        220,1,0,0,0,177,178,5,13,0,0,178,180,5,27,0,0,179,181,3,36,18,0,
        180,179,1,0,0,0,180,181,1,0,0,0,181,220,1,0,0,0,182,183,5,13,0,0,
        183,185,5,28,0,0,184,186,3,36,18,0,185,184,1,0,0,0,185,186,1,0,0,
        0,186,220,1,0,0,0,187,188,5,13,0,0,188,189,5,29,0,0,189,220,3,36,
        18,0,190,191,5,14,0,0,191,196,3,28,14,0,192,193,5,57,0,0,193,195,
        3,28,14,0,194,192,1,0,0,0,195,198,1,0,0,0,196,194,1,0,0,0,196,197,
        1,0,0,0,197,220,1,0,0,0,198,196,1,0,0,0,199,200,5,15,0,0,200,201,
        3,42,21,0,201,202,5,37,0,0,202,203,5,64,0,0,203,220,1,0,0,0,204,
        205,5,16,0,0,205,206,5,21,0,0,206,220,3,36,18,0,207,208,5,17,0,0,
        208,213,3,30,15,0,209,210,5,57,0,0,210,212,3,30,15,0,211,209,1,0,
        0,0,212,215,1,0,0,0,213,211,1,0,0,0,213,214,1,0,0,0,214,220,1,0,
        0,0,215,213,1,0,0,0,216,217,5,18,0,0,217,220,5,61,0,0,218,220,5,
        19,0,0,219,138,1,0,0,0,219,140,1,0,0,0,219,143,1,0,0,0,219,152,1,
        0,0,0,219,164,1,0,0,0,219,177,1,0,0,0,219,182,1,0,0,0,219,187,1,
        0,0,0,219,190,1,0,0,0,219,199,1,0,0,0,219,204,1,0,0,0,219,207,1,
        0,0,0,219,216,1,0,0,0,219,218,1,0,0,0,220,27,1,0,0,0,221,222,3,42,
        21,0,222,223,5,44,0,0,223,224,3,38,19,0,224,29,1,0,0,0,225,226,3,
        42,21,0,226,227,5,44,0,0,227,228,5,64,0,0,228,230,5,51,0,0,229,231,
        3,42,21,0,230,229,1,0,0,0,230,231,1,0,0,0,231,232,1,0,0,0,232,233,
        5,52,0,0,233,31,1,0,0,0,234,235,3,42,21,0,235,236,5,37,0,0,236,237,
        3,42,21,0,237,33,1,0,0,0,238,240,3,42,21,0,239,241,7,0,0,0,240,239,
        1,0,0,0,240,241,1,0,0,0,241,35,1,0,0,0,242,243,5,53,0,0,243,248,
        3,42,21,0,244,245,5,57,0,0,245,247,3,42,21,0,246,244,1,0,0,0,247,
        250,1,0,0,0,248,246,1,0,0,0,248,249,1,0,0,0,249,251,1,0,0,0,250,
        248,1,0,0,0,251,252,5,54,0,0,252,37,1,0,0,0,253,254,6,19,-1,0,254,
        255,5,51,0,0,255,256,3,38,19,0,256,257,5,52,0,0,257,282,1,0,0,0,
        258,259,5,64,0,0,259,268,5,51,0,0,260,265,3,38,19,0,261,262,5,57,
        0,0,262,264,3,38,19,0,263,261,1,0,0,0,264,267,1,0,0,0,265,263,1,
        0,0,0,265,266,1,0,0,0,266,269,1,0,0,0,267,265,1,0,0,0,268,260,1,
        0,0,0,268,269,1,0,0,0,269,270,1,0,0,0,270,282,5,52,0,0,271,272,3,
        42,21,0,272,273,5,59,0,0,273,274,3,42,21,0,274,282,1,0,0,0,275,276,
        5,46,0,0,276,282,3,38,19,10,277,278,5,32,0,0,278,282,3,38,19,5,279,
        282,3,40,20,0,280,282,3,42,21,0,281,253,1,0,0,0,281,258,1,0,0,0,
        281,271,1,0,0,0,281,275,1,0,0,0,281,277,1,0,0,0,281,279,1,0,0,0,
        281,280,1,0,0,0,282,306,1,0,0,0,283,284,10,11,0,0,284,285,5,50,0,
        0,285,305,3,38,19,11,286,287,10,9,0,0,287,288,7,1,0,0,288,305,3,
        38,19,10,289,290,10,8,0,0,290,291,7,2,0,0,291,305,3,38,19,9,292,
        293,10,7,0,0,293,294,7,3,0,0,294,305,3,38,19,8,295,296,10,6,0,0,
        296,297,7,4,0,0,297,305,3,38,19,7,298,299,10,4,0,0,299,300,5,30,
        0,0,300,305,3,38,19,5,301,302,10,3,0,0,302,303,5,31,0,0,303,305,
        3,38,19,4,304,283,1,0,0,0,304,286,1,0,0,0,304,289,1,0,0,0,304,292,
        1,0,0,0,304,295,1,0,0,0,304,298,1,0,0,0,304,301,1,0,0,0,305,308,
        1,0,0,0,306,304,1,0,0,0,306,307,1,0,0,0,307,39,1,0,0,0,308,306,1,
        0,0,0,309,310,7,5,0,0,310,41,1,0,0,0,311,312,7,6,0,0,312,43,1,0,
        0,0,28,45,50,63,85,89,96,102,112,117,126,130,136,149,159,172,180,
        185,196,213,219,230,240,248,265,268,281,304,306
    ]

class EvaParser ( Parser ):

    grammarFileName = "EvaParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'NERV'", "'ENTRY_PLUG'", "'MONITOR'", 
                     "'SEELE'", "'HOLOGRAM'", "'PATTERN_BLUE'", "'PATTERN_ORANGE'", 
                     "'TARGET'", "'AT_FIELD'", "'SYNC'", "'CODENAME'", "'FORMATION'", 
                     "'EJECT'", "'DUMMY_PLUG'", "'EQUIP'", "'SQUAD'", "'MAGI'", 
                     "'BATTERY'", "'DIAGNOSTIC'", "'donde'", "'por'", "'como'", 
                     "'con'", "'de'", "'asc'", "'desc'", "'duplicados'", 
                     "'faltantes'", "'columnas'", "'y'", "'o'", "'no'", 
                     "'verdadero'", "'falso'", "'nulo'", "'|>'", "'->'", 
                     "'=='", "'!='", "'<='", "'>='", "'<'", "'>'", "'='", 
                     "'+'", "'-'", "'*'", "'/'", "'%'", "'^'", "'('", "')'", 
                     "'['", "']'", "'{'", "'}'", "','", "':'", "'.'" ]

    symbolicNames = [ "<INVALID>", "NERV", "ENTRY_PLUG", "MONITOR", "SEELE", 
                      "HOLOGRAM", "PATTERN_BLUE", "PATTERN_ORANGE", "TARGET", 
                      "AT_FIELD", "SYNC", "CODENAME", "FORMATION", "EJECT", 
                      "DUMMY_PLUG", "EQUIP", "SQUAD", "MAGI", "BATTERY", 
                      "DIAGNOSTIC", "DONDE", "POR", "COMO", "CON", "DE", 
                      "ASC", "DESC", "DUPLICADOS", "FALTANTES", "COLUMNAS", 
                      "Y", "O", "NO", "VERDADERO", "FALSO", "NULO", "TUBERIA", 
                      "FLECHA", "IGUAL_IGUAL", "DIFERENTE", "MENOR_IGUAL", 
                      "MAYOR_IGUAL", "MENOR", "MAYOR", "IGUAL", "MAS", "MENOS", 
                      "POR_OP", "DIV", "MODULO", "POTENCIA", "PAR_IZQ", 
                      "PAR_DER", "COR_IZQ", "COR_DER", "LLAVE_IZQ", "LLAVE_DER", 
                      "COMA", "DOS_PUNTOS", "PUNTO", "REAL", "ENTERO", "CADENA", 
                      "CADENA_SIN_CERRAR", "ID", "ID_ESCAPADO", "COMENTARIO", 
                      "ESPACIOS", "CARACTER_INVALIDO" ]

    RULE_programa = 0
    RULE_cabecera = 1
    RULE_sentencia = 2
    RULE_asignacion = 3
    RULE_mostrar = 4
    RULE_guardar = 5
    RULE_graficar = 6
    RULE_condicional = 7
    RULE_bloque = 8
    RULE_flujo = 9
    RULE_fuente = 10
    RULE_carga = 11
    RULE_opcion = 12
    RULE_etapa = 13
    RULE_columnaNueva = 14
    RULE_agregacion = 15
    RULE_renombre = 16
    RULE_criterio = 17
    RULE_listaColumnas = 18
    RULE_expresion = 19
    RULE_literal = 20
    RULE_nombre = 21

    ruleNames =  [ "programa", "cabecera", "sentencia", "asignacion", "mostrar", 
                   "guardar", "graficar", "condicional", "bloque", "flujo", 
                   "fuente", "carga", "opcion", "etapa", "columnaNueva", 
                   "agregacion", "renombre", "criterio", "listaColumnas", 
                   "expresion", "literal", "nombre" ]

    EOF = Token.EOF
    NERV=1
    ENTRY_PLUG=2
    MONITOR=3
    SEELE=4
    HOLOGRAM=5
    PATTERN_BLUE=6
    PATTERN_ORANGE=7
    TARGET=8
    AT_FIELD=9
    SYNC=10
    CODENAME=11
    FORMATION=12
    EJECT=13
    DUMMY_PLUG=14
    EQUIP=15
    SQUAD=16
    MAGI=17
    BATTERY=18
    DIAGNOSTIC=19
    DONDE=20
    POR=21
    COMO=22
    CON=23
    DE=24
    ASC=25
    DESC=26
    DUPLICADOS=27
    FALTANTES=28
    COLUMNAS=29
    Y=30
    O=31
    NO=32
    VERDADERO=33
    FALSO=34
    NULO=35
    TUBERIA=36
    FLECHA=37
    IGUAL_IGUAL=38
    DIFERENTE=39
    MENOR_IGUAL=40
    MAYOR_IGUAL=41
    MENOR=42
    MAYOR=43
    IGUAL=44
    MAS=45
    MENOS=46
    POR_OP=47
    DIV=48
    MODULO=49
    POTENCIA=50
    PAR_IZQ=51
    PAR_DER=52
    COR_IZQ=53
    COR_DER=54
    LLAVE_IZQ=55
    LLAVE_DER=56
    COMA=57
    DOS_PUNTOS=58
    PUNTO=59
    REAL=60
    ENTERO=61
    CADENA=62
    CADENA_SIN_CERRAR=63
    ID=64
    ID_ESCAPADO=65
    COMENTARIO=66
    ESPACIOS=67
    CARACTER_INVALIDO=68

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(EvaParser.EOF, 0)

        def cabecera(self):
            return self.getTypedRuleContext(EvaParser.CabeceraContext,0)


        def sentencia(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.SentenciaContext)
            else:
                return self.getTypedRuleContext(EvaParser.SentenciaContext,i)


        def getRuleIndex(self):
            return EvaParser.RULE_programa

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrograma" ):
                return visitor.visitPrograma(self)
            else:
                return visitor.visitChildren(self)




    def programa(self):

        localctx = EvaParser.ProgramaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_programa)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 44
                self.cabecera()


            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 3)) & ~0x3f) == 0 and ((1 << (_la - 3)) & 6917529027641081871) != 0):
                self.state = 47
                self.sentencia()
                self.state = 52
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 53
            self.match(EvaParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CabeceraContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NERV(self):
            return self.getToken(EvaParser.NERV, 0)

        def CADENA(self):
            return self.getToken(EvaParser.CADENA, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_cabecera

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCabecera" ):
                return visitor.visitCabecera(self)
            else:
                return visitor.visitChildren(self)




    def cabecera(self):

        localctx = EvaParser.CabeceraContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_cabecera)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(EvaParser.NERV)
            self.state = 56
            self.match(EvaParser.CADENA)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SentenciaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def asignacion(self):
            return self.getTypedRuleContext(EvaParser.AsignacionContext,0)


        def mostrar(self):
            return self.getTypedRuleContext(EvaParser.MostrarContext,0)


        def guardar(self):
            return self.getTypedRuleContext(EvaParser.GuardarContext,0)


        def graficar(self):
            return self.getTypedRuleContext(EvaParser.GraficarContext,0)


        def condicional(self):
            return self.getTypedRuleContext(EvaParser.CondicionalContext,0)


        def getRuleIndex(self):
            return EvaParser.RULE_sentencia

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSentencia" ):
                return visitor.visitSentencia(self)
            else:
                return visitor.visitChildren(self)




    def sentencia(self):

        localctx = EvaParser.SentenciaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_sentencia)
        try:
            self.state = 63
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [64, 65]:
                self.enterOuterAlt(localctx, 1)
                self.state = 58
                self.asignacion()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 59
                self.mostrar()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 3)
                self.state = 60
                self.guardar()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 61
                self.graficar()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 5)
                self.state = 62
                self.condicional()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AsignacionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nombre(self):
            return self.getTypedRuleContext(EvaParser.NombreContext,0)


        def IGUAL(self):
            return self.getToken(EvaParser.IGUAL, 0)

        def flujo(self):
            return self.getTypedRuleContext(EvaParser.FlujoContext,0)


        def getRuleIndex(self):
            return EvaParser.RULE_asignacion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAsignacion" ):
                return visitor.visitAsignacion(self)
            else:
                return visitor.visitChildren(self)




    def asignacion(self):

        localctx = EvaParser.AsignacionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_asignacion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.nombre()
            self.state = 66
            self.match(EvaParser.IGUAL)
            self.state = 67
            self.flujo()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MostrarContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MONITOR(self):
            return self.getToken(EvaParser.MONITOR, 0)

        def flujo(self):
            return self.getTypedRuleContext(EvaParser.FlujoContext,0)


        def getRuleIndex(self):
            return EvaParser.RULE_mostrar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMostrar" ):
                return visitor.visitMostrar(self)
            else:
                return visitor.visitChildren(self)




    def mostrar(self):

        localctx = EvaParser.MostrarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_mostrar)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.match(EvaParser.MONITOR)
            self.state = 70
            self.flujo()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GuardarContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEELE(self):
            return self.getToken(EvaParser.SEELE, 0)

        def flujo(self):
            return self.getTypedRuleContext(EvaParser.FlujoContext,0)


        def COMO(self):
            return self.getToken(EvaParser.COMO, 0)

        def CADENA(self):
            return self.getToken(EvaParser.CADENA, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_guardar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGuardar" ):
                return visitor.visitGuardar(self)
            else:
                return visitor.visitChildren(self)




    def guardar(self):

        localctx = EvaParser.GuardarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_guardar)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(EvaParser.SEELE)
            self.state = 73
            self.flujo()
            self.state = 74
            self.match(EvaParser.COMO)
            self.state = 75
            self.match(EvaParser.CADENA)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GraficarContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HOLOGRAM(self):
            return self.getToken(EvaParser.HOLOGRAM, 0)

        def ID(self):
            return self.getToken(EvaParser.ID, 0)

        def DE(self):
            return self.getToken(EvaParser.DE, 0)

        def flujo(self):
            return self.getTypedRuleContext(EvaParser.FlujoContext,0)


        def LLAVE_IZQ(self):
            return self.getToken(EvaParser.LLAVE_IZQ, 0)

        def LLAVE_DER(self):
            return self.getToken(EvaParser.LLAVE_DER, 0)

        def opcion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.OpcionContext)
            else:
                return self.getTypedRuleContext(EvaParser.OpcionContext,i)


        def getRuleIndex(self):
            return EvaParser.RULE_graficar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGraficar" ):
                return visitor.visitGraficar(self)
            else:
                return visitor.visitChildren(self)




    def graficar(self):

        localctx = EvaParser.GraficarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_graficar)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.match(EvaParser.HOLOGRAM)
            self.state = 78
            self.match(EvaParser.ID)
            self.state = 79
            self.match(EvaParser.DE)
            self.state = 80
            self.flujo()
            self.state = 89
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==55:
                self.state = 81
                self.match(EvaParser.LLAVE_IZQ)
                self.state = 85
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==64:
                    self.state = 82
                    self.opcion()
                    self.state = 87
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 88
                self.match(EvaParser.LLAVE_DER)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CondicionalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PATTERN_BLUE(self):
            return self.getToken(EvaParser.PATTERN_BLUE, 0)

        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def bloque(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.BloqueContext)
            else:
                return self.getTypedRuleContext(EvaParser.BloqueContext,i)


        def PATTERN_ORANGE(self):
            return self.getToken(EvaParser.PATTERN_ORANGE, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_condicional

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCondicional" ):
                return visitor.visitCondicional(self)
            else:
                return visitor.visitChildren(self)




    def condicional(self):

        localctx = EvaParser.CondicionalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_condicional)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.match(EvaParser.PATTERN_BLUE)
            self.state = 92
            self.expresion(0)
            self.state = 93
            self.bloque()
            self.state = 96
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 94
                self.match(EvaParser.PATTERN_ORANGE)
                self.state = 95
                self.bloque()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BloqueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LLAVE_IZQ(self):
            return self.getToken(EvaParser.LLAVE_IZQ, 0)

        def LLAVE_DER(self):
            return self.getToken(EvaParser.LLAVE_DER, 0)

        def sentencia(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.SentenciaContext)
            else:
                return self.getTypedRuleContext(EvaParser.SentenciaContext,i)


        def getRuleIndex(self):
            return EvaParser.RULE_bloque

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBloque" ):
                return visitor.visitBloque(self)
            else:
                return visitor.visitChildren(self)




    def bloque(self):

        localctx = EvaParser.BloqueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_bloque)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 98
            self.match(EvaParser.LLAVE_IZQ)
            self.state = 102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 3)) & ~0x3f) == 0 and ((1 << (_la - 3)) & 6917529027641081871) != 0):
                self.state = 99
                self.sentencia()
                self.state = 104
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 105
            self.match(EvaParser.LLAVE_DER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FlujoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fuente(self):
            return self.getTypedRuleContext(EvaParser.FuenteContext,0)


        def TUBERIA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.TUBERIA)
            else:
                return self.getToken(EvaParser.TUBERIA, i)

        def etapa(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.EtapaContext)
            else:
                return self.getTypedRuleContext(EvaParser.EtapaContext,i)


        def getRuleIndex(self):
            return EvaParser.RULE_flujo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFlujo" ):
                return visitor.visitFlujo(self)
            else:
                return visitor.visitChildren(self)




    def flujo(self):

        localctx = EvaParser.FlujoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_flujo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            self.fuente()
            self.state = 112
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==36:
                self.state = 108
                self.match(EvaParser.TUBERIA)
                self.state = 109
                self.etapa()
                self.state = 114
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FuenteContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def carga(self):
            return self.getTypedRuleContext(EvaParser.CargaContext,0)


        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def getRuleIndex(self):
            return EvaParser.RULE_fuente

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFuente" ):
                return visitor.visitFuente(self)
            else:
                return visitor.visitChildren(self)




    def fuente(self):

        localctx = EvaParser.FuenteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_fuente)
        try:
            self.state = 117
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 115
                self.carga()
                pass
            elif token in [32, 33, 34, 35, 46, 51, 60, 61, 62, 64, 65]:
                self.enterOuterAlt(localctx, 2)
                self.state = 116
                self.expresion(0)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CargaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENTRY_PLUG(self):
            return self.getToken(EvaParser.ENTRY_PLUG, 0)

        def CADENA(self):
            return self.getToken(EvaParser.CADENA, 0)

        def CON(self):
            return self.getToken(EvaParser.CON, 0)

        def LLAVE_IZQ(self):
            return self.getToken(EvaParser.LLAVE_IZQ, 0)

        def LLAVE_DER(self):
            return self.getToken(EvaParser.LLAVE_DER, 0)

        def opcion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.OpcionContext)
            else:
                return self.getTypedRuleContext(EvaParser.OpcionContext,i)


        def getRuleIndex(self):
            return EvaParser.RULE_carga

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCarga" ):
                return visitor.visitCarga(self)
            else:
                return visitor.visitChildren(self)




    def carga(self):

        localctx = EvaParser.CargaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_carga)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 119
            self.match(EvaParser.ENTRY_PLUG)
            self.state = 120
            self.match(EvaParser.CADENA)
            self.state = 130
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==23:
                self.state = 121
                self.match(EvaParser.CON)
                self.state = 122
                self.match(EvaParser.LLAVE_IZQ)
                self.state = 126
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==64:
                    self.state = 123
                    self.opcion()
                    self.state = 128
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 129
                self.match(EvaParser.LLAVE_DER)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OpcionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(EvaParser.ID, 0)

        def DOS_PUNTOS(self):
            return self.getToken(EvaParser.DOS_PUNTOS, 0)

        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def COMA(self):
            return self.getToken(EvaParser.COMA, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_opcion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpcion" ):
                return visitor.visitOpcion(self)
            else:
                return visitor.visitChildren(self)




    def opcion(self):

        localctx = EvaParser.OpcionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_opcion)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 132
            self.match(EvaParser.ID)
            self.state = 133
            self.match(EvaParser.DOS_PUNTOS)
            self.state = 134
            self.expresion(0)
            self.state = 136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==57:
                self.state = 135
                self.match(EvaParser.COMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EtapaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return EvaParser.RULE_etapa

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class EtapaFiltrarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def AT_FIELD(self):
            return self.getToken(EvaParser.AT_FIELD, 0)
        def DONDE(self):
            return self.getToken(EvaParser.DONDE, 0)
        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaFiltrar" ):
                return visitor.visitEtapaFiltrar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaSeleccionarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def TARGET(self):
            return self.getToken(EvaParser.TARGET, 0)
        def listaColumnas(self):
            return self.getTypedRuleContext(EvaParser.ListaColumnasContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaSeleccionar" ):
                return visitor.visitEtapaSeleccionar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaQuitarDuplicadosContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EJECT(self):
            return self.getToken(EvaParser.EJECT, 0)
        def DUPLICADOS(self):
            return self.getToken(EvaParser.DUPLICADOS, 0)
        def listaColumnas(self):
            return self.getTypedRuleContext(EvaParser.ListaColumnasContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaQuitarDuplicados" ):
                return visitor.visitEtapaQuitarDuplicados(self)
            else:
                return visitor.visitChildren(self)


    class EtapaDiagnosticoContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def DIAGNOSTIC(self):
            return self.getToken(EvaParser.DIAGNOSTIC, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaDiagnostico" ):
                return visitor.visitEtapaDiagnostico(self)
            else:
                return visitor.visitChildren(self)


    class EtapaOrdenarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FORMATION(self):
            return self.getToken(EvaParser.FORMATION, 0)
        def POR(self):
            return self.getToken(EvaParser.POR, 0)
        def COR_IZQ(self):
            return self.getToken(EvaParser.COR_IZQ, 0)
        def criterio(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.CriterioContext)
            else:
                return self.getTypedRuleContext(EvaParser.CriterioContext,i)

        def COR_DER(self):
            return self.getToken(EvaParser.COR_DER, 0)
        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaOrdenar" ):
                return visitor.visitEtapaOrdenar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaLimitarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BATTERY(self):
            return self.getToken(EvaParser.BATTERY, 0)
        def ENTERO(self):
            return self.getToken(EvaParser.ENTERO, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaLimitar" ):
                return visitor.visitEtapaLimitar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaRenombrarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def CODENAME(self):
            return self.getToken(EvaParser.CODENAME, 0)
        def COR_IZQ(self):
            return self.getToken(EvaParser.COR_IZQ, 0)
        def renombre(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.RenombreContext)
            else:
                return self.getTypedRuleContext(EvaParser.RenombreContext,i)

        def COR_DER(self):
            return self.getToken(EvaParser.COR_DER, 0)
        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaRenombrar" ):
                return visitor.visitEtapaRenombrar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaResumirContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def MAGI(self):
            return self.getToken(EvaParser.MAGI, 0)
        def agregacion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.AgregacionContext)
            else:
                return self.getTypedRuleContext(EvaParser.AgregacionContext,i)

        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaResumir" ):
                return visitor.visitEtapaResumir(self)
            else:
                return visitor.visitChildren(self)


    class EtapaConvertirContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EQUIP(self):
            return self.getToken(EvaParser.EQUIP, 0)
        def nombre(self):
            return self.getTypedRuleContext(EvaParser.NombreContext,0)

        def FLECHA(self):
            return self.getToken(EvaParser.FLECHA, 0)
        def ID(self):
            return self.getToken(EvaParser.ID, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaConvertir" ):
                return visitor.visitEtapaConvertir(self)
            else:
                return visitor.visitChildren(self)


    class EtapaAgruparContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SQUAD(self):
            return self.getToken(EvaParser.SQUAD, 0)
        def POR(self):
            return self.getToken(EvaParser.POR, 0)
        def listaColumnas(self):
            return self.getTypedRuleContext(EvaParser.ListaColumnasContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaAgrupar" ):
                return visitor.visitEtapaAgrupar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaCrearContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SYNC(self):
            return self.getToken(EvaParser.SYNC, 0)
        def columnaNueva(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ColumnaNuevaContext)
            else:
                return self.getTypedRuleContext(EvaParser.ColumnaNuevaContext,i)

        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaCrear" ):
                return visitor.visitEtapaCrear(self)
            else:
                return visitor.visitChildren(self)


    class EtapaRellenarContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def DUMMY_PLUG(self):
            return self.getToken(EvaParser.DUMMY_PLUG, 0)
        def columnaNueva(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ColumnaNuevaContext)
            else:
                return self.getTypedRuleContext(EvaParser.ColumnaNuevaContext,i)

        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaRellenar" ):
                return visitor.visitEtapaRellenar(self)
            else:
                return visitor.visitChildren(self)


    class EtapaQuitarColumnasContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EJECT(self):
            return self.getToken(EvaParser.EJECT, 0)
        def COLUMNAS(self):
            return self.getToken(EvaParser.COLUMNAS, 0)
        def listaColumnas(self):
            return self.getTypedRuleContext(EvaParser.ListaColumnasContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaQuitarColumnas" ):
                return visitor.visitEtapaQuitarColumnas(self)
            else:
                return visitor.visitChildren(self)


    class EtapaQuitarFaltantesContext(EtapaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.EtapaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EJECT(self):
            return self.getToken(EvaParser.EJECT, 0)
        def FALTANTES(self):
            return self.getToken(EvaParser.FALTANTES, 0)
        def listaColumnas(self):
            return self.getTypedRuleContext(EvaParser.ListaColumnasContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEtapaQuitarFaltantes" ):
                return visitor.visitEtapaQuitarFaltantes(self)
            else:
                return visitor.visitChildren(self)



    def etapa(self):

        localctx = EvaParser.EtapaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_etapa)
        self._la = 0 # Token type
        try:
            self.state = 219
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                localctx = EvaParser.EtapaSeleccionarContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 138
                self.match(EvaParser.TARGET)
                self.state = 139
                self.listaColumnas()
                pass

            elif la_ == 2:
                localctx = EvaParser.EtapaFiltrarContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 140
                self.match(EvaParser.AT_FIELD)
                self.state = 141
                self.match(EvaParser.DONDE)
                self.state = 142
                self.expresion(0)
                pass

            elif la_ == 3:
                localctx = EvaParser.EtapaCrearContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 143
                self.match(EvaParser.SYNC)
                self.state = 144
                self.columnaNueva()
                self.state = 149
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==57:
                    self.state = 145
                    self.match(EvaParser.COMA)
                    self.state = 146
                    self.columnaNueva()
                    self.state = 151
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 4:
                localctx = EvaParser.EtapaRenombrarContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 152
                self.match(EvaParser.CODENAME)
                self.state = 153
                self.match(EvaParser.COR_IZQ)
                self.state = 154
                self.renombre()
                self.state = 159
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==57:
                    self.state = 155
                    self.match(EvaParser.COMA)
                    self.state = 156
                    self.renombre()
                    self.state = 161
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 162
                self.match(EvaParser.COR_DER)
                pass

            elif la_ == 5:
                localctx = EvaParser.EtapaOrdenarContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 164
                self.match(EvaParser.FORMATION)
                self.state = 165
                self.match(EvaParser.POR)
                self.state = 166
                self.match(EvaParser.COR_IZQ)
                self.state = 167
                self.criterio()
                self.state = 172
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==57:
                    self.state = 168
                    self.match(EvaParser.COMA)
                    self.state = 169
                    self.criterio()
                    self.state = 174
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 175
                self.match(EvaParser.COR_DER)
                pass

            elif la_ == 6:
                localctx = EvaParser.EtapaQuitarDuplicadosContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 177
                self.match(EvaParser.EJECT)
                self.state = 178
                self.match(EvaParser.DUPLICADOS)
                self.state = 180
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==53:
                    self.state = 179
                    self.listaColumnas()


                pass

            elif la_ == 7:
                localctx = EvaParser.EtapaQuitarFaltantesContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 182
                self.match(EvaParser.EJECT)
                self.state = 183
                self.match(EvaParser.FALTANTES)
                self.state = 185
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==53:
                    self.state = 184
                    self.listaColumnas()


                pass

            elif la_ == 8:
                localctx = EvaParser.EtapaQuitarColumnasContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 187
                self.match(EvaParser.EJECT)
                self.state = 188
                self.match(EvaParser.COLUMNAS)
                self.state = 189
                self.listaColumnas()
                pass

            elif la_ == 9:
                localctx = EvaParser.EtapaRellenarContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 190
                self.match(EvaParser.DUMMY_PLUG)
                self.state = 191
                self.columnaNueva()
                self.state = 196
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==57:
                    self.state = 192
                    self.match(EvaParser.COMA)
                    self.state = 193
                    self.columnaNueva()
                    self.state = 198
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 10:
                localctx = EvaParser.EtapaConvertirContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 199
                self.match(EvaParser.EQUIP)
                self.state = 200
                self.nombre()
                self.state = 201
                self.match(EvaParser.FLECHA)
                self.state = 202
                self.match(EvaParser.ID)
                pass

            elif la_ == 11:
                localctx = EvaParser.EtapaAgruparContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 204
                self.match(EvaParser.SQUAD)
                self.state = 205
                self.match(EvaParser.POR)
                self.state = 206
                self.listaColumnas()
                pass

            elif la_ == 12:
                localctx = EvaParser.EtapaResumirContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 207
                self.match(EvaParser.MAGI)
                self.state = 208
                self.agregacion()
                self.state = 213
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==57:
                    self.state = 209
                    self.match(EvaParser.COMA)
                    self.state = 210
                    self.agregacion()
                    self.state = 215
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 13:
                localctx = EvaParser.EtapaLimitarContext(self, localctx)
                self.enterOuterAlt(localctx, 13)
                self.state = 216
                self.match(EvaParser.BATTERY)
                self.state = 217
                self.match(EvaParser.ENTERO)
                pass

            elif la_ == 14:
                localctx = EvaParser.EtapaDiagnosticoContext(self, localctx)
                self.enterOuterAlt(localctx, 14)
                self.state = 218
                self.match(EvaParser.DIAGNOSTIC)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnaNuevaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nombre(self):
            return self.getTypedRuleContext(EvaParser.NombreContext,0)


        def IGUAL(self):
            return self.getToken(EvaParser.IGUAL, 0)

        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def getRuleIndex(self):
            return EvaParser.RULE_columnaNueva

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnaNueva" ):
                return visitor.visitColumnaNueva(self)
            else:
                return visitor.visitChildren(self)




    def columnaNueva(self):

        localctx = EvaParser.ColumnaNuevaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_columnaNueva)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 221
            self.nombre()
            self.state = 222
            self.match(EvaParser.IGUAL)
            self.state = 223
            self.expresion(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AgregacionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nombre(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.NombreContext)
            else:
                return self.getTypedRuleContext(EvaParser.NombreContext,i)


        def IGUAL(self):
            return self.getToken(EvaParser.IGUAL, 0)

        def ID(self):
            return self.getToken(EvaParser.ID, 0)

        def PAR_IZQ(self):
            return self.getToken(EvaParser.PAR_IZQ, 0)

        def PAR_DER(self):
            return self.getToken(EvaParser.PAR_DER, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_agregacion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAgregacion" ):
                return visitor.visitAgregacion(self)
            else:
                return visitor.visitChildren(self)




    def agregacion(self):

        localctx = EvaParser.AgregacionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_agregacion)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self.nombre()
            self.state = 226
            self.match(EvaParser.IGUAL)
            self.state = 227
            self.match(EvaParser.ID)
            self.state = 228
            self.match(EvaParser.PAR_IZQ)
            self.state = 230
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==64 or _la==65:
                self.state = 229
                self.nombre()


            self.state = 232
            self.match(EvaParser.PAR_DER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RenombreContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nombre(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.NombreContext)
            else:
                return self.getTypedRuleContext(EvaParser.NombreContext,i)


        def FLECHA(self):
            return self.getToken(EvaParser.FLECHA, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_renombre

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRenombre" ):
                return visitor.visitRenombre(self)
            else:
                return visitor.visitChildren(self)




    def renombre(self):

        localctx = EvaParser.RenombreContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_renombre)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 234
            self.nombre()
            self.state = 235
            self.match(EvaParser.FLECHA)
            self.state = 236
            self.nombre()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CriterioContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nombre(self):
            return self.getTypedRuleContext(EvaParser.NombreContext,0)


        def ASC(self):
            return self.getToken(EvaParser.ASC, 0)

        def DESC(self):
            return self.getToken(EvaParser.DESC, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_criterio

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCriterio" ):
                return visitor.visitCriterio(self)
            else:
                return visitor.visitChildren(self)




    def criterio(self):

        localctx = EvaParser.CriterioContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_criterio)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 238
            self.nombre()
            self.state = 240
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==25 or _la==26:
                self.state = 239
                _la = self._input.LA(1)
                if not(_la==25 or _la==26):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ListaColumnasContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COR_IZQ(self):
            return self.getToken(EvaParser.COR_IZQ, 0)

        def nombre(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.NombreContext)
            else:
                return self.getTypedRuleContext(EvaParser.NombreContext,i)


        def COR_DER(self):
            return self.getToken(EvaParser.COR_DER, 0)

        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def getRuleIndex(self):
            return EvaParser.RULE_listaColumnas

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitListaColumnas" ):
                return visitor.visitListaColumnas(self)
            else:
                return visitor.visitChildren(self)




    def listaColumnas(self):

        localctx = EvaParser.ListaColumnasContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_listaColumnas)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 242
            self.match(EvaParser.COR_IZQ)
            self.state = 243
            self.nombre()
            self.state = 248
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==57:
                self.state = 244
                self.match(EvaParser.COMA)
                self.state = 245
                self.nombre()
                self.state = 250
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 251
            self.match(EvaParser.COR_DER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpresionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return EvaParser.RULE_expresion

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ExprYContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def Y(self):
            return self.getToken(EvaParser.Y, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprY" ):
                return visitor.visitExprY(self)
            else:
                return visitor.visitChildren(self)


    class ExprAditivaContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def MAS(self):
            return self.getToken(EvaParser.MAS, 0)
        def MENOS(self):
            return self.getToken(EvaParser.MENOS, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprAditiva" ):
                return visitor.visitExprAditiva(self)
            else:
                return visitor.visitChildren(self)


    class ExprRelacionalContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def MENOR(self):
            return self.getToken(EvaParser.MENOR, 0)
        def MENOR_IGUAL(self):
            return self.getToken(EvaParser.MENOR_IGUAL, 0)
        def MAYOR(self):
            return self.getToken(EvaParser.MAYOR, 0)
        def MAYOR_IGUAL(self):
            return self.getToken(EvaParser.MAYOR_IGUAL, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprRelacional" ):
                return visitor.visitExprRelacional(self)
            else:
                return visitor.visitChildren(self)


    class ExprParentesisContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PAR_IZQ(self):
            return self.getToken(EvaParser.PAR_IZQ, 0)
        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)

        def PAR_DER(self):
            return self.getToken(EvaParser.PAR_DER, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprParentesis" ):
                return visitor.visitExprParentesis(self)
            else:
                return visitor.visitChildren(self)


    class ExprLiteralContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def literal(self):
            return self.getTypedRuleContext(EvaParser.LiteralContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprLiteral" ):
                return visitor.visitExprLiteral(self)
            else:
                return visitor.visitChildren(self)


    class ExprLlamadaContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(EvaParser.ID, 0)
        def PAR_IZQ(self):
            return self.getToken(EvaParser.PAR_IZQ, 0)
        def PAR_DER(self):
            return self.getToken(EvaParser.PAR_DER, 0)
        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(EvaParser.COMA)
            else:
                return self.getToken(EvaParser.COMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprLlamada" ):
                return visitor.visitExprLlamada(self)
            else:
                return visitor.visitChildren(self)


    class ExprNegativoContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def MENOS(self):
            return self.getToken(EvaParser.MENOS, 0)
        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprNegativo" ):
                return visitor.visitExprNegativo(self)
            else:
                return visitor.visitChildren(self)


    class ExprColumnaDeContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def nombre(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.NombreContext)
            else:
                return self.getTypedRuleContext(EvaParser.NombreContext,i)

        def PUNTO(self):
            return self.getToken(EvaParser.PUNTO, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprColumnaDe" ):
                return visitor.visitExprColumnaDe(self)
            else:
                return visitor.visitChildren(self)


    class ExprIgualdadContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def IGUAL_IGUAL(self):
            return self.getToken(EvaParser.IGUAL_IGUAL, 0)
        def DIFERENTE(self):
            return self.getToken(EvaParser.DIFERENTE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprIgualdad" ):
                return visitor.visitExprIgualdad(self)
            else:
                return visitor.visitChildren(self)


    class ExprPotenciaContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def POTENCIA(self):
            return self.getToken(EvaParser.POTENCIA, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprPotencia" ):
                return visitor.visitExprPotencia(self)
            else:
                return visitor.visitChildren(self)


    class ExprOContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def O(self):
            return self.getToken(EvaParser.O, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprO" ):
                return visitor.visitExprO(self)
            else:
                return visitor.visitChildren(self)


    class ExprNombreContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def nombre(self):
            return self.getTypedRuleContext(EvaParser.NombreContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprNombre" ):
                return visitor.visitExprNombre(self)
            else:
                return visitor.visitChildren(self)


    class ExprMultiplicativaContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expresion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvaParser.ExpresionContext)
            else:
                return self.getTypedRuleContext(EvaParser.ExpresionContext,i)

        def POR_OP(self):
            return self.getToken(EvaParser.POR_OP, 0)
        def DIV(self):
            return self.getToken(EvaParser.DIV, 0)
        def MODULO(self):
            return self.getToken(EvaParser.MODULO, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprMultiplicativa" ):
                return visitor.visitExprMultiplicativa(self)
            else:
                return visitor.visitChildren(self)


    class ExprNoContext(ExpresionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvaParser.ExpresionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NO(self):
            return self.getToken(EvaParser.NO, 0)
        def expresion(self):
            return self.getTypedRuleContext(EvaParser.ExpresionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExprNo" ):
                return visitor.visitExprNo(self)
            else:
                return visitor.visitChildren(self)



    def expresion(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = EvaParser.ExpresionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 38
        self.enterRecursionRule(localctx, 38, self.RULE_expresion, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 281
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                localctx = EvaParser.ExprParentesisContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 254
                self.match(EvaParser.PAR_IZQ)
                self.state = 255
                self.expresion(0)
                self.state = 256
                self.match(EvaParser.PAR_DER)
                pass

            elif la_ == 2:
                localctx = EvaParser.ExprLlamadaContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 258
                self.match(EvaParser.ID)
                self.state = 259
                self.match(EvaParser.PAR_IZQ)
                self.state = 268
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 32)) & ~0x3f) == 0 and ((1 << (_la - 32)) & 14764490767) != 0):
                    self.state = 260
                    self.expresion(0)
                    self.state = 265
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==57:
                        self.state = 261
                        self.match(EvaParser.COMA)
                        self.state = 262
                        self.expresion(0)
                        self.state = 267
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)



                self.state = 270
                self.match(EvaParser.PAR_DER)
                pass

            elif la_ == 3:
                localctx = EvaParser.ExprColumnaDeContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 271
                self.nombre()
                self.state = 272
                self.match(EvaParser.PUNTO)
                self.state = 273
                self.nombre()
                pass

            elif la_ == 4:
                localctx = EvaParser.ExprNegativoContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 275
                self.match(EvaParser.MENOS)
                self.state = 276
                self.expresion(10)
                pass

            elif la_ == 5:
                localctx = EvaParser.ExprNoContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 277
                self.match(EvaParser.NO)
                self.state = 278
                self.expresion(5)
                pass

            elif la_ == 6:
                localctx = EvaParser.ExprLiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 279
                self.literal()
                pass

            elif la_ == 7:
                localctx = EvaParser.ExprNombreContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 280
                self.nombre()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 306
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,27,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 304
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
                    if la_ == 1:
                        localctx = EvaParser.ExprPotenciaContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 283
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 284
                        self.match(EvaParser.POTENCIA)
                        self.state = 285
                        self.expresion(11)
                        pass

                    elif la_ == 2:
                        localctx = EvaParser.ExprMultiplicativaContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 286
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 287
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 985162418487296) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 288
                        self.expresion(10)
                        pass

                    elif la_ == 3:
                        localctx = EvaParser.ExprAditivaContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 289
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 290
                        _la = self._input.LA(1)
                        if not(_la==45 or _la==46):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 291
                        self.expresion(9)
                        pass

                    elif la_ == 4:
                        localctx = EvaParser.ExprRelacionalContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 292
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 293
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 16492674416640) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 294
                        self.expresion(8)
                        pass

                    elif la_ == 5:
                        localctx = EvaParser.ExprIgualdadContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 295
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 296
                        _la = self._input.LA(1)
                        if not(_la==38 or _la==39):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 297
                        self.expresion(7)
                        pass

                    elif la_ == 6:
                        localctx = EvaParser.ExprYContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 298
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 299
                        self.match(EvaParser.Y)
                        self.state = 300
                        self.expresion(5)
                        pass

                    elif la_ == 7:
                        localctx = EvaParser.ExprOContext(self, EvaParser.ExpresionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expresion)
                        self.state = 301
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 302
                        self.match(EvaParser.O)
                        self.state = 303
                        self.expresion(4)
                        pass

             
                self.state = 308
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,27,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENTERO(self):
            return self.getToken(EvaParser.ENTERO, 0)

        def REAL(self):
            return self.getToken(EvaParser.REAL, 0)

        def CADENA(self):
            return self.getToken(EvaParser.CADENA, 0)

        def VERDADERO(self):
            return self.getToken(EvaParser.VERDADERO, 0)

        def FALSO(self):
            return self.getToken(EvaParser.FALSO, 0)

        def NULO(self):
            return self.getToken(EvaParser.NULO, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_literal

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = EvaParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 309
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 8070450592377470976) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NombreContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(EvaParser.ID, 0)

        def ID_ESCAPADO(self):
            return self.getToken(EvaParser.ID_ESCAPADO, 0)

        def getRuleIndex(self):
            return EvaParser.RULE_nombre

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNombre" ):
                return visitor.visitNombre(self)
            else:
                return visitor.visitChildren(self)




    def nombre(self):

        localctx = EvaParser.NombreContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_nombre)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 311
            _la = self._input.LA(1)
            if not(_la==64 or _la==65):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[19] = self.expresion_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expresion_sempred(self, localctx:ExpresionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 11)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 3)
         




