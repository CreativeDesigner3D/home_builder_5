# `build_line_art_marked_channel` — canal "Marked" do Line Art

Local: `blendertomob/hb_layouts.py:564`. Auxiliares: `_emission_copy` `:521`, `_clear_emission_subset` `:536`,
`_authored_world` `:551`, `_ensure_lineart_layer` `:349`, `_apply_holdout_masks` `:678`, `update_line_art_sizes` `:476`. 🟢

> 🔴 LACUNA: nenhum chamador encontrado em `blendertomob/` fora de `hb_layouts.py` (o mesmo vale para
> `setup_iso_freestyle`, `build_line_art_text_holdouts` e `scene_uses_iso_freestyle`). O código de exportação/geração que
> os usava no Home Builder 5 não parece ter sido portado.

## Fluxograma

```mermaid
flowchart TD
    A[build_line_art_marked_channel scene] --> B{GP Line Art existe?}
    B -- não --> Z[return]
    B -- sim --> C{Scene_Freestyle_Solid existe?}
    C -- não --> Z
    C -- sim --> D[Get/cria Scene_LineArt_Marked e linka na cena]
    D --> E[Remove todos os objetos do Marked anterior]
    E --> F[lift = eixo +Z da câmera × 0,001 m]
    F --> G[Para cada inst em SOLID]
    G --> H{EMPTY instanciando COLLECTION,<br/>src não termina em ' LA-Marked',<br/>nome não começa com 'Isometric'/'Iso '?}
    H -- não --> G
    H -- sim --> I[subset = 'src LA-Marked' get/cria]
    I --> J[_clear_emission_subset:<br/>apaga cópias ' LAEmit', desvincula o resto]
    J --> K[Para cada MESH em src.all_objects<br/>com nome contendo Rail/Stile/Door (/Blind Panel/Drawer Front]
    K --> L[linka _emission_copy obj no subset]
    L --> M{subset vazio?}
    M -- sim --> G
    M -- não --> N[Empty 'inst LA-Marked' tag IS_HB_LINEART_MARKED<br/>instancia subset, parent = inst]
    N --> O[matrix_basis = W⁻¹ · T lift · W<br/>W = _authored_world inst]
    O --> P[cor = cor da inst · hide_select]
    P --> G
    G -- fim --> Q{mod 'Lineart Marked' existe?}
    Q -- não --> R[cria LINEART e move para antes de 'Resample Dashed']
    Q -- sim --> S
    R --> S[source = Marked · níveis 0..2 · contorno/crease/edge mark]
    S --> T[camada 'Marked' · material HB_LineArt_Solid]
    T --> U[_apply_holdout_masks]
    U --> V[update_line_art_sizes]
```

## Explicação

- **Problema resolvido** 🟢 (comentários `:89-121`): peças de frente/face-frame encostadas geram empates de oclusão e o
  passe sólido (nível 0) perde arestas; um terceiro passe com oclusão 0..2 redesenha só essas peças.
- **Cópias de emissão** 🟢: o filtro de collection do Line Art casa por OBJETO; linkar o original faria a peça emitir em
  todas as instâncias da cena. Por isso usa `obj.copy()` com sufixo ` LAEmit` (malha e modificadores compartilhados).
- **Elevação ("lift")** 🟢: 1 mm na direção da câmera quebra empates coplanares sem deslocar pixels numa vista ortográfica.
- **`_authored_world`** 🟢: compõe `matrix_basis`/`matrix_parent_inverse` pela cadeia de pais porque `matrix_world` pode
  estar desatualizado (depsgraph) para instâncias criadas na mesma execução.
- **Idempotência** 🟢: limpa e reconstrói a cada chamada; reaproveita o modificador existente.
- Células isométricas são puladas (desenhadas pelo passe Freestyle iso, `setup_iso_freestyle` `:825`) 🟢.
