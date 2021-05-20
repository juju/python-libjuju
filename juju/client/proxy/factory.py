from juju.client.proxy.kubernetes.proxy import KubernetesProxy


def proxy_from_config(conf):
    if conf is None:
        return None

    if 'type' not in conf:
        return None

    proxy_type = conf['type']
    if proxy_type != 'kubernetes-port-forward':
        raise ValueError('unknown proxy type %s' % proxy_type)

    return _construct_kube_proxy(conf['config'])


def _construct_kube_proxy(config):
    return KubernetesProxy(
        config.get('api-host', ''),
        config.get('namespace', ''),
        config.get('remote-port', ''),
        config.get('service', ''),
        config.get('service-account-token', ''),
        config.get('ca-cert', None),
    )
