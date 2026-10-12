// Parser de evangelionPL: arma el arbol a partir de los tokens.
parser grammar EvaParser;

options { tokenVocab = EvaLexer; }

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
