# Compatibilidade Blender 5.x no CAFFMob Draw

O que mudou na API e afeta (ou pode afetar) este código. Fonte primária: `corpus/change_log.md` (cobre **5.1 → 5.2**)
e as notas das próprias páginas da referência. Mudanças anteriores ao 5.1 não estão no changelog do zip;
quando citadas aqui, a fonte é indicada.

## Como checar automaticamente

```bash
python3 docs/rag/tools/check_api.py            # varre caffmob_draw/, sai com código 1 se houver referência inexistente no 5.2
python3 docs/rag/tools/check_api.py arquivo.py # só um arquivo
```

Detecta: `bpy.types.X.attr`, `bpy.ops.mod.op`, `bmesh.ops.*`, `gpu.*`, `blf.*`, `mathutils.*`, `bpy_extras.*` escritos por extenso
e nomes em `gpu.shader.from_builtin('...')`. Ignora operadores/classes/propriedades definidos no próprio repo e menus nativos
(`VIEW3D_MT_*` etc., que não constam na referência). **Não** checa acesso via variável (`obj.algo`) — para isso use
`rag_search.py --symbol bpy.types.Object.algo`.

Estado em 2026-09-28: `caffmob_draw/` (148 arquivos) sem referências desconhecidas.

## Inputs de modificadores Geometry Nodes (5.2) — afeta o núcleo paramétrico

`change_log.md` → `bpy.types.NodesModifier`: **adicionados** `properties`, `is_input_used`, `is_input_visible`;
**removido** `bl_system_properties_get` do modificador.

- `NodesModifier.properties` é `NodesModifierProperties` (somente leitura). Os sockets ficam em uma estrutura gerada em tempo de
  execução — por isso `properties.inputs.<identifier>` **não aparece** na referência estática; confirme no Blender quando mexer nisso.
- `NodesModifier` **não** está na lista de tipos com custom properties (`bpy_types_custom_properties.md`); `NodesModifierProperties` está.
  Ou seja, `mod["Socket_2"]` é o caminho antigo (< 5.2).
- O projeto encapsula a diferença:

| Operação | Helper (use sempre) | 5.2+ | < 5.2 |
|---|---|---|---|
| Ler | `compat.get_gn_input(mod, nome)` | `mod.properties.inputs.<id>.value` | `mod[<id>]` |
| Escrever | `compat.set_gn_input(mod, nome, valor)` (faz `update_tag()`) | idem | idem |
| Driver path | `compat.gn_input_data_path(mod, nome)` | `modifiers["M"].properties.inputs.<id>.value` | `modifiers["M"]["<id>"]` |

- `nome` é o nome do socket na interface do grupo; o helper resolve o `identifier` via `node_group.interface.items_tree[nome].identifier`
  e mantém cache (invalidado em `KeyError`/`AttributeError`).
- **Duplicação conhecida:** `caffmob_draw/hb_utils.py` tem helpers equivalentes (linhas ~8–60). Ao alterar a lógica, mantenha os dois
  em sincronia ou consolide em `compat.py`.

## Propriedades `bpy.props` × custom properties (5.0)

`bpy.props.md` (exemplo Getter/Setter): o RNA guarda valores de `bpy.props` num armazenamento interno **"system" separado desde o
Blender 5.0**. Consequências:

- `obj.btm_cabinet.width` ✔ — `obj["btm_cabinet"]["width"]` ✘ (não enxerga o valor RNA).
- Custom properties "soltas" (`scene['IS_MAIN_SCENE']`, `obj['IS_DETAIL_LINE']`, `scene['btm_nesting_json_cache']`) continuam válidas.
- `ID.bl_system_properties_get(*, do_create=False)` existe mas é marcado **DEBUG ONLY** — não use em código de produção.
- Getters/setters customizados devem guardar dados via `self.get(...)` / `self["..."]` com nome próprio, como no exemplo oficial.

## Shaders builtin da GPU

Os únicos nomes válidos no 5.2 estão em `gpu.shader.md` → "Built-in shaders" (ver lista em `02_padroes_blender_5_2.md`).
`compat.get_builtin_shader(name_3d='UNIFORM_COLOR', name_2d='2D_UNIFORM_COLOR')` tenta o nome moderno primeiro; o fallback `2D_*`
só serve para Blender antigo.

## Outras mudanças 5.1 → 5.2 relevantes

| Mudança | Onde afeta | Ação |
|---|---|---|
| `WindowManager.invoke_popup(operator, *, width=300, auto_keymap=False)` — novo argumento `auto_keymap` | Popups de operador | Compatível (argumento opcional). |
| `Panel.bl_icon` / `Panel.bl_icon_value` adicionados ("Icon override for the panel category tab") | Abas "CAFFMob Draw"/"CAFFMob Draw" da sidebar | Opcional: ícone na aba de categoria (só 5.2+; proteja com `bpy.app.version`). |
| `Menu.draw_preset(self, context)` — antes `(self, _context)` | Menus de preset | Só nomes de parâmetro. |
| `Node.poll(ntree)` / `NodeCustomGroup.poll(ntree)` — antes `_ntree` | Nós customizados (não usados hoje) | — |
| `UILayout.template_palette(data, property)` — removido `color` | Não usado | — |
| `UILayout.textbox`, `UILayout.link`, `UILayout.template_collection_importer` adicionados | UI | Disponíveis para UI nova. |
| `Object.visible_raycast` ("Object visibility to raycast rays"; ver também `ShaderNodeRaycast`, novo no 5.2) | Render/materiais | Não confundir com `Scene.ray_cast` do snapping. |
| `BlendData.all_ids` adicionado | Varreduras de dados | Alternativa a iterar cada coleção de `bpy.data`. |
| `Preferences.asset_libraries`, `UserAssetLibrary.remote_url` adicionados | `hb_assets.py` | Avaliar ao evoluir bibliotecas de assets. |
| `GreasePencilLineartModifier.fill_strokes` adicionado | Layouts 2D (`hb_layouts.py`, Line Art) | Opcional. |

## Manifesto × realidade

`blender_manifest.toml` diz `blender_version_min = "4.2.0"`. Com os helpers de `compat.py` o código **tenta** rodar em 4.2+, mas
o RAG e o smoke test cobrem apenas 5.2. Se o suporte a < 5.2 não for mais necessário, subir `blender_version_min` para `"5.2.0"`
elimina ramos de compatibilidade.
