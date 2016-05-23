


class AsyncRunner:
    async def __call__(self, facade_method, *args, **kwargs):
        await self.connection.rpc(facade_method(*args, **kwargs))


class ThreadedRunner:
    pass

# Methods are descriptors??
# get is called with params
# set gets called with the result?
# This could let us fake the protocol we want
# while decoupling the protocol from the RPC and the IO/Process context

# The problem is leaking the runtime impl details to the top levels of the API with
# async def
# By handling the Marshal/Unmarshal side of RPC as a protocol we can leave the RPC running to a specific
# delegate without altering the method signatures.
# This still isn't quite right though as async is co-op multitasking and the methods still need to know
# not to block or they will pause other execution





