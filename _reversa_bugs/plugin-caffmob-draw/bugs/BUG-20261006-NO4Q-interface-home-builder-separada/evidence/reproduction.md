# Cápsula de reprodução — BUG-20261006-NO4Q e BUG-20261006-QAVK

- Commit base: `f6d9188` (+ correção do BUG-20261006-SCVF não commitada) · Linux · Blender 5.2.0 LTS · 2026-10-06
- Determinístico (inspeção do código e do Blender ao vivo).

## Interface (NO4Q)
- Barra N: aba "Home Builder" (9 painéis raiz, 96 com subpainéis) e aba "Blender to Mob" (3 painéis raiz, 9 com
  subpainéis); `bl_category` "Home Builder" em 9 classes, "Blender to Mob" em 3, "Editor de Paredes" em 1.
- 54 ocorrências do texto "Home Builder" em 32 arquivos `.py`; rótulos legados em inglês.

## Identidade (QAVK)
- `blendertomob/blender_manifest.toml`: `id = "blendertomob"`, `name = "Blender to Mob"`.
- Prefixos de `bl_idname`: hb_face_frame 111, hb_frameless 94, btm 43, hb_closets 35, blendertomob 29,
  home_builder_layouts 24, home_builder_walls 22, home_builder_details 15, home_builder_doors_windows 12,
  home_builder_obstacles 5, home_builder 4, home_builder_stairs 3, hb_general 2, hb_catalog 2 (~400 operadores).
- Ocorrências em `.py`: "hb_" 4.402 (119 arquivos), "home_builder" 736 (51), "btm" 448 (69), "blendertomob" 79 (19),
  "BlenderToMob" 26 (16), "Blender to Mob" 9 (5), "Home Builder" 54 (32).
- Propriedades registradas e **gravadas nos .blend**: `Object.home_builder`, `Scene.home_builder`, `Scene.hb_*`
  (frameless, face_frame, closets, project, obstacles, catalog…), `Object.hb_closet_*`, `Object.face_frame_*`,
  `Object.btm_*`, `Scene.btm_*`, `WindowManager.btm_*`.
- Bibliotecas do pacote: amostra de 21 `.blend` abertos no Blender → 20 com dados gravados nesses nomes
  (`home_builder` 24 IDs, `pro_closet`, `closet_pricing`…). Renomear o atributo sem migração perde esses dados.
