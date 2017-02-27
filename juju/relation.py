import logging

from . import model

log = logging.getLogger(__name__)


class Relation(model.ModelEntity):
    async def destroy(self):
        raise NotImplementedError()
        # TODO: destroy a relation
