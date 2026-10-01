# `GeoNodeWall.get_connected_wall` / `_geometric_neighbor` — vizinhança entre paredes

Local: 🟢 `blendertomob/hb_types.py:486-522` e `:524-561`. Conexão criada por `connect_to_wall`
(`hb_types.py:480-484`): a parede nova recebe uma restrição `COPY_LOCATION` apontando para o empty `obj_x` da parede
anterior. O `obj_x` fica em `location.x = Length` por driver (`hb_types.py:454-466`).

```mermaid
flowchart TD
    A[get_connected_wall direction, include_loop_seam] --> B{direction}
    B -- left --> C{para cada constraint COPY_LOCATION}
    C --> C1{target.parent tem IS_WALL_BP?}
    C1 -- sim --> R1[return GeoNodeWall target.parent]
    C1 -- não --> C
    B -- right --> D{para cada obj em bpy.data.objects<br/>com IS_WALL_BP e != self}
    D --> D1{alguma COPY_LOCATION com target == self.obj_x?}
    D1 -- sim --> R2[return GeoNodeWall obj]
    D1 -- não --> D
    C -- fim --> E{include_loop_seam?}
    D -- fim --> E
    E -- não --> N[return None]
    E -- sim --> G[_geometric_neighbor direction]
    G --> G1[extremos: início = matrix_world.translation<br/>fim = início + cos/sin rot.z × Length]
    G1 --> G2{para cada outra parede com modificador}
    G2 --> G3{left: fim dela ~ meu início<br/>right: início dela ~ meu fim<br/>hypot < 0,01 m}
    G3 -- sim --> R3[return other]
    G3 -- não --> G2
    G2 -- fim --> N
```

**Regra (HB_CORE-R08).** 🟢 A vizinhança é primeiro topológica (cadeia de restrições) e, opcionalmente, geométrica
(coincidência de extremos no plano XY do mundo, tolerância de 0,01 m). A busca geométrica existe porque a cadeia de
restrições não atravessa a "costura" de um cômodo fechado; a docstring avisa que quem percorre a cadeia não deve usar
`include_loop_seam`, senão o laço não termina (`hb_types.py:492-499`).

**Observações.**
- 🟢 A busca à direita é O(n × restrições) sobre `bpy.data.objects`, incluindo objetos de outras cenas.
- 🟡 Só a rotação Z entra no cálculo dos extremos; paredes inclinadas em X/Y seriam avaliadas errado.
- 🟢 Exceções em `get_input('Length')` são engolidas (`except Exception`), e a parede é ignorada.
