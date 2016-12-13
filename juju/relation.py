import logging

from . import model

log = logging.getLogger(__name__)


class Relation(model.ModelEntity):
    async def destroy(self):
        pass
        # TODO: destroy a relation
