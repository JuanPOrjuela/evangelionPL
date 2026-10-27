// Gramatica de evangelionPL. Arriba van las reglas sintacticas (en minuscula)
// y abajo las lexicas (en mayuscula), todo en un solo archivo.
grammar Eva;

// Reglas sintacticas

// El EOF obliga a leer todo el archivo, asi no se cuela basura al final
programa : cabecera? sentencia* EOF ;

cabecera : NERV CADENA ;

sentencia
    : asignacion
    | mostrar
    | guardar
    | graficar
    | condicional
    | mientras
    | para
    | funcion
    | retornar
    | llamada
    ;

// lista[0] = 5 o datos["clave"] = 5 cambian un elemento por dentro
asignacion  : nombre indice* IGUAL flujo ;
indice      : COR_IZQ expresion COR_DER ;
mostrar     : MONITOR flujo ;
guardar     : SEELE flujo COMO CADENA ;
graficar    : HOLOGRAM ID DE flujo ( LLAVE_IZQ opcion* LLAVE_DER )? ;
// "sino si" encadena varias condiciones sin tener que anidar llaves
condicional : PATTERN_BLUE expresion bloque ( PATTERN_ORANGE ( condicional | bloque ) )? ;
mientras    : MIENTRAS expresion bloque ;
para        : PARA nombre ( EN expresion | DESDE expresion HASTA expresion ) bloque ;
// funcion promedio(a, b) { retornar (a + b) / 2 }
funcion     : FUNCION ID PAR_IZQ ( nombre ( COMA nombre )* )? PAR_DER bloque ;
retornar    : RETORNAR flujo ;
// una funcion que se llama sola, por ejemplo agregar(lista, 4)
llamada     : ID PAR_IZQ ( expresion ( COMA expresion )* )? PAR_DER ;
bloque      : LLAVE_IZQ sentencia* LLAVE_DER ;

// Un flujo es una fuente y despues las etapas que se le encadenan con |>
flujo  : fuente ( TUBERIA etapa )* ;
fuente : carga | expresion ;
carga  : ENTRY_PLUG CADENA ( CON LLAVE_IZQ opcion* LLAVE_DER )? ;
opcion : ID DOS_PUNTOS expresion COMA? ;

// Las etiquetas (#...) hacen que ANTLR genere un metodo visit por cada etapa
etapa
    : TARGET listaColumnas                                      # etapaSeleccionar
    | AT_FIELD DONDE expresion                                  # etapaFiltrar
    | SYNC columnaNueva ( COMA columnaNueva )*                  # etapaCrear
    | CODENAME COR_IZQ renombre ( COMA renombre )* COR_DER      # etapaRenombrar
    | FORMATION POR COR_IZQ criterio ( COMA criterio )* COR_DER # etapaOrdenar
    | EJECT DUPLICADOS listaColumnas?                           # etapaQuitarDuplicados
    | EJECT FALTANTES listaColumnas?                            # etapaQuitarFaltantes
    | EJECT COLUMNAS listaColumnas                              # etapaQuitarColumnas
    | DUMMY_PLUG columnaNueva ( COMA columnaNueva )*            # etapaRellenar
    | EQUIP nombre FLECHA ID                                    # etapaConvertir
    | SQUAD POR listaColumnas                                   # etapaAgrupar
    | MAGI agregacion ( COMA agregacion )*                      # etapaResumir
    | BATTERY ENTERO                                            # etapaLimitar
    | DIAGNOSTIC                                                # etapaDiagnostico
    ;

columnaNueva  : nombre IGUAL expresion ;
agregacion    : nombre IGUAL ID PAR_IZQ nombre? PAR_DER ;
renombre      : nombre FLECHA nombre ;
criterio      : nombre ( ASC | DESC )? ;
listaColumnas : COR_IZQ nombre ( COMA nombre )* COR_DER ;

// La precedencia sale del orden: la alternativa de mas arriba amarra mas fuerte
expresion
    : PAR_IZQ expresion PAR_DER                                         # exprParentesis
    | ID PAR_IZQ ( expresion ( COMA expresion )* )? PAR_DER             # exprLlamada
    | nombre PUNTO nombre                                               # exprColumnaDe
    | expresion COR_IZQ expresion COR_DER                               # exprIndice
    | <assoc=right> expresion POTENCIA expresion                        # exprPotencia
    | MENOS expresion                                                   # exprNegativo
    | expresion ( POR_OP | DIV | MODULO ) expresion                     # exprMultiplicativa
    | expresion ( MAS | MENOS ) expresion                               # exprAditiva
    | expresion ( MENOR | MENOR_IGUAL | MAYOR | MAYOR_IGUAL ) expresion # exprRelacional
    | expresion ( IGUAL_IGUAL | DIFERENTE ) expresion                   # exprIgualdad
    | NO expresion                                                      # exprNo
    | expresion Y expresion                                             # exprY
    | expresion O expresion                                             # exprO
    | COR_IZQ ( expresion ( COMA expresion )* COMA? )? COR_DER           # exprLista
    | LLAVE_IZQ ( par ( COMA par )* COMA? )? LLAVE_DER                   # exprDiccionario
    | literal                                                           # exprLiteral
    | nombre                                                            # exprNombre
    ;

par     : ( CADENA | nombre ) DOS_PUNTOS expresion ;

literal : ENTERO | REAL | CADENA | VERDADERO | FALSO | NULO ;

nombre : ID | ID_ESCAPADO ;

// Reglas lexicas 

// --- Instrucciones (van antes que ID para que ganen el empate) ---
// Cada una se puede escribir con su nombre de Evangelion o con una palabra en espanol
NERV           : 'NERV' | 'programa' ;
ENTRY_PLUG     : 'ENTRY_PLUG' | 'cargar' ;
MONITOR        : 'MONITOR' | 'mostrar' ;
SEELE          : 'SEELE' | 'guardar' ;
HOLOGRAM       : 'HOLOGRAM' | 'graficar' ;
PATTERN_BLUE   : 'PATTERN_BLUE' | 'si' ;
PATTERN_ORANGE : 'PATTERN_ORANGE' | 'sino' ;

// --- Etapas del flujo ---
TARGET     : 'TARGET' | 'seleccionar' ;
AT_FIELD   : 'AT_FIELD' | 'filtrar' ;
SYNC       : 'SYNC' | 'crear' ;
CODENAME   : 'CODENAME' | 'renombrar' ;
FORMATION  : 'FORMATION' | 'ordenar' ;
EJECT      : 'EJECT' | 'quitar' ;
DUMMY_PLUG : 'DUMMY_PLUG' | 'rellenar' ;
EQUIP      : 'EQUIP' | 'convertir' ;
SQUAD      : 'SQUAD' | 'agrupar' ;
MAGI       : 'MAGI' | 'resumir' ;
BATTERY    : 'BATTERY' | 'limitar' ;
DIAGNOSTIC : 'DIAGNOSTIC' | 'diagnosticar' ;

// --- Funciones ---
FUNCION    : 'funcion' ;
RETORNAR   : 'retornar' ;

// --- Ciclos ---
MIENTRAS   : 'mientras' ;
PARA       : 'para' ;
EN         : 'en' ;
DESDE      : 'desde' ;
HASTA      : 'hasta' ;

// --- Conectores ---
DONDE      : 'donde' ;
POR        : 'por' ;
COMO       : 'como' ;
CON        : 'con' ;
DE         : 'de' ;
ASC        : 'asc' ;
DESC       : 'desc' ;
DUPLICADOS : 'duplicados' ;
FALTANTES  : 'faltantes' ;
COLUMNAS   : 'columnas' ;

// --- Operadores logicos y literales fijos ---
Y         : 'y' ;
O         : 'o' ;
NO        : 'no' ;
VERDADERO : 'verdadero' ;
FALSO     : 'falso' ;
NULO      : 'nulo' ;

// --- Operadores y signos ---
TUBERIA     : '|>' ;
FLECHA      : '->' ;
IGUAL_IGUAL : '==' ;
DIFERENTE   : '!=' ;
MENOR_IGUAL : '<=' ;
MAYOR_IGUAL : '>=' ;
MENOR       : '<' ;
MAYOR       : '>' ;
IGUAL       : '=' ;
MAS         : '+' ;
MENOS       : '-' ;
POR_OP      : '*' ;
DIV         : '/' ;
MODULO      : '%' ;
POTENCIA    : '^' ;
PAR_IZQ     : '(' ;
PAR_DER     : ')' ;
COR_IZQ     : '[' ;
COR_DER     : ']' ;
LLAVE_IZQ   : '{' ;
LLAVE_DER   : '}' ;
COMA        : ',' ;
DOS_PUNTOS  : ':' ;
PUNTO       : '.' ;

// --- Literales ---
// REAL va primero, si no 3.5 se partiria en 3 . 5
REAL   : DIGITO+ '.' DIGITO+ ;
ENTERO : DIGITO+ ;
CADENA : '"' ( ESCAPE | ~["\\\r\n] )* '"' ;

// Si falta la comilla de cierre cae aqui y lo reportamos como error lexico
CADENA_SIN_CERRAR : '"' ( ESCAPE | ~["\\\r\n] )* ;

// --- Identificadores ---
ID : LETRA ( LETRA | DIGITO | '_' )* ;

// Para columnas con espacios o que se llaman igual que una reservada: `Tipo de EVA`
ID_ESCAPADO : '`' ~[`\r\n]+ '`' ;

// --- Lo que el parser no necesita ver ---
COMENTARIO : '#' ~[\r\n]* -> skip ;
ESPACIOS   : [ \t\r\n]+ -> skip ;

// Cualquier otro caracter es un error lexico
CARACTER_INVALIDO : . ;

fragment DIGITO : [0-9] ;
fragment LETRA  : [a-zA-Z_áéíóúñÁÉÍÓÚÑ] ;
fragment ESCAPE : '\\' ["\\nt] ;
