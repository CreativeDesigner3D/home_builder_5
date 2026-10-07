# Cápsula de reprodução — BUG-20261007-A2G7

- Commit base: `f6d9188` (branch `feature/001-incremento-1-padrao-dimensoes`) + alterações locais não commitadas (identidade CAFFMob Draw e feature 003)
- Ambiente: Linux 6.8, Blender 5.2 (`/opt/blender/blender --background --factory-startup`), pacote `caffmob_draw` do repositório via `tests/_blender_env.py`
- Classificação: **determinístico**, taxa 3/3

| Caso | Comando | Exit | Resultado |
|---|---|---|---|
| Sala 4 x 3 m pelo editor de paredes | `blender --background --factory-startup --python-exit-code 1 --python evidence/reproducao-ajustar-piso.py` | 0 | piso 4 vértices, 5 x 5 m em (-2,5..2,5); paredes em -0,15..4,15 x -0,15..3,15 |
| Sala em L pelo editor + um balcão frameless na cena | `... --python evidence/reproducao-sala-L-construtor.py` | 0 | paredes HB com **0 vértices** na malha; balcão com `object_kind = 'WALL'`; piso 5 x 5 m (área 25,0; esperado 12,0) |
| Sala em L de paredes da camada nova (`btm_wall_segments`, 48 vértices) | `... --python evidence/reproducao-sala-L-camada-nova.py` | 0 | piso por fecho convexo: área 15,06 m², caixa -0,075..4,075 (face externa), o recorte do L coberto |
