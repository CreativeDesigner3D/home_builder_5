# hb_layouts — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Cada caso: cenário, comportamento legado, impacto e mitigação. Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Caminhos relativos a `blendertomob/`.

---

## EC-01 — Tamanho de papel desconhecido 🟢
- **Cenário:** `set_paper_size('A2')`.
- **Comportamento legado:** a resolução cai para LETTER, mas `scene['PAPER_SIZE']` grava `'A2'` (`hb_layouts.py:34-35,1398-1402`).
- **Impacto:** a cena diz A2 e renderiza em Letter; outras leituras (`get_paper_aspect_ratio`) seguem o mesmo fallback, mas a UI mostra A2.
- **Mitigação:** validar antes de gravar; incluir papéis ABNT (T-01).

## EC-02 — Resolução truncada 🟢
- **Cenário:** A4 paisagem a 150 DPI.
- **Comportamento legado:** `int(11,69 × 150) = 1753` (`hb_layouts.py:42`).
- **Impacto:** perda de até 1 px por eixo; escala impressa ligeiramente diferente da nominal.
- **Mitigação:** `round()`; aceitável para paridade.

## EC-03 — Conteúdo alto em papel paisagem 🟡
- **Cenário:** parede de 1,5 m de comprimento e 2,7 m de altura em LETTER paisagem.
- **Comportamento legado:** `ortho_scale = max(w, h)` é aplicado à maior dimensão do sensor (largura) e ignora o aspecto (`hb_layouts.py:1504-1578`).
- **Impacto:** topo/base do conteúdo cortados.
- **Mitigação:** T-11.

## EC-04 — `ElevationView.update` diverge da criação 🟢
- **Cenário:** mudar o comprimento da parede e atualizar a elevação.
- **Comportamento legado:** regra simplificada (y = −2, `max(L, H) + 0,4 m`), sem cotas e sem filhos (`hb_layouts.py:1780-1801`).
- **Impacto:** o quadro muda de enquadramento; cotas e gabinetes podem sair da página.
- **Mitigação:** T-12.

## EC-05 — Gabinete fora da faixa de 1,2 m 🟢
- **Cenário:** aéreo baixo instalado a 1,1 m, ou torre alta com origem no piso.
- **Comportamento legado:** o aéreo a 1,1 m é tratado como inferior (cota embaixo); a torre alta é inferior (cota embaixo) (`hb_layouts.py:1614`).
- **Impacto:** cotas no lugar inesperado.
- **Mitigação:** classificar pelo tipo do gabinete (base/alto/aéreo) quando disponível.

## EC-06 — Closets sem cotas automáticas 🟢
- **Cenário:** elevação de parede com closet.
- **Comportamento legado:** só cages FRAMELESS/FACE_FRAME são cotados; closets entram no conteúdo (R22) mas sem cota (`hb_layouts.py:1580-1634`).
- **Impacto:** prancha incompleta para o marceneiro.
- **Mitigação:** T-10 (Q-05).

## EC-07 — Gabinete neto da parede 🟢
- **Cenário:** gabinete dentro de um grupo ou filho de outro gabinete.
- **Comportamento legado:** só filhos **diretos** da parede são cotados.
- **Impacto:** gabinetes agrupados sem cota.
- **Mitigação:** percorrer descendentes até o primeiro cage.

## EC-08 — Planta ignora espessura e gabinetes 🟢
- **Cenário:** península que avança 1,2 m a partir da parede.
- **Comportamento legado:** bbox só pelos pontos inicial/final das paredes + 1 m (`hb_layouts.py:1840-1878`).
- **Impacto:** a península pode ficar parcialmente fora do quadro.
- **Mitigação:** T-14.

## EC-09 — `create_all_elevations` em arquivo com vários cômodos 🟡
- **Cenário:** arquivo com cozinha e banheiro.
- **Comportamento legado:** percorre `bpy.data.objects` e cria elevações das paredes de todos os cômodos (`hb_layouts.py:2998`).
- **Impacto:** pranchas duplicadas ou indesejadas.
- **Mitigação:** T-13.

## EC-10 — Excluir prancha 🟡
- **Cenário:** usuário exclui uma elevação.
- **Comportamento legado:** `LayoutView.delete` remove só a cena (`hb_layouts.py:1417-1424`).
- **Impacto:** collections `<cena>_*`, câmera, GP e cotas ficam órfãos; um nome de cena reaproveitado pode "herdar" collections antigas pelo nome.
- **Mitigação:** T-05.

## EC-11 — Renomear a cena de layout 🟡
- **Cenário:** usuário renomeia "Elevation 1" para "Parede Pia".
- **Comportamento legado:** `get_freestyle_collection` procura `<nome atual>_Freestyle_*` (`hb_layouts.py:1333-1349`).
- **Impacto:** as collections antigas não são encontradas; `add_to_freestyle_collection` falha e novas anotações não entram no roteamento.
- **Mitigação:** guardar referência às collections em IDProperty da cena em vez de depender do nome.

## EC-12 — Line Art sem `hb_layout_scale` 🟢
- **Cenário:** cena criada antes do registro das props de layout.
- **Comportamento legado:** fallback `1/4"=1'`; qualquer exceção → retorna calado (`hb_layouts.py:476-515`).
- **Impacto:** traço com espessura errada, sem mensagem.
- **Mitigação:** registrar o erro (T-07).

## EC-13 — Bake sem janela 🟢
- **Cenário:** bake chamado em `--background` ou de um timer.
- **Comportamento legado:** troca `bpy.context.window.scene` (try/finally) — sem janela, `AttributeError` (`hb_layouts.py:255-330`).
- **Impacto:** bake impossível em lote.
- **Mitigação:** avaliar pelo depsgraph da cena alvo sem trocar a janela.

## EC-14 — Vista baked e mudança de modelo 🟢
- **Cenário:** usuário assa o Line Art e depois altera o gabinete.
- **Comportamento legado:** modificadores desligados; a vista não acompanha; `set_line_art_visible` não religa (`hb_layouts.py:198-214`).
- **Impacto:** prancha desatualizada sem aviso.
- **Mitigação:** indicador visual "baked" + botão de desassar.

## EC-15 — Fonte Calibri ausente 🟡
- **Cenário:** Linux/macOS, ou Windows sem Office.
- **Comportamento legado:** `get_font` retorna `None` e é atribuído a `TextCurve.font` (`hb_layouts.py:44-48,1085`); nos rótulos, fallback para Bfont (`hb_details.py:329-349`).
- **Impacto:** possível exceção no carimbo; aparência diferente entre máquinas.
- **Mitigação:** T-22 (fonte embarcada).

## EC-16 — `TitleBlock.update` não faz nada 🟡
- **Cenário:** mudar a escala e atualizar o carimbo.
- **Comportamento legado:** procura nomes contendo `view_name`/`scale` em minúsculas; os campos são `..._Scale`; lista vazia em instâncias novas (`hb_layouts.py:1100-1107`).
- **Impacto:** carimbo com placeholders em inglês para sempre.
- **Mitigação:** T-20.

## EC-17 — Índice da biblioteca corrompido 🟢
- **Cenário:** `library_index.json` truncado por queda de energia.
- **Comportamento legado:** carrega índice vazio; a próxima gravação sobrescreve e "perde" todos os detalhes (os `.blend` continuam no disco) (`hb_detail_library.py:24-43`).
- **Impacto:** biblioteca aparentemente vazia.
- **Mitigação:** escrita atômica e reconstrução do índice varrendo os `.blend` (T-23).

## EC-18 — Nome de detalhe só com acentos/símbolos 🟢
- **Cenário:** nome "Ção ✓".
- **Comportamento legado:** vira `____<data>.blend` (`hb_detail_library.py:46-57`).
- **Impacto:** arquivos ilegíveis no disco (nome exibido preservado no índice).
- **Mitigação:** transliterar (unidecode simples) antes de sanitizar.

## EC-19 — Excluir detalhe inexistente 🟢
- **Cenário:** arquivo já apagado manualmente.
- **Comportamento legado:** remove do índice e retorna sucesso (`hb_detail_library.py:225-243`).
- **Impacto:** nenhum dano; mensagem enganosa.
- **Mitigação:** aviso distinto.

## EC-20 — `asset_poll(None)` 🟢
- **Cenário:** o Blender chama `asset_poll` com `None` (documentado em `bpy.types.AssetShelf.md#bpy.types.AssetShelf.asset_poll`).
- **Comportamento legado:** `asset.id_type` → `AttributeError` (`hb_assets.py:334-335`).
- **Impacto:** erro no console a cada redesenho da shelf.
- **Mitigação:** T-26.

## EC-21 — Recarregar a extensão 🟡
- **Cenário:** desativar/ativar em Preferências.
- **Comportamento legado:** `hasattr(bpy.types, 'HB_OT_add_asset_library')` é falso (nome RNA `HOME_BUILDER_OT_*`) → operadores não desregistrados; exceções engolidas (`hb_assets.py:408-428`).
- **Impacto:** operadores fantasmas/duplicados após recarga.
- **Mitigação:** T-26.

## EC-22 — Biblioteca do usuário com pasta apagada 🟡
- **Cenário:** o usuário apaga a pasta registrada.
- **Comportamento legado:** a `UserAssetLibrary` continua nas preferências; `get_all_subfolder_paths` só inclui subpastas existentes (`hb_assets.py:37-62`).
- **Impacto:** entrada inválida no navegador de assets.
- **Mitigação:** avisar e oferecer remoção no `refresh`.

## EC-23 — Multivista de objeto sem geometria 🟢
- **Cenário:** multivista de um empty ou de um cage vazio.
- **Comportamento legado:** bbox `(0, dimensions)` ou `(0, (1,1,1))` (`hb_layouts.py:2785-2840`).
- **Impacto:** prancha com quadro de 1 m sem conteúdo.
- **Mitigação:** bloquear o operador (`poll`) para objetos sem geometria.

## EC-24 — Operações de UI em `--background` 🟢
- **Cenário:** testes automatizados.
- **Comportamento legado:** `window.scene`, `context.screen.areas`, `bpy.ops.object.select_all` e `bpy.ops.grease_pencil.layer_mask_add` (este falha em silêncio) dependem de janela.
- **Impacto:** vistas não testáveis em CI.
- **Mitigação:** T-03, T-21, T-23.
