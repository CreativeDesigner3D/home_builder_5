# `Cabinet.create_base_carcass(name)` — geração da caixa inferior

Local: `blendertomob/product_libraries/frameless/types_frameless.py:125-313` 🟢
Variantes: `create_tall_carcass` (`:315-455`), `create_upper_carcass` (`:457-535`),
`create_lap_drawer_carcass` (`:645-777`), `CornerCabinet.create_corner_base_carcass` (`:2472-2631`).

Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

```mermaid
flowchart TD
    A["create_cabinet(name)<br/>cage GN, marcadores, Dim X/Y/Z, Mirror Y"] --> B["prompts: Material Thickness (mt)<br/>Toe Kick Height/Setback/Type, Remove Bottom, Leg Leveler Inset<br/>Base Top Construction, Stretcher Width 4in, Sink Apron Width 7in"]
    B --> C["variáveis de driver: dim_x dim_y dim_z mt tkh tks rb btc sw saw"]
    C --> D{"Toe Kick Type<br/>(lido 1× na criação)"}
    D -- "0 Notch Ends to Floor" --> E["Laterais CabinetSideNotched<br/>Length=dim_z; recorte CPM_CORNERNOTCH X=tkh Y=tks"]
    D -- "1/2/3" --> F["Laterais CabinetPart<br/>z=tkh; Length=dim_z-tkh"]
    E & F --> G["Bottom: x=mt z=tkh<br/>L=dim_x-2mt  W=dim_y  hide se rb"]
    G --> H["Back: x=mt z=IF(rb,0,tkh+mt)<br/>L=IF(rb,dim_z,dim_z-tkh-mt)  W=dim_x-2mt  T=mt"]
    H --> I{"tipo 0?"}
    I -- sim --> J["Toe Kick: y=-dim_y+tks<br/>L=dim_x-2mt  W=tkh  hide se rb"]
    I -- não --> K
    J --> K["Top (btc==0): y=-mt z=dim_z L=dim_x-2mt W=dim_y-mt"]
    K --> L["Front Stretcher (btc==1): y=-dim_y W=sw<br/>Back Stretcher (btc==1): y=-sw-mt W=sw"]
    L --> M["Sink Apron (btc==2): vertical, y=-dim_y W=saw"]
    M --> N["Bay: x=mt y=-dim_y z=tkh+IF(rb,0,mt)<br/>X=dim_x-2mt  Y=dim_y-mt  Z=dim_z-tkh-IF(rb,0,mt)-mt"]
    N --> O{"tipo"}
    O -- "1 Ladder" --> P["LadderBaseCage (placeholder)<br/>y=-dim_y+tks X=dim_x Y=dim_y-tks Z=tkh"]
    O -- "3 Leg Levelers" --> Q["4 GeoNodeHardware nos cantos<br/>inset lli (padrão 2in)"]
    O -- "0/2" --> R["fim"]
```

## Regras extraídas

| Peça | Posição | Comprimento (Length) | Largura (Width) | Espessura | Conf. |
|---|---|---|---|---|---|
| Lateral esq. (tipo 0) | origem, rot Y −90° | `dim_z` | `dim_y` | `mt` | 🟢 `:148-156` |
| Lateral (tipos 1-3) | z=`tkh` | `dim_z-tkh` | `dim_y` | `mt` | 🟢 `:169-190` |
| Base (Bottom) | x=`mt`, z=`tkh` | `dim_x-2mt` | `dim_y` | `mt` | 🟢 `:193-203` |
| Fundo (Back) | x=`mt`, z=`tkh+mt` | `dim_z-tkh-mt` | `dim_x-2mt` | `mt` (fundo cheio, não 3/6 mm) | 🟢 `:206-216` |
| Rodapé (Toe Kick) | y=`-dim_y+tks` | `dim_x-2mt` | `tkh` | `mt` | 🟢 `:220-231` |
| Tampo (btc=0) | y=`-mt`, z=`dim_z` | `dim_x-2mt` | `dim_y-mt` | `mt` | 🟢 `:235-246` |
| Travessas (btc=1) | frente y=`-dim_y`; trás y=`-sw-mt` | `dim_x-2mt` | `sw`=4in | `mt` | 🟢 `:249-276` |
| Avental de pia (btc=2) | vertical, frente | `dim_x-2mt` | `saw`=7in | `mt` | 🟢 `:279-289` |
| Vão (Bay) | x=`mt`, z=`tkh+mt` | X=`dim_x-2mt` | Y=`dim_y-mt`, Z=`dim_z-tkh-2mt` | — | 🟢 `:292-300` |

Observações:
- 🟢 A construção é "laterais passantes": base, fundo, tampo e rodapé ficam **entre** as laterais (`dim_x-2·mt`).
- 🟢 O fundo tem a mesma espessura da caixa (`mt`) e fica embutido entre laterais — não há rebaixo/canal para fundo fino (HDF 3/6 mm usual no Brasil).
- 🟢 Diferença alta×base: no gabinete alto o fundo desconta mais um `mt` (`Length = ...-mt`, `:401`) e o tampo tem largura `dim_y` e sem recuo `y` (`:422-431`).
- 🟢 Superior (`create_upper_carcass`): sem rodapé; fundo `z=mt`, `Length=dim_z-2mt`; vão `Z=dim_z-2mt` (`:501-535`).
- 🟡 O tipo de rodapé é lido de `self.obj.get('Toe Kick Type', 0)` só na criação (`:144`); mudar o prompt depois não troca laterais entalhadas↔retas nem cria/remove o painel de rodapé (a geometria fica inconsistente até recriar o gabinete). `ops_defaults.update_toe_kick_prompts` (`operators/ops_defaults.py:19-26`) altera o índice mesmo assim.
- 🔴 Ladder Style é só uma gaiola marrom placeholder ("peças reais serão implementadas depois", `:1608-1619`).
