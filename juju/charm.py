# Copyright 2019 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import logging
import zipfile
import yaml
from pathlib import Path
from . import model

log = logging.getLogger(__name__)


def get_local_charm_metadata(path):
    """Retrieve Metadata of a Charm from its path

    :patam str path: Path of charm directory or .charm file

    :return: Object of charm metadata
    """
    if str(path).endswith('.charm'):
        with zipfile.ZipFile(path, 'r') as charm_file:
            metadata = yaml.load(charm_file.read('metadata.yaml'), Loader=yaml.FullLoader)
    else:
        entity_path = Path(path)
        metadata_path = entity_path / 'metadata.yaml'
        metadata = yaml.load(metadata_path.read_text(), Loader=yaml.FullLoader)

    return metadata


class Charm(model.ModelEntity):
    pass
