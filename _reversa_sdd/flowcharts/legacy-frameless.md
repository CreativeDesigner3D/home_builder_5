# Fluxogramas — módulo legado `frameless`

Camada legada (fork do Home Builder 5). Pacote: `blendertomob/product_libraries/frameless/`
(26 arquivos `.py`, ~23 mil linhas). Biblioteca de gabinetes **sem quadro frontal** (estilo europeu / 32 mm,
porém parametrizada em polegadas no fork americano).

Legenda de confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.

Arquivos de detalhe por função:
- [`legacy-frameless-create_base_carcass.md`](legacy-frameless-create_base_carcass.md) — geração da caixa inferior (laterais, base, fundo, rodapé, tampo/travessas, vão).
- [`legacy-frameless-splitter_vertical.md`](legacy-frameless-splitter_vertical.md) — divisores com calculadora de vãos (gavetas/portas empilhadas).
- [`legacy-frameless-front_overlay.md`](legacy-frameless-front_overlay.md) — cálculo de sobreposição (overlay) e dimensionamento de portas/frentes/gavetas.
- [`legacy-frameless-place_cabinet_modal.md`](legacy-frameless-place_cabinet_modal.md) — operador modal de inserção em parede/piso.
- [`legacy-frameless-create_wall_countertop.md`](legacy-frameless-create_wall_countertop.md) — geração de tampo (bancada) por corrida de paredes.
- [`legacy-frameless-assign_crown.md`](legacy-frameless-assign_crown.md) — extrusão de moldura (crown) com cantos.

## 1. Visão geral — quem chama quem

```mermaid
flowchart LR
    subgraph UI["UI / Menus"]
        PSP["Frameless_Scene_Props.draw_library_ui<br/>props_hb_frameless.py:2383"]
        MENUS["menus_frameless.py<br/>HOME_BUILDER_MT_*_commands"]
    end
    subgraph OPS["operators/ (17 módulos)"]
        DRAW["hb_frameless.draw_cabinet<br/>ops_placement.py:1927"]
        PLACE["hb_frameless.place_cabinet (modal)<br/>ops_placement.py:270"]
        BAY["hb_frameless.change_bay_opening<br/>ops_opening.py:92"]
        STY["ops_styles.py<br/>assign_cabinet_style / door styles / pulls"]
        CT["ops_countertop.py<br/>add_countertops"]
        CR["ops_crown.py / ops_toe_kick.py / ops_upper_bottom.py<br/>molduras extrudadas"]
        DEF["ops_defaults.py<br/>propaga padrões às instâncias"]
        LIB["ops_library.py<br/>grupos de gabinetes .blend"]
        TPL["props_elevation_templates.py<br/>templates de elevação"]
    end
    subgraph TYPES["Tipos paramétricos"]
        TF["types_frameless.py<br/>Cabinet + aberturas + frentes"]
        TP["types_products.py<br/>Product (prateleira, sanca, perna...)"]
        APP["common/types_appliances.py"]
    end
    subgraph PROPS["Estado"]
        SP["Scene.hb_frameless<br/>Frameless_Scene_Props"]
        CS["Frameless_Cabinet_Style"]
        DS["Frameless_Door_Style"]
        WM["wood_materials.py + finish_colors.py"]
    end
    subgraph CORE["Núcleo (outros módulos)"]
        HBT["hb_types.GeoNodeCage / GeoNodeCutpart<br/>drivers + inputs GN"]
        HBU["hb_utils.run_calc_fix"]
        HBP["hb_placement.PlacementMixin / hb_snap"]
    end
    PSP --> DRAW --> PLACE
    PLACE --> TF & TP & APP
    PLACE --> STY
    MENUS --> BAY --> TF
    TPL --> TF & APP
    STY --> CS & DS
    CS --> WM
    TF --> HBT
    TF --> SP
    PLACE --> HBP
    PLACE --> HBU
    CT --> SP
    CR --> SP
    DEF --> SP
```

🟢 Registro: `frameless/__init__.py:10-20` chama `props_hb_frameless.register()`, `props_elevation_templates.register()`,
`operators.register()` (17 módulos, `operators/__init__.py:20-37`) e `menus_frameless.register()`.

## 2. Hierarquia de classes (tipos paramétricos)

```mermaid
classDiagram
    direction TB
    class GeoNodeCage {
      <<hb_types>>
      create()
      var_input()
      driver_input()
      set_input()
      add_property()
    }
    class GeoNodeCutpart {
      <<hb_types>>
      add_part_modifier()
    }
    class Cabinet {
      width = 18in
      height = 34in
      depth = 24in
      default_exterior = Doors
      create_cabinet()
      create_base_carcass()
      create_tall_carcass()
      create_upper_carcass()
      add_cage_to_bay()
      _add_leg_levelers()
    }
    class BaseCabinet {
      add_exterior()
      add_doors()
      add_drawer_door()
      add_drawer_stack(n)
    }
    class LapDrawerCabinet {
      create_lap_drawer_carcass()
    }
    class TallCabinet {
      is_stacked
      add_doors()
    }
    class RefrigeratorCabinet {
      add_openings()
    }
    class UpperCabinet {
      is_stacked
      add_doors()
    }
    class CornerCabinet {
      corner_size=36in
      add_corner_doors()
      create_corner_base_carcass()
      create_corner_upper_carcass()
      add_corner_modifier()*
    }
    class DiagonalCornerBaseCabinet
    class PieCutCornerBaseCabinet
    class DiagonalCornerTallCabinet {
      stub
    }
    class PieCutCornerTallCabinet
    class DiagonalCornerUpperCabinet {
      stub
    }
    class PieCutCornerUpperCabinet
    class CabinetBay
    class SplitterVertical {
      splitter_qty
      opening_sizes
      opening_inserts
    }
    class SplitterHorizontal {
      splitter_qty
      opening_sizes
      opening_inserts
    }
    class CabinetOpening {
      half_overlay_flags
      add_properties_front_overlays()
      add_properties_front_overlay_calculations()
    }
    class Doors {
      door_pull_location
    }
    class FlipUpDoor
    class Drawer
    class Pullout
    class FalseFront
    class Appliance {
      appliance_name
    }
    class OpenWithShelves
    class CabinetInterior
    class CabinetShelves
    class InteriorSplitterVertical
    class InteriorSplitterHorizontal
    class InteriorSection
    class LadderBaseCage
    class CabinetPart
    class CabinetSideNotched
    class CabinetFront {
      assign_door_style()
      get_pull_object()
    }
    class CabinetDoor
    class CabinetFlipUpDoor
    class CabinetDrawerFront {
      add_drawer_box()
    }
    class CabinetPulloutFront {
      add_drawer_box()
    }
    class Product {
      create_product()
    }
    class FloatingShelf
    class Valance
    class SupportFrame
    class HalfWall
    class Leg
    class TallLeg
    class UpperLeg
    class Panel
    class MiscPart

    GeoNodeCage <|-- Cabinet
    Cabinet <|-- BaseCabinet
    Cabinet <|-- LapDrawerCabinet
    Cabinet <|-- TallCabinet
    Cabinet <|-- RefrigeratorCabinet
    Cabinet <|-- UpperCabinet
    Cabinet <|-- CornerCabinet
    CornerCabinet <|-- DiagonalCornerBaseCabinet
    CornerCabinet <|-- PieCutCornerBaseCabinet
    CornerCabinet <|-- DiagonalCornerTallCabinet
    CornerCabinet <|-- PieCutCornerTallCabinet
    CornerCabinet <|-- DiagonalCornerUpperCabinet
    CornerCabinet <|-- PieCutCornerUpperCabinet
    GeoNodeCage <|-- CabinetBay
    GeoNodeCage <|-- SplitterVertical
    GeoNodeCage <|-- SplitterHorizontal
    GeoNodeCage <|-- CabinetOpening
    CabinetOpening <|-- Doors
    CabinetOpening <|-- FlipUpDoor
    CabinetOpening <|-- Drawer
    CabinetOpening <|-- Pullout
    CabinetOpening <|-- FalseFront
    CabinetOpening <|-- Appliance
    CabinetOpening <|-- OpenWithShelves
    GeoNodeCage <|-- CabinetInterior
    CabinetInterior <|-- CabinetShelves
    CabinetInterior <|-- InteriorSplitterVertical
    CabinetInterior <|-- InteriorSplitterHorizontal
    GeoNodeCage <|-- InteriorSection
    GeoNodeCage <|-- LadderBaseCage
    GeoNodeCutpart <|-- CabinetPart
    CabinetPart <|-- CabinetSideNotched
    CabinetPart <|-- CabinetFront
    CabinetFront <|-- CabinetDoor
    CabinetFront <|-- CabinetFlipUpDoor
    CabinetFront <|-- CabinetDrawerFront
    CabinetFront <|-- CabinetPulloutFront
    GeoNodeCage <|-- Product
    Product <|-- FloatingShelf
    Product <|-- Valance
    Product <|-- SupportFrame
    Product <|-- HalfWall
    Product <|-- Leg
    Product <|-- TallLeg
    Product <|-- UpperLeg
    Product <|-- Panel
    CabinetPart <|-- MiscPart
```

🟢 Todas as heranças lidas em `types_frameless.py` (linhas 8–2921) e `types_products.py` (8–938).
🔴 `DiagonalCornerTallCabinet.create` (`types_frameless.py:2808-2811`) e `DiagonalCornerUpperCabinet.create`
(`:2869-2872`) só criam a gaiola — sem caixa nem portas (stubs). A UI de canto diagonal está comentada
(`props_hb_frameless.py:1945-1965`).

## 3. Árvore de objetos de um gabinete (composição em tempo de execução)

```mermaid
flowchart TD
    CAB["Cabinet cage<br/>IS_FRAMELESS_CABINET_CAGE<br/>CABINET_TYPE=BASE/TALL/UPPER"]
    CAB --> LS["Left Side / Right Side<br/>CabinetPart ou CabinetSideNotched"]
    CAB --> BOT["Bottom"]
    CAB --> BACK["Back (espessura = mt)"]
    CAB --> TK["Toe Kick (só tipo 0)"]
    CAB --> TOP["Top | Front+Back Stretcher | Sink Apron<br/>(visibilidade por driver btc)"]
    CAB --> LAD["Ladder Base cage (tipo 1)"]
    CAB --> LL["4× Leg Leveler (tipo 3)"]
    CAB --> BAYN["Bay (CabinetBay)<br/>IS_FRAMELESS_BAY_CAGE"]
    BAYN --> INS{"Inserção"}
    INS --> DOORS["Doors / Drawer / Pullout / FlipUp / FalseFront / Appliance / OpenWithShelves"]
    INS --> SPL["SplitterVertical | SplitterHorizontal"]
    SPL --> OPN["Opening N (CabinetOpening)"]
    OPN --> DOORS
    DOORS --> FR["CabinetDoor / CabinetDrawerFront / ..."]
    FR --> PULL["Pull (GeoNodeHardware)"]
    FR --> DB["Drawer Box (GeoNodeDrawerBox)"]
    DOORS --> INT["Interior: CabinetShelves (array)"]
    DOORS --> OVL["Overlay Prompt Obj (empty com drivers)"]
```

🟢 Montado por `Cabinet.add_cage_to_bay` (`types_frameless.py:52-63`), `SplitterVertical.create` (`:940-1026`),
`Doors.create` (`:1271-1328`), `CabinetDrawerFront.add_drawer_box` (`:1867-1926`).

## 4. Fluxo de criação de um gabinete (do clique à cena)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Library UI
    participant D as draw_cabinet
    participant P as place_cabinet (modal)
    participant T as types_frameless
    participant S as assign_cabinet_style
    participant H as hb_utils.run_calc_fix
    U->>L: clica "Door Drw"
    L->>D: cabinet_name="Base Door Drw"
    D->>P: INVOKE_DEFAULT cabinet_type=BASE
    P->>P: cria preview cage + ARRAY + cotas
    loop MOUSEMOVE
        P->>P: raycast → parede? gap → fill/snap
    end
    U->>P: LMB / Enter
    P->>T: get_cabinet_class() → BaseCabinet(default_exterior)
    T->>T: create_base_carcass + add_exterior
    P->>S: bpy.ops.hb_frameless.assign_cabinet_style
    P->>H: run_calc_fix ×2 (bug #133392)
    P->>P: assign_door_styles_to_cabinet
    P->>P: calculate_shelf_quantity / toggle_mode
```

🟢 `ops_placement.py:1934-1977` (draw_cabinet), `:1825-1851` (confirmação), `:1455-1509` (fábrica de classes).

## 5. Estilos, materiais e cores

```mermaid
flowchart TD
    A["Frameless_Cabinet_Style.assign_style_to_cabinet(obj)<br/>props_hb_frameless.py:693"] --> B["get_finish_material()"]
    B --> B1{"wood_species"}
    B1 -- CUSTOM --> B2["custom_material (sem rotação)"]
    B1 -- CUSTOM_PROCEDURAL --> B3["carrega 'Wood' de cabinet_material.blend<br/>+ update_finish_material_custom_procedural"]
    B1 -- espécie/PAINT_GRADE --> B4["carrega/reusa 'Wood' + cópia ROTATED<br/>update_finish_material(): cores + grão por espécie"]
    A --> C["get_interior_material(): MAPLE_PLY | MATCHING | CUSTOM"]
    A --> E["edge = custom_edge | finish ROTATED"]
    A --> F["para cada CABINET_PART:<br/>Top/Bottom Surface = finish se 'Finish Top/Bottom' senão interior<br/>(Finished Interior → tudo finish)<br/>Edge W1/W2/L1/L2 = edge"]
    F --> G["modifiers CPM_*: Material / Stile / Rail(ROTATED) / Panel"]
    A --> H["aberturas: Inset Front = (overlay==INSET)<br/>Half Overlay * = (overlay==HALF) salvo FORCE_HALF_OVERLAY_*"]
    A --> I["raiz (canto): Inset Front / Half Overlay Top/Bottom/Outer"]
```

🟢 `props_hb_frameless.py:636-798`, `wood_materials.py:22-228`, `finish_colors.py:207-253`.

## 6. Templates de elevação

```mermaid
flowchart LR
    S["select_elevation_template<br/>(parede ativa)"] --> I["init_from_wall: wall_width=Length, ceiling_height"]
    I --> CP["create_preview: cages + retângulos rotulados"]
    CP --> UP["update_preview (callback de cada prop)"]
    UP --> DR["draw_elevation_template → draw_cabinets"]
    DR --> RR["Refrigerator_Range: Pantry(Tall) → Fridge(RefrigeratorCabinet) → Base L / Range / Base R → Uppers"]
    DR --> IS["Island: BaseCabinets rotacionados 180°, sink central, dishwasher L/R"]
    RR & IS --> AS["apply_styles_to_cabinet + run_calc_fix"]
    AS --> CL["clear_preview"]
```

🟢 `props_elevation_templates.py:1401-1478` (operadores), `:566-775` (Refrigerator_Range.draw_cabinets), `:1136-1284` (Island.draw_cabinets).
🟡 `range_hood_type='RAISE_UPPER'` apenas une as uppers sobre o fogão — não eleva nada; `range_hood_height` só aparece na UI (`:866-869`).
