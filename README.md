[![Pruina-Socket-Python](https://socialify.git.ci/Aminor-z/Pruina-Socket-Python/image?font=Inter&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FAminor-z%2FPruina-Socket-Python%2Fmain%2Flogo.svg&pattern=Plus&pulls=1&stargazers=1&theme=Dark)](https://github.com/Aminor-z/Pruina-SocketServer-Python)

# Prunia-Socket
**Prunia-Socket**是一个用于快速开发的TCP Socket组件，包含服务端、客户端等内容。
# Prunia-Socket-Python
通过以下简单的代码，即可启动具有响应功能的`Prunia-Socket`的服务端和客户端：

```python
from pruina.socket.server import PruinaSocketServer
from pruina.socket.client import PruinaSocketClient


# 服务端响应函数
def server_response(word, handler= None, **kwargs):
    print(f"{handler.server_name}: get '{word.decode()}'")
    handler.send("server response", word)


# 客户端响应函数
def client_response(word, handler: PruinaSocketClient = None, **kwargs):
    decoded_word = word.decode()
    print(f"{handler.name}: get '{decoded_word}'")


# 服务端
server = PruinaSocketServer()
server.hooks.add_hook("client msg", server_response)
server.serve_forever(new_thread=True)  # new_thread=False时，将阻塞

# 客户端
client = PruinaSocketClient()
client.hooks.add_hook("server response", client_response)
client.connect()
client.send("client msg", b"hello world!")

# 暂时阻止退出
import time

time.sleep(1)
```

也可通过以下简单的代码，即可启动复杂的服务端（以torch模型服务为例）：  
1. 模型配置

    ``` python
    # 模型配置
    import torch.nn as nn
    import os
    import torch


    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(1, 1)

        def forward(self, x):
            return self.linear(x)


    # 模型存储路径，不存在自动生成
    model_path = 'resources/example.pt'
    if not os.path.exists('resources/example.pt'):
        torch.save(Model(), model_path)
    ```

2. 服务端配置和启动
    
    ``` python
    # 响应函数
    from pruina.socket.handler.MessageHookRequestHandler import MessageHookRequestHandler
    from pruina.socket.server import PruinaSocketServer


    def predict(d: bytes, handler: MessageHookRequestHandler = None, **kwargs):
        model = handler.resources.get("torch_model")
        x = torch.tensor([float(d.decode())], dtype=torch.float32)
        y = model(x)
        print(f'Torch model:\n\t{x.item():.4f}->{y.item():.4f}')

    server = PruinaSocketServer()
    server.resources.add_lazy_resource("torch_model", torch.load, "resources/example.pt")
    server.hooks.add_hook("predict", predict)
    server.serve_forever()
    ```

3. 使用客户端测试（此处使用另一进程）

    ``` python
    # 响应函数
    from pruina.socket.client import PruinaSocketClient

    client = PruinaSocketClient()
    client.connect()
    client.send("predict", b"1.23")
    ```


# 使用概览
## 服务端
* **PruinaSocketServer**  
以hook形式运行的SocketServer

> **PruinaSocketServer 可选参数**  
> * `host`: str = socket.gethostname() # 服务地址  
> * `port`: int = 50003 # 端口  
> * `name`: str = 'server' # 服务名称  
> * `daemon_threads`: bool = True # daemon设置  
> 
> **PruinaSocketServer 属性**  
> * `name`: str = name # 服务名称
> * `server`: ThreadingTCPServer = ThreadingTCPServer((host, port), MessageHookRequestHandler) # ThreadingTCPServer
> * `properties`: Properties = Properties() # Properties
> * `local_properties`: Properties = Properties() # Local Properties
> * `resources`: Resources = Resources() # Resources
> * `local_resources`: Resources = Resources() # Local Resources
> * `hooks`: CachedMsgHooks = CachedMsgHooks() # CachedMsgHooks

示例代码：

```python
from pruina.socket.handler.MessageHookRequestHandler import MessageHookRequestHandler
from pruina.socket.server import PruinaSocketServer


# 服务端响应函数
def server_response(word, handler: MessageHookRequestHandler = None, **kwargs):
    decoded_word = word.decode()
    print(f"{handler.server_name}: get '{decoded_word}'")
    handler.send("server response", word)


# 服务端
server = PruinaSocketServer()
server.hooks.add_hook("client msg", server_response)
server.serve_forever()
```

## 客户端
* **PruinaSocketClient**  
以hook形式运行的SocketClient

> **PruinaSocketClient 可选参数**  
> * `host`: str = socket.gethostbyname(socket.gethostname()) # 服务地址
> * `port`: int = 50003 # 端口
> * `name`: str = 'server' # 服务名称
> * `max_retry`: int = 3 # 最大重试次数
> 
> **PruinaSocketClient 属性**  
> * `name`: str = name # 服务名称
> * `host`: str = socket.gethostbyname(socket.gethostname()) # 服务地址  
> * `port`: int = 50003 # 端口  
> * `client`: socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.socket
> * `properties`: Properties = Properties() # Properties
> * `resources`: Resources = Resources() # Resources
> * `hooks`: CachedMsgHooks = CachedMsgHooks() # CachedMsgHooks

示例代码：

```python
from pruina.socket.client import PruinaSocketClient


# 客户端响应函数
def client_response(word, handler: PruinaSocketClient = None, **kwargs):
    decoded_word = word.decode()
    print(f"{handler.name}: get '{decoded_word}'")


# 客户端
client = PruinaSocketClient()
client.hooks.add_hook("server response", client_response)
client.connect()
client.send("client msg", b"hello world!")
```

## 组件
* **Hooks**  
默认使用`CachedMsgHooks`。  
`CachedMsgHooks`是拥有一级缓存的Hook映射集，实现将消息标识符与函数的绑定。
> **CachedMsgHooks 参数**  
> * `parent`: MsgHooks = None 指向另一个CachedMsgHooks时，会进行deepcopy

示例代码：

```python
from pruina.socket.server import PruinaSocketServer


# hook函数
def server_response(word, handler=None, **kwargs):
    decoded_word = word.decode()
    print(f"{handler.server_name}: get '{decoded_word}'")
    handler.send("server response", word)


server = PruinaSocketServer()
server.hooks.add_hook("client msg", server_response)
server.serve_forever()

```

* **Properties**  
`Properties`用于传入小型对象，如int，str等。  
Prunia的server中，有`properties`和`local_properties`之分。
> * **properties**  
> 在整个server和所有handler中，只存在唯一的`properties`
>
> * **local_properties**  
> 对于每一个建立连接的handler，都有唯一的`Properties`。
> 每个handler中的`local_properties`都将从Server中设定的`local_properties`中deepcopy一份，作为handler独立的`local_properties`。

示例代码：

```python
from pruina.socket.server import PruinaSocketServer

server = PruinaSocketServer()

server.properties.set_properties("var_int", 1)
server.properties.set_properties("var_str", "Hello World!")
server.local_properties.set_properties("var_list", list())
server.local_properties.set_properties("var_dict", dict())

server.init()
server.serve_forever()
```

* Resources  
`Resources`用于传入大型资源，如`torch.nn.model`等。  
`Resources`中保存着`Resource`和`LazyResource`（见Resource & LazyResource）  
Prunia的server中，有`resources`和`local_resources`之分。
> * **resources**  
> 在整个server和所有handler中，只存在唯一的`resources`。  
>
> * **local_resources**  
> 对于每一个建立连接的handler，都有唯一的`local_resources`。  
> 每个handler中的`local_resources`都将从Server中设定的`local_resources`中deepcopy一份，作为handler独立的`local_resources`。

示例代码见Resource和LazyResource部分。

* Resource & LazyResource
`Resource`和`LazyResource`是资源实体。  
> * **Resource**  
> 资源实体，传入构造数据后，将在服务器启动时加载。  
> 
> * **LazyResource**  
> 资源实体，传入构造数据后，将在首次`get()`时进行加载。

示例代码：

```python
import os

import torch
import torch.nn as nn

from pruina.socket.server import PruinaSocketServer
from pruina.socket.handler.MessageHookRequestHandler import MessageHookRequestHandler


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)


def predict(d: bytes, handler: MessageHookRequestHandler = None, **kwargs):
    model = handler.resources.get("torch_model_1")
    x = torch.tensor([float(d.decode())], dtype=torch.float32)
    y = model(x)
    print(f'Torch model:\n\t{x.item():.4f}->{y.item():.4f}')


model_path = 'resources/example.pt'
if not os.path.exists('resources/example.pt'):
    torch.save(Model(), model_path)
server = PruinaSocketServer()

server.resources.add_resource("torch_model_1", torch.load, model_path)
server.resources.add_lazy_resource("torch_model_2", torch.load, model_path)
server.local_resources.add_resource("torch_model_3", torch.load, model_path)
server.local_resources.add_lazy_resource("torch_model_4", torch.load, model_path)

server.hooks.add_hook("predict", predict)

server.init()
server.serve_forever()
```

## Cython
`Prunia-SocketServer`可通过`cypackage`直接转化为cython版本。
* 安装`cypackage`：
```cmd
pip install cypackage
```
* 使用`cypackage`生成cython版本的`Prunia-SocketServer`
```cmd
cypackage prunia-socket
```