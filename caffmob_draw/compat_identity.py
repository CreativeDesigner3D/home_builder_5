"""Migração da identidade BlenderToMob → CAFFMob Draw (BUG-20261006-QAVK, fase A).

Ao ligar a extensão `caffmob_draw` pela primeira vez:
- copia as pastas de dados do usuário da extensão antiga (`blendertomob`: biblioteca de detalhes e cores de
  acabamento) para a nova, só quando a pasta nova ainda está vazia (nunca sobrescreve);
- renomeia a biblioteca de assets "Home Builder" para "CAFFMob Draw" nas preferências, se existir;
- avisa no console se a extensão antiga ainda estiver ativa (as duas registram as mesmas propriedades).

`copy_if_empty` é Python puro (testado em `tests/test_identity.py`); o resto roda num timer, fora do `register()`.
"""

import os
import shutil

OLD_EXTENSION = "blendertomob"
OLD_LIBRARY_NAME = "Home Builder"
NEW_LIBRARY_NAME = "CAFFMob Draw"
USER_DATA_DIRS = ("detail_library", "user_data")


def copy_if_empty(src, dst):
    """Copia a pasta `src` para `dst` se `src` existir e `dst` não existir ou estiver vazia. True se copiou."""
    src, dst = str(src), str(dst)
    if not os.path.isdir(src) or not os.listdir(src):
        return False
    if os.path.isdir(dst) and os.listdir(dst):
        return False
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return True


def _old_user_root(new_root, package):
    """Pasta de dados da extensão antiga, irmã da nova (mesmo repositório de extensões)."""
    short = package.rsplit(".", 1)[-1]
    root = new_root.rstrip(os.sep)
    if not root.endswith(short):
        return None
    return root[: -len(short)] + OLD_EXTENSION


def migrate(package):
    import bpy  # type: ignore
    try:
        new_root = bpy.utils.extension_path_user(package, create=False)
    except (ValueError, TypeError):
        new_root = None            # carregado fora do sistema de extensões (testes)
    if new_root:
        old_root = _old_user_root(new_root, package)
        for name in USER_DATA_DIRS:
            if old_root and copy_if_empty(os.path.join(old_root, name), os.path.join(new_root, name)):
                print(f"CAFFMob Draw: dados de '{name}' copiados da extensão antiga.")
    prefs = bpy.context.preferences
    for lib in prefs.filepaths.asset_libraries:
        if lib.name == OLD_LIBRARY_NAME and not any(x.name == NEW_LIBRARY_NAME for x in prefs.filepaths.asset_libraries):
            lib.name = NEW_LIBRARY_NAME
    if any(key == OLD_EXTENSION or key.endswith("." + OLD_EXTENSION) for key in prefs.addons.keys()):
        print("CAFFMob Draw: a extensão antiga 'Blender to Mob' ainda está ativa. Desinstale-a em Preferências › "
              "Add-ons para evitar conflito.")
    return None


def register(package):
    import bpy  # type: ignore
    bpy.app.timers.register(lambda: migrate(package), first_interval=0.5)
