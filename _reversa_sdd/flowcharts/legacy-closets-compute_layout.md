# `solver_closets.compute_layout` + `distribute_widths` — solver de distribuição de painéis e vãos

> Arquivo: `blendertomob/product_libraries/closets/solver_closets.py` (126 linhas, **sem `bpy`**, recarregável a quente).
> Chamado por `ClosetStarter.recalculate()` (`types_closets.py:492`) com o spec montado em `_spec_from_props` (`types_closets.py:434-456`).
> Confiança geral: 🟢 CONFIRMADO (lido linha a linha).

## Entrada / saída

| Campo | Origem | Significado |
|---|---|---|
| `spec.width` | `hb_closet_starter.width` | largura total do starter (m) |
| `spec.height` | `hb_closet_starter.height` | altura do envelope (piso → topo do módulo) |
| `spec.pt` / `spec.st` | `Scene.hb_closets.panel_thickness` / `shelf_thickness` | espessura de painel / prateleira (default 0,75 in = 19,05 mm) |
| `spec.kick_height` | `hb_closet_starter.toe_kick_height` | altura do rodapé |
| `spec.kick_setback` | idem | **não usado pelo solver** (usado só em `types_closets`) |
| `spec.bays[i]` | `hb_closet_bay` | `width, locked, height, depth, floor, remove_bottom, remove_cleat` |

Saída: `{'widths': [...], 'panels': [{x, z, length, depth}], 'bays': [{x, z0, width, height, depth, kick, floor, bottom_z, top_z, cleat_z, interior_z, interior_h}]}`.

## Fluxograma

```mermaid
flowchart TD
    A([compute_layout spec]) --> B[n = len bays]
    B --> DW[[distribute_widths width, pt, bays]]

    subgraph DWS["distribute_widths (solver_closets.py:26-50)"]
        D1["interior = W − (n+1)·pt"] --> D2["locked_total = Σ largura dos vãos travados"]
        D2 --> D3{existe vão destravado?}
        D3 -- sim --> D4["share = (interior − locked_total) / nº destravados"]
        D4 --> D5["share = max(share, MIN_BAY_WIDTH = 1 in)"]
        D5 --> D6[atribui share a cada destravado]
        D3 -- não --> D7{widths e locked_total > 0?}
        D7 -- sim --> D8["escala proporcional: w · interior/locked_total"]
        D7 -- não --> D9[mantém larguras]
    end

    DW --> X["xs[0]=0; xs[i+1] = xs[i] + pt + w[i]<br/>(borda esquerda de cada painel)"]
    X --> P{para painel i em 0..n}
    P --> P1["vizinhos = bay[i−1] (esq) e bay[i] (dir), se existirem"]
    P1 --> P2["top = max(topo de cada vizinho)<br/>piso: height do vão · suspenso: altura do starter"]
    P2 --> P3["bottom = min(base de cada vizinho)<br/>piso: 0 · suspenso: H − height do vão"]
    P3 --> P4["painel: x=xs[i], z=bottom, length=top−bottom,<br/>depth = max(profundidade dos vizinhos)"]
    P4 --> P
    P -- fim --> Q{para cada vão i}
    Q --> Q1["kick = kick_height se piso, senão 0"]
    Q1 --> Q2["z0 = 0 se piso, senão H − height"]
    Q2 --> Q3["bottom_z = kick (face inferior da prat. de baixo)<br/>top_z = height − st (face inferior da prat. de cima)"]
    Q3 --> Q4["interior_z = bottom_z + st<br/>interior_h = max(top_z − interior_z, 0,25 in)"]
    Q4 --> Q5{remove_bottom?}
    Q5 -- sim --> Q6[cleat_z = 0]
    Q5 -- não --> Q7[cleat_z = interior_z]
    Q6 --> Q8["vão: x = xs[i] + pt, ..."]
    Q7 --> Q8
    Q8 --> Q
    Q -- fim --> R([retorna widths, panels, bays])
```

## Regras embutidas

1. **Painéis compartilhados** 🟢 (`solver_closets.py:85-97`): painel *i* é o painel ESQUERDO do vão *i*; N vãos → N+1 painéis. Um painel entre um vão de piso e um vão suspenso vai do piso ao topo (altura máxima envolvente); profundidade = maior dos vizinhos.
2. **Redistribuição de largura** 🟢: vãos destravados dividem igualmente o que sobra; valor mínimo 1 in (25,4 mm). Com o mínimo ativado a soma **não fecha** e os painéis ultrapassam a largura do starter ("degrada visivelmente", docstring `:30-32`).
3. **Todos travados** 🟢 (`:44-49`): escala proporcional para fechar na largura total. Caso degenerado `locked_total == 0` (todos travados com largura 0) mantém larguras sem ajuste 🟡.
4. **Vão de piso vs. suspenso** 🟢: o envelope de um vão de piso começa no piso (o rodapé fica dentro do envelope); o suspenso é ancorado no topo do starter (`z0 = H − height`).
5. **Altura interna** 🟢: `interior_h = height − kick − 2·st`, piso em 0,25 in (6,35 mm) para evitar valores negativos.
6. **Cleat** 🟢: acompanha a prateleira inferior; sem prateleira inferior desce para a base do envelope.

## Exemplo numérico (Base default) 🟢/🟡

W = 80 in (2032 mm), 2 vãos (placement usa `auto_bay_qty(80in) = ceil(80/42) = 2`, `types_closets.py:1749-1754`), pt = 19,05 mm:
`interior = 2032 − 3·19,05 = 1974,85 mm` → cada vão 987,4 mm. H = 819 mm, kick = 96 mm:
`bottom_z = 96`, `interior_z = 115,05`, `top_z = 799,95`, `interior_h = 684,9 mm`.
