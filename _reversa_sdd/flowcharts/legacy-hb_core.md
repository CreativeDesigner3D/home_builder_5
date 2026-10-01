# Fluxogramas — `hb_core` (camada legada Home Builder 5)

Módulo núcleo da camada legada: modelo de objetos paramétricos baseados em Geometry Nodes (`GeoNodeObject` e subclasses),
sistema de drivers (`Variable` + `add_driver_variables`), calculadoras de distribuição (`Calculator`), PropertyGroups
`home_builder` (Object/Scene/WindowManager), projeto/cena principal, obstáculos, unidades e operadores gerais.

Legenda de confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.

Fluxos detalhados por função:

- [`legacy-hb_core-set_input.md`](legacy-hb_core-set_input.md) — escrita/leitura de inputs de GN com cache de identificadores
- [`legacy-hb_core-calculator_calculate.md`](legacy-hb_core-calculator_calculate.md) — distribuição de medidas "iguais"
- [`legacy-hb_core-run_calc_fix.md`](legacy-hb_core-run_calc_fix.md) — contorno do bug de drivers netos (#133392)
- [`legacy-hb_core-get_connected_wall.md`](legacy-hb_core-get_connected_wall.md) — vizinhança de paredes (restrição + geometria)
- [`legacy-hb_core-set_decimal.md`](legacy-hb_core-set_decimal.md) — precisão decimal das cotas

## 1. Visão geral do módulo (dependências internas)

🟢 Baseado nos imports de `blendertomob/hb_types.py:1-6`, `hb_props.py:15-17`, `hb_props_obstacles.py:1-8`,
`hb_project.py:18-23`, `ops.py:1-8`, `units.py:1-19` e `__init__.py:58-80,212-256`.

```mermaid
flowchart LR
    subgraph hb_core
        UNITS[units.py<br/>reexporta data/units.py]
        UTILS[hb_utils.py<br/>GN I/O, base points,<br/>drivers, calc fix, view state]
        TYPES[hb_types.py<br/>Variable, GeoNodeObject<br/>e subclasses]
        PROPS[hb_props.py<br/>Calculator, Home_Builder_*_Props,<br/>HB_Wall_Editor_Props]
        PROJ[hb_project.py<br/>Home_Builder_Project_Props,<br/>cena principal]
        OBST[hb_props_obstacles.py<br/>catálogo + Obstacles_Scene_Props]
        DRVF[hb_driver_functions.py<br/>IF / OR / AND]
        OPS[ops.py<br/>operadores gerais]
    end
    DATAUNITS[data/units.py]
    INIT[__init__.py]
    LIBS[product_libraries/*<br/>Cabinet, Closet, FaceFrame...]
    LAYOUTS[operators/layouts.py]
    MOLD[molding/*]

    UNITS --> DATAUNITS
    TYPES --> UNITS
    TYPES --> UTILS
    PROPS --> UTILS
    PROPS --> TYPES
    PROPS -.update callbacks.-> LAYOUTS
    PROPS -.enum/update.-> MOLD
    PROPS -.enum.-> LIBS
    OBST --> UNITS
    OPS --> UTILS
    INIT -->|register| PROPS
    INIT -->|register| PROJ
    INIT -->|register| OBST
    INIT -->|register| OPS
    INIT -->|driver_namespace| DRVF
    INIT -->|load_post: ensure_main_scene| PROJ
    LIBS -->|herdam GeoNodeCage| TYPES
```

## 2. Hierarquia de classes do modelo de objetos

🟢 `hb_types.py:59-962`; subclasses externas 🟢 por grep (`product_libraries/frameless/types_frameless.py:8`,
`closets/types_closets.py:139`, `face_frame/types_face_frame.py:766`, `hb_details.py:107`).

```mermaid
classDiagram
    class Variable {
      obj : ID
      data_path : str
      name : str
    }
    class GeoNodeObject {
      obj : Object
      create(geo_node_name, name)
      create_curve(geo_node_name, name)
      add_empty(obj_name)
      add_property(name,type,value,items)
      var_input / var_prop / var_location / var_rotation / var_hide
      driver_input / driver_prop / driver_location / driver_rotation / driver_hide
      set_input / get_input / has_input / has_modifier
      draw_input / draw_prop
    }
    GeoNodeObject <|-- GeoNodeWall
    GeoNodeObject <|-- GeoNodeCage
    GeoNodeObject <|-- GeoNodeRectangle
    GeoNodeObject <|-- GeoNodeCutpart
    GeoNodeObject <|-- GeoNode5PieceDoor
    GeoNodeObject <|-- GeoNodeHardware
    GeoNodeObject <|-- GeoNodeDrawerBox
    GeoNodeObject <|-- GeoNodeDoorSwing
    GeoNodeObject <|-- GeoNodeDimension
    GeoNodeObject <|-- GeoNodeArrow
    GeoNodeObject <|-- CabinetPartModifier
    GeoNodeCage <|-- Cabinet_frameless
    GeoNodeCage <|-- ClosetBay_etc
    GeoNodeCage <|-- FaceFrameCabinet_etc
    GeoNodeCutpart ..> CabinetPartModifier : add_part_modifier
    GeoNodeObject ..> Variable : var_*()
```

## 3. Criação de um objeto GeoNode (`GeoNodeObject.create`)

🟢 `hb_types.py:79-97` (mesh) e `hb_types.py:99-122` (curva POLY de 2 pontos).

```mermaid
flowchart TD
    A[create geo_node_name, name] --> B{geo_node_name em<br/>bpy.data.node_groups?}
    B -- não --> C[bpy.data.libraries.load<br/>geometry_nodes/NAME.blend<br/>data_to.node_groups = NAME]
    B -- sim --> D
    C --> D[ng = bpy.data.node_groups NAME]
    D --> E[mesh = meshes.new name<br/>obj = objects.new name, mesh]
    E --> F[mod = obj.modifiers.new NAME, 'NODES'<br/>mod.node_group = ng]
    F --> G[obj.home_builder.mod_name = mod.name]
    G --> H[scene.collection.objects.link obj]
    H --> I{Subclasse}
    I -- GeoNodeWall --> W[IS_WALL_BP, MENU_ID, cor das prefs<br/>cria empty obj_x com driver location.x = Length]
    I -- GeoNodeCage --> K[IS_GEONODE_CAGE, WIRE, preto,<br/>invisível a câmera/sombra, hide_render]
    I -- GeoNodeDimension --> DM[create_curve + ensure_dimension_text_offset_basis<br/>IS_2D_ANNOTATION, IS_DIMENSION, inputs das props da cena<br/>Unit Type = get_unit_type]
    I -- DrawerBox/DoorSwing/Rectangle/Arrow --> P[set_input de valores padrão em polegadas]
```

## 4. Sistema de drivers (Variable → driver)

🟢 `hb_types.py:59-68,167-287`, `hb_utils.py:55-60,299-305`, `hb_props.py:238-257,382-406`.

```mermaid
flowchart TD
    A[Chamador ex.: Cabinet.create] --> B[var_input 'Dim Z','dim_z'<br/>var_prop 'Material Thickness','mt'<br/>prompt.get_var ...]
    B --> C[Variable obj, data_path, name]
    C --> D[driver_input / driver_location / driver_prop / driver_hide<br/>com expression e lista de Variables]
    D --> E[obj.driver_add data_path, index]
    E --> F[add_driver_variables:<br/>para cada Variable -> var SINGLE_PROP<br/>targets 0 .id = obj, .data_path]
    F --> G[driver.expression = expression]
    G --> H[(bpy.app.driver_namespace<br/>IF, OR, AND)]
    D -. data_path de input GN .-> P{bpy.app.version >= 5.2?}
    P -- sim --> P1["modifiers['M'].properties.inputs.ID.value"]
    P -- não --> P2["modifiers['M']['ID']"]
```

## 5. Cena principal e projeto

🟢 `hb_project.py:143-278`, `__init__.py:58-80`.

```mermaid
flowchart TD
    L[load_post: load_file_post] --> NS[registra IF/OR/AND no driver_namespace<br/>se ausentes]
    NS --> E[ensure_main_scene]
    E --> G[get_main_scene]
    G --> G1{alguma cena com IS_MAIN_SCENE?}
    G1 -- sim --> R[retorna essa cena]
    G1 -- não --> G2[get_room_scenes: sem IS_LAYOUT_VIEW/IS_DETAIL_VIEW<br/>ordenadas por home_builder.sort_order]
    G2 --> G3{há cenas de cômodo?}
    G3 -- sim --> M1[main = primeira]
    G3 -- não --> G4{há alguma cena?}
    G4 -- sim --> M2[main = scenes 0]
    G4 -- não --> N[None]
    M1 --> T[try main IS_MAIN_SCENE = True<br/>except AttributeError: ignora - contexto de desenho]
    M2 --> T
    T --> R
    R --> P[get_project_props -> main.hb_project]
```

## 6. Obstáculos — seleção de tipo

🟢 `hb_props_obstacles.py:104-145,216-252`.

```mermaid
flowchart TD
    A[Usuário escolhe obstacle_type no enum] --> B[get_obstacle_items: cabeçalhos HEADER_* com ids 0/100/200/300<br/>+ itens numerados a partir de base+1]
    B --> C[update_obstacle_type]
    C --> D{get_obstacle_data encontrou<br/>e não é HEADER_?}
    D -- sim --> E[copia largura, altura, profundidade,<br/>altura do piso do catálogo]
    D -- não --> F[nada]
    E --> G[draw_obstacle_ui]
    F --> G
    G --> H{tipo começa com HEADER_?}
    H -- sim --> I[label 'Select an obstacle type' e retorna]
    H -- não --> J[botão home_builder_obstacles.place_obstacle<br/>+ dimensões; 'From Floor' só se surface == WALL]
```

## 7. Operadores gerais (`ops.py`)

🟢 `ops.py:10-685`.

```mermaid
flowchart LR
    subgraph Diálogos
        TD[blendertomob.to_do<br/>placeholder]
        RS[blendertomob.set_recommended_settings<br/>overlay/shading/snapping]
        RD[blendertomob.rendering_settings<br/>só desenha props EEVEE/Freestyle]
    end
    CC[blendertomob.create_camera<br/>câmera da vista + Track To + backplate emissivo]
    AA[home_builder_annotations.apply_settings_to_all<br/>linhas, textos, cotas]
    SC[blendertomob.set_scale_with_two_points<br/>modal + draw handler POST_PIXEL]
    SC --> SC1[1º clique: first_point] --> SC2[2º clique: fator = known_distance / distância<br/>empty_display_size *= fator] --> SC3[cleanup: remove draw handler]
    SC -->|ESC / botão direito| SC3
```
