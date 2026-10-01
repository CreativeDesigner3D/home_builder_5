"""
BlenderToMob Internationalization & Localization (i18n)
Dicionário de traduções oficial (Português do Brasil pt_BR e Inglês en_US)
"""

import bpy  # type: ignore

translations_dict = {
    "pt_BR": {
        ("*", "Construir Parede"): "Construir Parede",
        ("*", "Inserir Abertura"): "Inserir Abertura",
        ("*", "Remover Abertura"): "Remover Abertura",
        ("*", "Inserir Armário"): "Inserir Armário",
        ("*", "Módulo Rápido"): "Módulo Rápido",
        ("*", "Largura"): "Largura",
        ("*", "Altura"): "Altura",
        ("*", "Profundidade"): "Profundidade",
        ("*", "Espessura"): "Espessura",
        ("*", "Espessura MDF"): "Espessura MDF",
        ("*", "Espessura Chapas"): "Espessura Chapas",
        ("*", "Comprimento"): "Comprimento",
        ("*", "Afastamento"): "Afastamento",
        ("*", "Flecha"): "Flecha",
        ("*", "Peitoril"): "Peitoril",
        ("*", "Porta"): "Porta",
        ("*", "Janela"): "Janela",
        ("*", "Basculante"): "Basculante",
        ("*", "Configurações"): "Configurações",
        ("*", "Piso"): "Piso",
        ("*", "Módulos"): "Módulos",
        ("*", "Calcular Plano de Corte"): "Calcular Plano de Corte",
        ("*", "Exportar Plano de Corte (JSON)"): "Exportar Plano de Corte (JSON)",
        ("*", "Plano de Corte (Nesting)"): "Plano de Corte (Nesting)",
        ("*", "Abertura Porta"): "Abertura Porta",
        ("*", "Sentido Abertura"): "Sentido Abertura",
        ("*", "Configurador de Dimensões"): "Configurador de Dimensões",
        ("*", "Configurações de Dimensões"): "Configurações de Dimensões",
        ("*", "Material"): "Material",
        ("*", "Largura Máxima da Chapa"): "Largura Máxima da Chapa",
        ("*", "Comprimento Máximo da Chapa"): "Comprimento Máximo da Chapa",
        ("*", "Espessura da Chapa"): "Espessura da Chapa",
        ("*", "Fita Borda 1 (Superior)"): "Fita Borda 1 (Superior)",
        ("*", "Fita Borda 2 (Inferior)"): "Fita Borda 2 (Inferior)",
        ("*", "Fita Borda 3 (Direita/Traseira)"): "Fita Borda 3 (Direita/Traseira)",
        ("*", "Fita Borda 4 (Esquerda/Frontal)"): "Fita Borda 4 (Esquerda/Frontal)",
        ("*", "Refilo Superior"): "Refilo Superior",
        ("*", "Refilo Inferior"): "Refilo Inferior",
        ("*", "Refilo Esquerdo"): "Refilo Esquerdo",
        ("*", "Refilo Direito"): "Refilo Direito",
        ("*", "Espessura da Serra (Kerf)"): "Espessura da Serra (Kerf)",
        ("*", "Respeitar Veio da Madeira"): "Respeitar Veio da Madeira",
        ("*", "Permitir Rotação"): "Permitir Rotação",
        ("*", "Altura do Rodapé / Base"): "Altura do Rodapé / Base",
        ("*", "Folga entre Portas"): "Folga entre Portas",
        ("*", "Recuo do Fundo"): "Recuo do Fundo",
        ("*", "Profundidade do Canal"): "Profundidade do Canal",
    },
    "en_US": {
        ("*", "Construir Parede"): "Build Wall",
        ("*", "Inserir Abertura"): "Insert Opening",
        ("*", "Remover Abertura"): "Remove Opening",
        ("*", "Inserir Armário"): "Insert Cabinet",
        ("*", "Módulo Rápido"): "Quick Cabinet",
        ("*", "Largura"): "Width",
        ("*", "Altura"): "Height",
        ("*", "Profundidade"): "Depth",
        ("*", "Espessura"): "Thickness",
        ("*", "Espessura MDF"): "MDF Thickness",
        ("*", "Espessura Chapas"): "Panel Thickness",
        ("*", "Comprimento"): "Length",
        ("*", "Afastamento"): "Offset",
        ("*", "Flecha"): "Sagitta",
        ("*", "Peitoril"): "Sill Height",
        ("*", "Porta"): "Door",
        ("*", "Janela"): "Window",
        ("*", "Basculante"): "Flip Up",
        ("*", "Configurações"): "Settings",
        ("*", "Piso"): "Floor",
        ("*", "Módulos"): "Modules",
        ("*", "Calcular Plano de Corte"): "Calculate Cut Plan",
        ("*", "Exportar Plano de Corte (JSON)"): "Export Cut Plan (JSON)",
        ("*", "Plano de Corte (Nesting)"): "Cut Plan (Nesting)",
        ("*", "Abertura Porta"): "Door Opening",
        ("*", "Sentido Abertura"): "Swing Direction",
        ("*", "Configurador de Dimensões"): "Dimension Configurator",
        ("*", "Configurações de Dimensões"): "Dimension Settings",
        ("*", "Material"): "Material",
        ("*", "Largura Máxima da Chapa"): "Max Sheet Width",
        ("*", "Comprimento Máximo da Chapa"): "Max Sheet Length",
        ("*", "Espessura da Chapa"): "Sheet Thickness",
        ("*", "Fita Borda 1 (Superior)"): "Edge Band 1 (Top)",
        ("*", "Fita Borda 2 (Inferior)"): "Edge Band 2 (Bottom)",
        ("*", "Fita Borda 3 (Direita/Traseira)"): "Edge Band 3 (Right/Back)",
        ("*", "Fita Borda 4 (Esquerda/Frontal)"): "Edge Band 4 (Left/Front)",
        ("*", "Refilo Superior"): "Top Margin (Trim)",
        ("*", "Refilo Inferior"): "Bottom Margin (Trim)",
        ("*", "Refilo Esquerdo"): "Left Margin (Trim)",
        ("*", "Refilo Direito"): "Right Margin (Trim)",
        ("*", "Espessura da Serra (Kerf)"): "Saw Blade Kerf",
        ("*", "Respeitar Veio da Madeira"): "Respect Wood Grain",
        ("*", "Permitir Rotação"): "Allow Part Rotation",
        ("*", "Altura do Rodapé / Base"): "Base / Plinth Height",
        ("*", "Folga entre Portas"): "Door Clearance Gap",
        ("*", "Recuo do Fundo"): "Back Panel Inset",
        ("*", "Profundidade do Canal"): "Groove Depth",
        # Padrão de Dimensões / Configurador (T044)
        ("*", "Padrão de Dimensões"): "Dimension Standard",
        ("*", "Abrir Configurador de Dimensões"): "Open Dimension Configurator",
        ("*", "Config. Dimensões"): "Dimension Settings",
        ("*", "Aplicar Padrão de Dimensões"): "Apply Dimension Standard",
        ("*", "Definir Definição Ativa"): "Set Active Definition",
        ("*", "Definir e aplicar"): "Set and Apply",
        ("*", "Duplicar Definição"): "Duplicate Definition",
        ("*", "Duplicar para editar"): "Duplicate to Edit",
        ("*", "Renomear Definição"): "Rename Definition",
        ("*", "Excluir Definição"): "Delete Definition",
        ("*", "Exportar Definição (JSON)"): "Export Definition (JSON)",
        ("*", "Importar Definição (JSON)"): "Import Definition (JSON)",
        ("*", "Importar do Promob"): "Import from Promob",
        ("*", "Exportar para o Promob"): "Export to Promob",
        ("*", "Exportar p/ Promob"): "Export to Promob",
        ("*", "Relatório do Padrão de Dimensões"): "Dimension Standard Report",
        ("*", "Incluir medidas manuais"): "Include Manual Measurements",
        ("*", "Definição"): "Definition",
        ("*", "Nome"): "Name",
        ("*", "Buscar"): "Search",
        ("*", "Valor"): "Value",
        ("*", "Aplicar"): "Apply",
        ("*", "Fechar"): "Close",
        ("*", "Importar"): "Import",
        ("*", "Exportar"): "Export",
        ("*", "Medidas Máximas"): "Maximum Measurements",
        ("*", "Dimensões Externas"): "External Dimensions",
        ("*", "Chapas"): "Sheets",
        ("*", "Componentes"): "Components",
        ("*", "Nenhuma alteração pendente."): "No pending changes.",
        ("*", "Selecione um parâmetro na árvore."): "Select a parameter in the tree.",
        ("*", "Imagem de referência indisponível."): "Reference image unavailable.",
        # Lista de peças e plano de corte (T044)
        ("*", "Lista de Peças e Plano de Corte"): "Parts List and Cut Plan",
        ("*", "Exportar JSON Global"): "Export Global JSON",
        ("*", "Importar JSON Global"): "Import Global JSON",
        ("*", "Exportar Peças (CSV)"): "Export Parts (CSV)",
        ("*", "Incluir dados do cliente"): "Include Client Data",
        ("*", "Incluir Dados do Cliente"): "Include Client Data",
        ("*", "Incluir plano de corte"): "Include Cut Plan",
        ("*", "Plano de Corte Desatualizado"): "Cut Plan Out of Date",
        ("*", "O projeto mudou: recalcule o plano de corte."): "The project changed: recalculate the cut plan.",
        ("*", "Nenhuma otimização calculada."): "No optimization calculated.",
        ("*", "Otimizador de Chapas MDF"): "MDF Sheet Optimizer",
    }
}


def _schema_translations():
    """Rótulos do esquema do Padrão de Dimensões (label_pt → label_en), gerados do próprio esquema."""
    from . import dimension_schema as schema
    entries = {}
    for param in schema.PARAMS.values():
        entries[("*", param.label_pt)] = param.label_en
    for comp in schema.COMPONENTS:
        entries[("*", comp.label_pt)] = comp.label_en
    for _code, pt, en in schema.LINES:
        entries[("*", pt)] = en
    return entries


for _key, _value in _schema_translations().items():
    translations_dict["en_US"].setdefault(_key, _value)


def register():
    try:
        bpy.app.translations.register(__name__, translations_dict)
    except Exception:
        pass


def unregister():
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
