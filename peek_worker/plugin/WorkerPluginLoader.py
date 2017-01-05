import logging
from typing import Type, Tuple

from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC
from peek_worker.plugin.PeekWorkerPlatformHook import PeekWorkerPlatformHook

logger = logging.getLogger(__name__)


class _CeleryLoaderMixin:
    ''' Celery Loader Mixin

    Separate some logic out into this class

    '''

    @property
    def celeryAppIncludes(self):
        includes = []
        for pluginWorkerMain in list(self._loadedPlugins.values()):
            includes.extend(pluginWorkerMain.celeryAppIncludes)
        return includes


class WorkerPluginLoader(PluginLoaderABC, _CeleryLoaderMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "WorkerPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls)
        return cls._instance

    @property
    def _entryHookFuncName(self) -> str:
        return "peekWorkerEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginWorkerEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["worker"]

    def _loadPluginThrows(self, pluginName: str,
                          EntryHookClass: Type[PluginCommonEntryHookABC],
                          pluginRootDir: str,
                          requiresService: Tuple[str, ...]) -> None:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekWorkerPlatformHook()

        pluginMain = EntryHookClass(pluginName=pluginName,
                                    pluginRootDir=pluginRootDir,
                                    platform=platformApi)

        # Load the plugin
        pluginMain.load()

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks
        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pluginMain.celeryApp)

        # Start the Plugin
        pluginMain.start()

        self._loadedPlugins[pluginName] = pluginMain
