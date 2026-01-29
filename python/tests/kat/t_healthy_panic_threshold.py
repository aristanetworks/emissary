from typing import Dict, Generator, Tuple, Union

from abstract_tests import HTTP, AmbassadorTest, Node, ServiceType
from kat.harness import Query


class HealthyPanicThresholdTest(AmbassadorTest):
    target: ServiceType

    def init(self):
        self.target = HTTP()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-default
hostname: "*"
prefix: /{self.name}-default/
service: {self.target.path.fqdn}
resolver: endpoint
load_balancer:
  policy: round_robin
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-25percent
hostname: "*"
prefix: /{self.name}-25percent/
service: {self.target.path.fqdn}
resolver: endpoint
load_balancer:
  policy: round_robin
  healthy_panic_threshold: 25.0
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-0percent
hostname: "*"
prefix: /{self.name}-0percent/
service: {self.target.path.fqdn}
resolver: endpoint
load_balancer:
  policy: round_robin
  healthy_panic_threshold: 0.0
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-100percent
hostname: "*"
prefix: /{self.name}-100percent/
service: {self.target.path.fqdn}
resolver: endpoint
load_balancer:
  policy: round_robin
  healthy_panic_threshold: 100.0
"""
        )

    def queries(self):
        yield Query(self.url(self.name + "-default/"))
        yield Query(self.url(self.name + "-25percent/"))
        yield Query(self.url(self.name + "-0percent/"))
        yield Query(self.url(self.name + "-100percent/"))

    def check(self):
        for result in self.results:
            assert result.status == 200

    def requirements(self):
        yield ("url", Query(self.url("ambassador/v0/diag/?json=true&filter=errors")))
        yield ("url", Query(self.url("ambassador/v0/diag/?json=true&filter=clusters")))
