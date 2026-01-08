from .plugin_manager import (
    ZshPluginManager,
    ZshPluginManagerType,
)
from .omz_plugin_mananger import OmzPluginManager
from .zinit_plugin_manager import ZinitPluginManager

PLUGIN_MANAGERS: dict[ZshPluginManagerType, type[ZshPluginManager]] = {
    ZshPluginManagerType.ZINIT: ZinitPluginManager,
    ZshPluginManagerType.OMZ: OmzPluginManager,
}


def get_plugin_manager(plugin_manager_type: ZshPluginManagerType):
    return PLUGIN_MANAGERS.get(plugin_manager_type, ZinitPluginManager)()


__all__ = [
    "ZshPluginManager",
    "ZshPluginManagerType",
    "OmzPluginManager",
    "ZinitPluginManager",
    "PLUGIN_MANAGERS",
    "get_plugin_manager",
]
