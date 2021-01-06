from functools import partial

import asyncio
import theblues.charmstore
import theblues.errors


class CharmStore:
    """
    Async wrapper around theblues.charmstore.CharmStore
    """
    def __init__(self, loop, cs_timeout=20):
        self.loop = loop
        self._cs = theblues.charmstore.CharmStore(timeout=cs_timeout)

    def __getattr__(self, name):
        """
        Wrap method calls in coroutines that use run_in_executor to make them
        async.
        """
        attr = getattr(self._cs, name)
        if not callable(attr):
            wrapper = partial(getattr, self._cs, name)
            setattr(self, name, wrapper)
        else:
            async def coro(*args, **kwargs):
                method = partial(attr, *args, **kwargs)
                for attempt in range(1, 4):
                    try:
                        return await self.loop.run_in_executor(None, method)
                    except theblues.errors.ServerError:
                        if attempt == 3:
                            raise
                        await asyncio.sleep(1, loop=self.loop)
            setattr(self, name, coro)
            wrapper = coro
        return wrapper
