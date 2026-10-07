# Cápsula de reprodução — BUG-20261006-SCVF

- Commit base: `f6d9188` · branch `feature/001-incremento-1-padrao-dimensoes` · Linux · Blender 5.2.0 LTS
- Data: 2026-10-06

## 1. Raiz do repositório como pacote

Comando: `git archive --format=zip --prefix=BlenderPremiumMob-master/ HEAD` (equivale ao "Download ZIP" do GitHub) e
`blender --command extension validate <zip>`.

- O ZIP tem dois manifestos: `BlenderPremiumMob-master/blender_manifest.toml` (raiz, `id = "blendertomob"`,
  `name = "Blender to Mob"`) e `BlenderPremiumMob-master/blendertomob/blender_manifest.toml` (pacote real).
- Validação: `FATAL_ERROR: Error, archive has no manifest` (não instala como extensão).

## 2. Raiz carregada como add-on legado junto da extensão nova (Blender em background)

Script `both.py`: importa a raiz como pacote `blendertomob_legacy` e chama `register()`; depois registra o pacote novo
e salva um `.blend`.

- Raiz: `ModuleNotFoundError: No module named 'blendertomob_legacy.ui'` → a cópia antiga **não registra** (a raiz
  não tem `ui/`; só o pacote `blendertomob/` tem).
- Extensão nova: registra; `save_pre` só com `blendertomob.inspection.save_guard`; salvar: `{'FINISHED'}`.

## 3. Preferências desta máquina

`bpy.context.preferences.addons` contém `blendertomob` (add-on legado) além de `bl_ext.user_default.blendertomob`;
ao abrir: `Add-on not loaded: "blendertomob", cause: No module named 'blendertomob'`.

## Classificação

Determinístico (1/1 em cada passo).
