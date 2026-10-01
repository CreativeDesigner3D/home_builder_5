# `run_calc_fix` / `run_calc_fix_until_stable` — forçar reavaliação de drivers

Local: 🟢 `blendertomob/hb_utils.py:190-246` e `:249-297`. Contorno documentado no código para o bug do Blender
#133392 (drivers de "netos" não atualizam). Chamado em cerca de 61 pontos do pacote (grep).

```mermaid
flowchart TD
    A[run_calc_fix context, obj=None, passes=2] --> B{obj?}
    B -- sim --> C[objs = obj + children_recursive]
    B -- não --> D[objs = scene.objects]
    C --> E[coleta todas as calculators de objs.home_builder.calculators]
    D --> E
    E --> F{repete passes vezes}
    F --> G[para cada o: o.location = o.location<br/>para cada mod NODES: show_viewport = show_viewport]
    G --> H[calculator.calculate para todas]
    H --> I[frame_set atual+1 e volta ao atual]
    I --> J[view_layer.update]
    J --> F
    F -- fim --> K[depsgraph = evaluated_depsgraph_get<br/>o.evaluated_get para cada MESH, erros ignorados]

    S[run_calc_fix_until_stable max_passes=5, tol=0.0001] --> S1{pass < max_passes}
    S1 --> S2[run_calc_fix passes=1]
    S2 --> S3[snapshot: nome e dimensions de cada MESH]
    S3 --> S4{snapshot anterior existe<br/>e todas as diferenças <= tol?}
    S4 -- sim --> S5[return pass+1]
    S4 -- não --> S1
    S1 -- esgotou --> S6[return -1]
```

**Regra (HB_CORE-R21).** 🟢 Cada passada "toca" transformações e modificadores, recalcula as calculadoras, provoca uma
mudança de frame e atualiza a view layer. A versão "until stable" compara `dimensions` de meshes com tolerância de 0,1 mm
por até 5 passadas; retorna o número de passadas ou -1.

**Observações.**
- 🟢 `frame_set` dispara `frame_change_pre/post` de outros add-ons e altera o frame duas vezes: custo O(passes × objetos).
- 🟡 A comparação usa `zip` na ordem de coleta; se objetos forem criados ou removidos entre passadas, os pares podem ficar
  desalinhados.
- 🟡 Sem contexto de janela (modo background), `context.view_layer` funciona, mas os efeitos de redesenho não se aplicam.
