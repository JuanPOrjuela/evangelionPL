# Generated from Eva.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .EvaParser import EvaParser
else:
    from EvaParser import EvaParser

# This class defines a complete generic visitor for a parse tree produced by EvaParser.

class EvaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by EvaParser#programa.
    def visitPrograma(self, ctx:EvaParser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#cabecera.
    def visitCabecera(self, ctx:EvaParser.CabeceraContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#sentencia.
    def visitSentencia(self, ctx:EvaParser.SentenciaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#asignacion.
    def visitAsignacion(self, ctx:EvaParser.AsignacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#indice.
    def visitIndice(self, ctx:EvaParser.IndiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#mostrar.
    def visitMostrar(self, ctx:EvaParser.MostrarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#guardar.
    def visitGuardar(self, ctx:EvaParser.GuardarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#graficar.
    def visitGraficar(self, ctx:EvaParser.GraficarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#condicional.
    def visitCondicional(self, ctx:EvaParser.CondicionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#mientras.
    def visitMientras(self, ctx:EvaParser.MientrasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#para.
    def visitPara(self, ctx:EvaParser.ParaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#llamada.
    def visitLlamada(self, ctx:EvaParser.LlamadaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#bloque.
    def visitBloque(self, ctx:EvaParser.BloqueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#flujo.
    def visitFlujo(self, ctx:EvaParser.FlujoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#fuente.
    def visitFuente(self, ctx:EvaParser.FuenteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#carga.
    def visitCarga(self, ctx:EvaParser.CargaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#opcion.
    def visitOpcion(self, ctx:EvaParser.OpcionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaSeleccionar.
    def visitEtapaSeleccionar(self, ctx:EvaParser.EtapaSeleccionarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaFiltrar.
    def visitEtapaFiltrar(self, ctx:EvaParser.EtapaFiltrarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaCrear.
    def visitEtapaCrear(self, ctx:EvaParser.EtapaCrearContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaRenombrar.
    def visitEtapaRenombrar(self, ctx:EvaParser.EtapaRenombrarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaOrdenar.
    def visitEtapaOrdenar(self, ctx:EvaParser.EtapaOrdenarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaQuitarDuplicados.
    def visitEtapaQuitarDuplicados(self, ctx:EvaParser.EtapaQuitarDuplicadosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaQuitarFaltantes.
    def visitEtapaQuitarFaltantes(self, ctx:EvaParser.EtapaQuitarFaltantesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaQuitarColumnas.
    def visitEtapaQuitarColumnas(self, ctx:EvaParser.EtapaQuitarColumnasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaRellenar.
    def visitEtapaRellenar(self, ctx:EvaParser.EtapaRellenarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaConvertir.
    def visitEtapaConvertir(self, ctx:EvaParser.EtapaConvertirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaAgrupar.
    def visitEtapaAgrupar(self, ctx:EvaParser.EtapaAgruparContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaResumir.
    def visitEtapaResumir(self, ctx:EvaParser.EtapaResumirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaLimitar.
    def visitEtapaLimitar(self, ctx:EvaParser.EtapaLimitarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#etapaDiagnostico.
    def visitEtapaDiagnostico(self, ctx:EvaParser.EtapaDiagnosticoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#columnaNueva.
    def visitColumnaNueva(self, ctx:EvaParser.ColumnaNuevaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#agregacion.
    def visitAgregacion(self, ctx:EvaParser.AgregacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#renombre.
    def visitRenombre(self, ctx:EvaParser.RenombreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#criterio.
    def visitCriterio(self, ctx:EvaParser.CriterioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#listaColumnas.
    def visitListaColumnas(self, ctx:EvaParser.ListaColumnasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprLista.
    def visitExprLista(self, ctx:EvaParser.ExprListaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprY.
    def visitExprY(self, ctx:EvaParser.ExprYContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprAditiva.
    def visitExprAditiva(self, ctx:EvaParser.ExprAditivaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprRelacional.
    def visitExprRelacional(self, ctx:EvaParser.ExprRelacionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprIndice.
    def visitExprIndice(self, ctx:EvaParser.ExprIndiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprParentesis.
    def visitExprParentesis(self, ctx:EvaParser.ExprParentesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprLiteral.
    def visitExprLiteral(self, ctx:EvaParser.ExprLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprLlamada.
    def visitExprLlamada(self, ctx:EvaParser.ExprLlamadaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprDiccionario.
    def visitExprDiccionario(self, ctx:EvaParser.ExprDiccionarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprNegativo.
    def visitExprNegativo(self, ctx:EvaParser.ExprNegativoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprColumnaDe.
    def visitExprColumnaDe(self, ctx:EvaParser.ExprColumnaDeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprIgualdad.
    def visitExprIgualdad(self, ctx:EvaParser.ExprIgualdadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprPotencia.
    def visitExprPotencia(self, ctx:EvaParser.ExprPotenciaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprO.
    def visitExprO(self, ctx:EvaParser.ExprOContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprNombre.
    def visitExprNombre(self, ctx:EvaParser.ExprNombreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprMultiplicativa.
    def visitExprMultiplicativa(self, ctx:EvaParser.ExprMultiplicativaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#exprNo.
    def visitExprNo(self, ctx:EvaParser.ExprNoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#par.
    def visitPar(self, ctx:EvaParser.ParContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#literal.
    def visitLiteral(self, ctx:EvaParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvaParser#nombre.
    def visitNombre(self, ctx:EvaParser.NombreContext):
        return self.visitChildren(ctx)



del EvaParser