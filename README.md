# Getting Started

```python
from juju import Juju

juju = Juju()
lxd = juju.get_cloud('lxd')
controller = lxd.bootstrap('lxd-test')
model = controller.get_model('default')

# We might want an async and blocking version of deploy()?
model.deploy('mediawiki-single')

mediawiki = model.get_service('mediawiki')
mediawiki.expose()
```


