import logging

from .client import client
from .errors import JujuError

log = logging.getLogger(__name__)


async def _get_annotations(entity_tag, connection):
    """Get annotations for the specified entity

    :return dict: The annotations for the entity
    """
    facade = client.AnnotationsFacade.from_connection(connection)
    result = (await facade.Get(entities=[{"tag": entity_tag}])).results[0]
    if result.error is not None:
        raise JujuError(result.error)
    return result.annotations


async def _set_annotations(entity_tag, annotations, connection):
    """Set annotations on the specified entity.

    :param annotations map[string]string: the annotations as key/value
        pairs.
    """
    # TODO: ensure annotations is dict with only string keys
    # and values.
    log.debug('Updating annotations on %s', entity_tag)
    facade = client.AnnotationsFacade.from_connection(connection)
    args = client.EntityAnnotations(
        entity=entity_tag,
        annotations=annotations,
    )
    return await facade.Set(annotations=[args])
