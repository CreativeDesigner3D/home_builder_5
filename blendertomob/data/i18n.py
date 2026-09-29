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
    }
}


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
