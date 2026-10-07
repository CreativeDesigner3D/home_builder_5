# Reprodução sem interface (2026-10-07)

Ambiente: Linux, Blender 5.2 em `--background --factory-startup`, pacote `caffmob_draw` do repositório
(branch `feature/001-incremento-1-padrao-dimensoes`, commit base f6d9188 + alterações locais da feature 003).

Script: `reproducao-ajustar-piso.py` (sala 4 x 3 m pelo editor de paredes, depois `bpy.ops.caffmob.adjust_floor()`).

Saída:

```
HB walls 4 kinds ['WALL']
adjust_floor {'FINISHED'}
floor bbox [-2.5, -2.5] [2.5, 2.5] verts 4
walls bbox [-0.15, -0.15] [4.15, 3.15]
```

Leitura: o piso tem 4 vértices, 5 x 5 m, centrado na origem; as paredes ocupam de -0,15 a 4,15 x -0,15 a 3,15.
Todos os objetos da cena têm `btm_plane.object_kind == 'WALL'` (valor padrão). Taxa: 1/1 (determinístico).
