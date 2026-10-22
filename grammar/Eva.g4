// Gramatica de evangelionPL. Arriba van las reglas sintacticas (en minuscula)
// y abajo las lexicas (en mayuscula), todo en un solo archivo.
grammar Eva;

// ============================ Reglas sintacticas ============================

// El EOF obliga a leer todo el archivo, asi no se cuela basura al final
programa : cabecera? sentencia* EOF ;

cabecera : NERV CADENA ;

sentencia
    : asignacion
    | mostrar
    | guardar
    | graficar
    | condicional
    ;

asignacion  : nombre IGUAL flujo ;
mostrar     : MONITOR flujo ;
guardar     : SEELE flujo COMO CADENA ;
graficar    : HOLOGRAM ID DE flujo ( LLAVE_IZQ opcion* LLAVE_DER )? ;
condicional : PATTERN_BLUE expresion bloque ( PATTERN_ORANGE bloque )? ;
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
    | PROFECIA nombre POR listaColumnas VECINOS ENTERO          # etapaProfecia
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
    | <assoc=right> expresion POTENCIA expresion                        # exprPotencia
    | MENOS expresion                                                   # exprNegativo
    | expresion ( POR_OP | DIV | MODULO ) expresion                     # exprMultiplicativa
    | expresion ( MAS | MENOS ) expresion                               # exprAditiva
    | expresion ( MENOR | MENOR_IGUAL | MAYOR | MAYOR_IGUAL ) expresion # exprRelacional
    | expresion ( IGUAL_IGUAL | DIFERENTE ) expresion                   # exprIgualdad
    | NO expresion                                                      # exprNo
    | expresion Y expresion                                             # exprY
    | expresion O expresion                                             # exprO
    | literal                                                           # exprLiteral
    | nombre                                                            # exprNombre
    ;

literal : ENTERO | REAL | CADENA | VERDADERO | FALSO | NULO ;

nombre : ID | ID_ESCAPADO ;

// ============================== Reglas lexicas ==============================

// --- Instrucciones (van antes que ID para que ganen el empate) ---
NERV           : 'NERV' ;
ENTRY_PLUG     : 'ENTRY_PLUG' ;
MONITOR        : 'MONITOR' ;
SEELE          : 'SEELE' ;
HOLOGRAM       : 'HOLOGRAM' ;
PATTERN_BLUE   : 'PATTERN_BLUE' ;
PATTERN_ORANGE : 'PATTERN_ORANGE' ;

// --- Etapas del flujo ---
TARGET     : 'TARGET' ;
AT_FIELD   : 'AT_FIELD' ;
SYNC       : 'SYNC' ;
CODENAME   : 'CODENAME' ;
FORMATION  : 'FORMATION' ;
EJECT      : 'EJECT' ;
DUMMY_PLUG : 'DUMMY_PLUG' ;
EQUIP      : 'EQUIP' ;
SQUAD      : 'SQUAD' ;
MAGI       : 'MAGI' ;
BATTERY    : 'BATTERY' ;
DIAGNOSTIC : 'DIAGNOSTIC' ;
PROFECIA   : 'PROFECIA' ;

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
VECINOS    : 'vecinos' ;

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
