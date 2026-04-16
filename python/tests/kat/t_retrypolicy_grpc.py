from typing import Generator, Tuple, Union

from abstract_tests import EGRPC, AmbassadorTest, Node, ServiceType
from kat.harness import Query


class RetryPolicyGrpcTest(AmbassadorTest):
    target: ServiceType

    def init(self):
        self.target = EGRPC()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}
hostname: "*"
prefix: /echo.EchoService/
rewrite: /echo.EchoService/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
retry_policy:
  retry_grpc_on: "unavailable"
  num_retries: 2
"""
        )

    def queries(self):
        # Test successful gRPC request
        yield Query(
            self.url("echo.EchoService/Echo"),
            headers={"content-type": "application/grpc", "kat-req-echo-requested-status": "0"},  # OK
            expected=200,
            grpc_type="real",
        )

        # Check diagnostics
        yield Query(self.url("ambassador/v0/diag/?json=true&filter=errors"), phase=2)

    def check(self):
        # Check that there are no errors in diagnostics
        errors = self.results[-1].json
        assert len(errors) == 0, f"Expected no errors, got: {errors}"

        # Verify the successful gRPC response
        assert self.results[0].headers.get("Grpc-Status") == ["0"], "Expected OK status for successful query"


class RetryPolicyGrpcModuleTest(AmbassadorTest):
    """Test retry_grpc_on at the Module level"""
    target: ServiceType

    def init(self):
        self.target = EGRPC()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Module
name: ambassador
config:
  retry_policy:
    retry_grpc_on: "resource-exhausted"
    num_retries: 2
"""
        )

        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-module-retry
hostname: "*"
prefix: /echo.EchoService/
rewrite: /echo.EchoService/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
"""
        )

    def queries(self):
        # Test successful request to verify module works
        yield Query(
            self.url("echo.EchoService/Echo"),
            headers={"content-type": "application/grpc", "kat-req-echo-requested-status": "0"},  # OK
            expected=200,
            grpc_type="real",
        )

        # Check diagnostics
        yield Query(self.url("ambassador/v0/diag/?json=true&filter=errors"), phase=2)

    def check(self):
        # Check that there are no errors in diagnostics
        errors = self.results[-1].json
        assert len(errors) == 0, f"Expected no errors, got: {errors}"

        # Verify successful request
        assert self.results[0].headers.get("Grpc-Status") == ["0"], "Expected OK status for successful query"
