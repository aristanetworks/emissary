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
name:  {self.name}-grpc-retry
hostname: "*"
prefix: /{self.name}-grpc-retry/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
retry_policy:
  retry_grpc_on: "unavailable"
  num_retries: 2
"""
        )

        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-combined-retry
hostname: "*"
prefix: /{self.name}-combined-retry/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
retry_policy:
  retry_on: "5xx"
  retry_grpc_on: "cancelled"
  num_retries: 3
"""
        )

        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  {self.name}-normal
hostname: "*"
prefix: /{self.name}-normal/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
"""
        )

    def queries(self):
        # Test gRPC retry with unavailable status
        yield Query(
            self.url(f"{self.name}-grpc-retry/echo.EchoService/Echo"),
            headers={"content-type": "application/grpc", "kat-req-echo-requested-status": "14"},  # UNAVAILABLE
            expected=200,
            grpc_type="real",
        )

        # Test combined HTTP and gRPC retry
        yield Query(
            self.url(f"{self.name}-combined-retry/echo.EchoService/Echo"),
            headers={"content-type": "application/grpc", "kat-req-echo-requested-status": "1"},  # CANCELLED
            expected=200,
            grpc_type="real",
        )

        # Test normal request without retry
        yield Query(
            self.url(f"{self.name}-normal/echo.EchoService/Echo"),
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

        # Verify the gRPC responses
        assert self.results[0].headers.get("Grpc-Status") is not None
        assert self.results[1].headers.get("Grpc-Status") is not None
        assert self.results[2].headers.get("Grpc-Status") == ["0"]  # OK status


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
prefix: /{self.name}-module-retry/
service: {self.target.path.fqdn}
grpc: True
timeout_ms: 3000
"""
        )

    def queries(self):
        # Test that module-level gRPC retry policy is applied
        yield Query(
            self.url(f"{self.name}-module-retry/echo.EchoService/Echo"),
            headers={"content-type": "application/grpc", "kat-req-echo-requested-status": "8"},  # RESOURCE_EXHAUSTED
            expected=200,
            grpc_type="real",
        )

        # Check diagnostics
        yield Query(self.url("ambassador/v0/diag/?json=true&filter=errors"), phase=2)

    def check(self):
        # Check that there are no errors in diagnostics
        errors = self.results[-1].json
        assert len(errors) == 0, f"Expected no errors, got: {errors}"

        # Verify the gRPC response
        assert self.results[0].headers.get("Grpc-Status") is not None
