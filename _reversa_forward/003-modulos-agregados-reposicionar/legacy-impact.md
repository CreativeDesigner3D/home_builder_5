# Legacy impact — 003-modulos-agregados-reposicionar

> Gerado por `/reversa-coding` em 2026-10-07 (rodada única: T001–T071, todas concluídas).
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md` e as specs por unidade em `_reversa_sdd/<unidade>/`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/customize/` (spec, manifest, props, adapters/*, reapply, library_io, ops_customize, ops_library, panels) | Personalização de módulo (novo) | componente-novo | MEDIUM | Bloco A da feature: personalização por instância nas quatro bibliotecas e biblioteca de módulos do usuário (D-01 a D-11) |
| `caffmob_draw/aggregates/` (limits, sweep, props, convert, apply, perforate, production, leaf, collision, overlay, ops_import, ops_aggregate, panels) | Agregados e folhas (novo) | componente-novo | MEDIUM | Blocos B e folha de porta (D-12 a D-20) |
| `caffmob_draw/product_libraries/frameless/types_frameless.py` | Frameless (interiores) | regra-nova | MEDIUM | `_add_rollouts_to_section` deixou de ser `TODO`: gavetas internas empilhadas na seção (D-09) |
| `caffmob_draw/product_libraries/frameless/operators/ops_opening.py`, `operators/ops_styles.py`, `props_hb_frameless.py` | Frameless (frentes e estilos) | regra-alterada | MEDIUM | Fim de `change_opening_type`, `update_cabinet_materials` e `assign_style_to_cabinet` chama `customize.reapply.after_rebuild` (D-04) |
| `caffmob_draw/product_libraries/face_frame/types_face_frame.py` | Face frame (recálculo) | regra-alterada | MEDIUM | `recalculate_face_frame_cabinet` reaplica a personalização depois de `_reapply_cabinet_style` (D-04) |
| `caffmob_draw/product_libraries/closets/types_closets.py` | Closets (recálculo) | regra-alterada | MEDIUM | `recalculate_closet_starter` reaplica a personalização no fim (D-04) |
| `caffmob_draw/geometry/mesh_gen.py`, `geometry/door_controller.py`, `data/properties.py` | Módulo paramétrico `btm` | regra-alterada / delta-de-dados | LOW | Prateleiras na malha (`btm_cabinet.shelves`), índices de material por grupo, puxador e material nas portas |
| `caffmob_draw/cutting/machining.py`, `cutting/part_sources.py`, `cutting/nesting.py`, `cutting/part_extractor.py`, `cutting/json_exporter.py` | Plano de corte / JSON de produção | delta-de-contrato-externo | HIGH | JSON `2.0.0` → `2.1.0` com `machining` por peça; agregados "peça de produção" entram como `FREE_GEOMETRY`; leitor aceita 2.0 e 2.1 |
| `caffmob_draw/inspection/pivot_math.py`, `inspection/fronts.py`, `inspection/adapters/aggregate_leaf.py` | Inspeção de frentes (001) | regra-alterada | MEDIUM | `clamp_angle`/`edge_rotation`/`pose_for` aceitam `maximum` (padrão 90° preservado); novo adaptador de folhas convertidas |
| `caffmob_draw/move_over/` (props, scene, ops_dialog, reposition, ops_substitute, insertion_plane, `__init__`) | Mover Sobre (002) | regra-alterada | MEDIUM | Rotação, passo, relativa/absoluta, posições salvas, Substituir e plano de inserção (D-21 a D-24) |
| `caffmob_draw/hb_snap.py` | Posicionamento (snap à grade) | regra-alterada | MEDIUM | Sem acerto em objeto, o ponto cai no plano de inserção ativo em vez de Z = 0 (D-24) |
| `caffmob_draw/ui/object_properties.py`, `ui/save_feedback.py`, `ui/__init__.py` | Interface | regra-nova | LOW | Subpainéis Arranjo/Movimentação/Dimensões e limites; aviso de projeto salvo e falha ao salvar (D-25, D-27) |
| `caffmob_draw/compat.py` | Compatibilidade | regra-nova | LOW | `try_set_gn_input` |
| `caffmob_draw/__init__.py` | Registro | regra-alterada | LOW | Registra/desregistra `customize` e `aggregates` |
| `tests/test_production_contracts.py`, `tests/blender_smoke.py`, `tests/blender_increment1_smoke.py` | Testes legados | regra-alterada | LOW | Versão esperada do JSON passou a 2.1.0; novos testes de 2.0 aceito e de `machining` |

## Diff conceitual por componente

**Personalização de módulo (novo).** Um módulo inserido pode ter frente, estilo, puxador e material por vão, materiais
por grupo e por peça e divisões internas próprias. O pedido fica em `Object.btm_custom` no vão (que sobrevive à
reconstrução das frentes) e um adaptador por biblioteca aplica pela própria biblioteca. "Salvar como módulo" grava
`.blend` + manifesto JSON + miniatura em `modules/<categoria>/`, com estilos, materiais e puxadores por nome.

**Frameless.** Ganhou gavetas internas reais e o gancho de reaplicação no fim das operações que recriam frentes ou
reatribuem materiais. O estilo por índice (RN-29) continua valendo para quem não personaliza; o módulo personalizado
resolve o estilo pelo nome no momento de aplicar.

**Face frame e closets.** O recálculo central passou a terminar com a reaplicação da personalização, só quando o
módulo tem personalização (custo zero nos demais).

**Módulo paramétrico (`btm`).** A malha ganhou prateleiras e índices de material (caixa 0, prateleiras 1, fundo 2);
as portas ganham puxador como filho e material.

**Plano de corte.** Contrato do JSON de produção na versão 2.1.0: `machining` por peça com os recortes de agregados
marcados como "Furo real no plano de corte" (lidos dos `CPM_CUTOUT` "Agregado: *"). `drilling` continua vazio.

**Inspeção (001).** O máximo de 90° continua sendo a regra comum dos módulos; folhas convertidas usam o próprio máximo
(até 180°) e entram em "Abrir/Fechar Frentes", na verificação de interferência e no salvar fechado.

**Mover Sobre (002).** Mesma janela, com os recursos do Reposicionar do Promob.

**Posicionamento.** O plano de inserção, quando ativo, substitui o piso Z = 0 no snap à grade.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- R-01 (piso só com paredes), R-02 (piso conformal por fecho convexo), R-03 (sentido das paredes).
- R-04 a R-08 (aberturas presas à parede, movimento constrangido, limites, transição entre segmentos, peitoril).
- R-09 e R-10 (nesting por área e corte guilhotinado).

Outras regras 🟢 de specs por unidade preservadas:
- `_reversa_sdd/frameless/requirements.md` RN-25 (porta 5 peças com tamanho mínimo; abaixo dele a mensagem é repassada ao usuário).
- `_reversa_sdd/frameless/requirements.md` RN-29 (estilo vinculado por índice) para módulos sem personalização.
- Operadores de grupo de gabinetes (`save_cabinet_group_to_user_library` / `load_cabinet_group_from_library`) e a pasta `cabinet_groups/`, sem mudança.

## Modificadas

| Regra 🟢 | Origem | Como fica |
|---|---|---|
| Biblioteca do usuário só para grupos de gabinetes (frameless/face frame) | `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-44) | Continua; além dela, qualquer módulo das quatro bibliotecas pode ser salvo em `modules/` com manifesto e reaplicação |
| Ponto sem acerto cai no plano Z = 0 | `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-04) | Cai no plano de inserção quando ativo; Z = 0 só sem plano |
| Abertura de frentes limitada a 90° em todas as linhas | `_reversa_forward/001-addon-moveis-planejados/roadmap.md` (D-20) | Continua para módulos; folhas convertidas têm máximo próprio |
| JSON de produção v2.0.0 com `drilling: []` | `cutting/json_exporter.py` (contrato da 001/002) | v2.1.0 com `machining` por peça; leitor aceita 2.0 |
| Recálculo de face frame/closets e troca de vão/estilo do frameless | `_reversa_sdd/face_frame/`, `_reversa_sdd/closets/`, `_reversa_sdd/frameless/requirements.md#Requisitos Funcionais` (RF-09, RF-20) | Terminam reaplicando a personalização gravada no módulo |
