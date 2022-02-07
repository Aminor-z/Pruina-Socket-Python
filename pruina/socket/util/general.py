# cython: language_level=3
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from pruina.socket.handler.util.util import hashcode

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class Hooks(object):
    def __init__(self):
        self.hooks: dict = None
        self.hooks_reflect_dict: dict = None


class CachedHooks(Hooks):
    def __init__(self, thread_pool_size=2, parent: Hooks = None):
        super().__init__()
        self.last_hook_key: str = ""
        self.last_hook_value = None
        self.hooks: dict = dict()
        self.hooks_reflect_dict = dict()
        self.thread_pool_size = thread_pool_size
        self.thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        if parent:
            self.parent = parent
            from copy import copy
            self.hooks = copy(self.parent.hooks)
            self.hooks_reflect_dict = copy(self.parent.hooks_reflect_dict)

    def clear_cache(self):
        self.last_hook_key = None
        self.last_hook_value = None

    def add_hook(self, flag, func, new_thread=False):
        if type(flag) == str:
            hc = hashcode(flag)
            self.hooks[hc] = (func, new_thread)
            self.hooks_reflect_dict[hc] = flag
        elif type(flag) == int:
            self.hooks[flag] = (func, new_thread)

    def get_hook(self, flag):
        if self.last_hook_key == flag:
            return self.last_hook_value
        else:
            c = self.hooks.get(flag)
            if c is not None:
                self.last_hook_key = flag
                self.last_hook_value = c
                return c
            else:
                return None

    def call_hook(self, flag, data, **kwargs):
        c = self.get_hook(flag)
        if c is not None:
            if c[1]:
                self.thread_pool.submit(c[0], data, **kwargs)
            else:
                return c[0](data, **kwargs)
        else:
            name = self.hooks_reflect_dict.get(flag)
            if name is None:
                logging.error(f"No such hook[type={flag}]")
            else:
                logging.error(f"No such hook[type={name}]")


class LoadFunc(object):
    def __init__(self, obj_call, *args, **kwargs):
        self.obj_call: callable = None
        self.args: () = None
        self.kwargs: {} = None
        self.set_load_func(obj_call, *args, **kwargs)

    def set_load_func(self, obj_call, *args, **kwargs):
        self.obj_call = obj_call
        self.args: () = args
        self.kwargs: {} = kwargs

    def load(self):
        if self.args and len(self.args):
            if self.kwargs and len(self.kwargs):
                obj = self.obj_call(*self.args, **self.kwargs)
            else:
                obj = self.obj_call(*self.args)
        else:
            if self.kwargs and len(self.kwargs):
                obj = self.obj_call(**self.kwargs)
            else:
                obj = self.obj_call()
        return obj


class Resources(object):
    def __init__(self):
        self.__unload_resources = list()  # real signature unknown
        """
        will load on init.
        """
        self.__unload_local_resources = list()
        """
        will load on local init.
        """
        self.resources: dict = dict()

    def get(self, name: str):
        resource = self.resources.get(name)
        if resource is not None:
            resource = resource.get()
        return resource

    def add_resource(self, name: str, obj_call, *args, **kwargs):
        resource = Resource(name=name)
        resource.set_load_func(obj_call, *args, **kwargs)
        self.__unload_resources.append(resource)

    def add_lazy_resource(self, name: str, obj_call, *args, **kwargs):
        resource = LazyResource(name=name)
        resource.set_load_func(obj_call, *args, **kwargs)
        self.__unload_resources.append(resource)

    def load_resources(self):
        unload_resource: Resource
        if len(self.__unload_resources) > 0:
            q = tqdm(self.__unload_resources)
            for unload_resource in q:
                q.set_description(f"Loading Resource[{unload_resource.name}]")
                if type(unload_resource) == Resource:
                    self.resources[unload_resource.name] = unload_resource.load()
                elif type(unload_resource) == LazyResource:
                    self.resources[unload_resource.name] = unload_resource
            q.set_description("Loading Resource")
            q.close()
        del self.__unload_resources

    def remove(self, name: str):
        try:
            self.remove(name)
        except:
            pass


class Resource(object):
    load_func: LoadFunc

    def __init__(self, name: str = ""):
        self.name = str(self) if name is None else name
        self.is_load: bool = False
        self.load_func: LoadFunc
        self.resource: object = None

    def load(self):
        try:
            self.resource = self.load_func.load()
            self.is_load = True
            return self
        except Exception:
            error = f"At Resource[{str(self)}]:\n" \
                    f"\tObject:{str(self.load_func.obj_call)}\n" \
                    f"\targs:{str(self.load_func.args)}\n" \
                    f"\tkwargs:{str(self.load_func.kwargs)}"
            logging.error(f"{traceback.format_exc()}\n{error}")

    def set_load_func(self, obj_call, *args, **kwargs):
        self.load_func = LoadFunc(obj_call, *args, **kwargs)

    def get(self, release=True):
        if self.load_func:
            if release:
                self.load_func = None
        return self.resource


class LazyResource(Resource):
    def __init__(self, name=None):
        super().__init__(name=name)

    def get(self, release=True):
        if not self.is_load:
            self.load()
            if release:
                del self.load_func
        return self.resource


class Properties:
    def set(self, name: str, target):
        setattr(self, name, target)

    def get(self, name: str):
        try:
            return getattr(self, name)
        except:
            return None

    def remove(self, name: str):
        try:
            delattr(self, name)
        except:
            pass
