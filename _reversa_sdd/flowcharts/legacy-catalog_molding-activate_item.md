# `hb_catalog.activate_item` — item do catálogo → produto na cena

Local: `blendertomob/catalog/ops_catalog.py:45` (operador), `:16` (`_apply_global_assembly_config`), `:89` (`not_yet_implemented`).

```mermaid
flowchart TD
    A[execute item_id] --> B[catalog_data.find_entry<br/>busca linear em CATALOG]
    B --> C{entry?}
    C -- não --> W[WARNING Unknown catalog item → CANCELLED]
    C -- sim --> D{action_operator vazio?}
    D -- sim --> I[INFO no action wired → CANCELLED]
    D -- não --> E{contém '.'?}
    E -- não --> ER[ERROR Bad action_operator format → CANCELLED]
    E -- sim --> F[getattr bpy.ops, módulo, método]
    F --> G{AttributeError?}
    G -- sim --> FB[hb_face_frame.draw_cabinet INVOKE_DEFAULT<br/>cabinet_name='Base Door' + config global → FINISHED]
    G -- não --> H[op **action_args EXEC_DEFAULT]
    H --> J{exceção?}
    J -- sim --> ER2[ERROR Failed to activate → CANCELLED]
    J -- não --> K[_apply_global_assembly_config<br/>context.active_object]
    K --> Z[FINISHED]

    subgraph NYI[hb_catalog.not_yet_implemented item_name]
        N1{'Upper' ou 'Wall' no nome?} -- sim --> N2[Upper]
        N1 -- não --> N3{'Tall', 'Pantry' ou 'Oven'?}
        N3 -- sim --> N4[Tall]
        N3 -- não --> N5[Base Door]
        N2 --> N6[draw_cabinet INVOKE_DEFAULT + config global]
        N4 --> N6
        N5 --> N6
    end

    subgraph CFG[_apply_global_assembly_config obj]
        G1[root = find_cabinet_root obj ou obj] --> G2{root.face_frame_cabinet?}
        G2 -- sim --> G3[ensure_default_styles FF; estilo ativo<br/>.assign_style_to_cabinet root]
        G2 -- não --> G4{root.hb_frameless?}
        G4 -- sim --> G5[idem com estilos frameless]
        G3 & G5 --> G6[exceções engolidas]
    end
```

## Explicação

- 🟢 Cada entrada do catálogo carrega `action_operator` + `action_args`; o operador faz despacho dinâmico em `bpy.ops` — `ops_catalog.py:59-80`.
- 🟢 Entradas `_todo(...)` apontam para `hb_catalog.not_yet_implemented`, que coloca um armário face frame genérico mapeado por palavras-chave do nome — `catalog_data.py:37-42`, `ops_catalog.py:99-108`.
- 🟢 `hb_face_frame.draw_cabinet.execute` apenas dispara modais `INVOKE_DEFAULT` (`place_cabinet`, `place_corner_cabinet`, `place_appliance`) e retorna FINISHED imediatamente — `product_libraries/face_frame/operators/ops_cabinet.py:37-68`.
- 🟡 Consequência: `_apply_global_assembly_config(context.active_object)` roda **antes** do usuário confirmar o posicionamento no modal, sobre o objeto ativo anterior (ou sobre o cabinet-preview, dependendo de como o modal cria o objeto) — possível aplicação de estilo no objeto errado.
- 🟡 `getattr(bpy.ops.<mod>, <op>)` em geral não levanta `AttributeError` para operadores inexistentes (o erro surge na chamada), então o ramo de fallback é provavelmente inalcançável; um operador inexistente cai no `except Exception` → CANCELLED.
