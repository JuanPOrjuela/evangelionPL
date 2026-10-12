// Lexer de evangelionPL: convierte el texto en tokens.
lexer grammar EvaLexer;

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
