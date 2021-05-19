import tempfile

from juju.client.proxy.proxy import Proxy, ProxyNotConnectedError
from kubernetes import client
from kubernetes.stream import portforward


class KubernetesProxy(Proxy):
    def __init__(
            self,
            api_host,
            namespace,
            remote_port,
            service,
            service_account_token,
            ca_cert=None,
    ):
        config = client.Configuration()
        config.host = api_host
        config.ssl_ca_cert = ca_cert
        config.api_key = {"authorization": "Bearer " + service_account_token}

        self.namespace = namespace
        self.remote_port = remote_port
        self.service = service

        try:
            self.remote_port = int(remote_port)
        except ValueError:
            raise ValueError("Invalid port number: {}".format(remote_port))

        if ca_cert:
            self.temp_ca_file = tempfile.NamedTemporaryFile()
            self.temp_ca_file.write(bytes(ca_cert, 'utf-8'))
            self.temp_ca_file.flush()
            config.ssl_ca_cert = self.temp_ca_file.name

        self.api_client = client.ApiClient(config)

    def connect(self):
        corev1 = client.CoreV1Api(self.api_client)
        service = corev1.read_namespaced_service(self.service, self.namespace)

        label_selector = ','.join(k + '=' + v for k, v in service.spec.selector.items())

        pods = corev1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector,
        )

        self.port_forwarder = portforward(
            corev1.connect_get_namespaced_pod_portforward,
            pods.items[0].metadata.name,
            self.namespace,
            ports=str(self.remote_port),
        )

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.port_forwarder.close()
            self.temp_ca_file.close()
        except AttributeError:
            pass

    def socket(self):
        if self.port_forwarder is not None:
            return self.port_forwarder.socket(self.remote_port)._socket
        raise ProxyNotConnectedError()
