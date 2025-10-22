from typing import TYPE_CHECKING

from ..config import Config
from .irresource import IRResource

if TYPE_CHECKING:
    from .ir import IR  # pragma: no cover


class IRRetryPolicy(IRResource):
    def __init__(
        self,
        ir: "IR",
        aconf: Config,
        rkey: str = "ir.retrypolicy",
        kind: str = "IRRetryPolicy",
        name: str = "ir.retrypolicy",
        **kwargs
    ) -> None:
        # print("IRRetryPolicy __init__ (%s %s %s)" % (kind, name, kwargs))

        super().__init__(ir=ir, aconf=aconf, rkey=rkey, kind=kind, name=name, **kwargs)

    def setup(self, ir: "IR", aconf: Config) -> bool:
        if not self.validate_retry_policy():
            self.post_error("Invalid retry policy specified: {}".format(self))
            return False

        return True

    def validate_retry_policy(self) -> bool:
        retry_on = self.get("retry_on", None)
        retry_grpc_on = self.get("retry_grpc_on", None)

        # At least one of retry_on or retry_grpc_on should be specified
        if not retry_on and not retry_grpc_on:
            return False

        is_valid = True

        # Validate retry_on if specified
        if retry_on and retry_on not in {
            "5xx",
            "gateway-error",
            "connect-failure",
            "retriable-4xx",
            "refused-stream",
            "retriable-status-codes",
        }:
            is_valid = False

        # Validate retry_grpc_on if specified
        if retry_grpc_on and retry_grpc_on not in {
            "cancelled",
            "deadline-exceeded",
            "internal",
            "resource-exhausted",
            "unavailable",
        }:
            is_valid = False

        return is_valid

    def as_dict(self) -> dict:
        raw_dict = super().as_dict()

        for key in list(raw_dict):
            if key in [
                "_active",
                "_errored",
                "_referenced_by",
                "_rkey",
                "kind",
                "location",
                "name",
                "namespace",
                "metadata_labels",
            ]:
                raw_dict.pop(key, None)

        # Combine retry_on and retry_grpc_on into a single retry_on field for Envoy
        retry_on = raw_dict.get("retry_on", "")
        retry_grpc_on = raw_dict.get("retry_grpc_on", "")

        if retry_on and retry_grpc_on:
            # Both are specified, combine them with a comma
            raw_dict["retry_on"] = f"{retry_on},{retry_grpc_on}"
        elif retry_grpc_on:
            # Only gRPC retry conditions specified
            raw_dict["retry_on"] = retry_grpc_on
        # If only retry_on is specified, it's already in the dict

        # Remove the separate retry_grpc_on field since Envoy expects everything in retry_on
        raw_dict.pop("retry_grpc_on", None)

        return raw_dict
