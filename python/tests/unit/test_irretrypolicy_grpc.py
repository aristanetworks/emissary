from unittest.mock import MagicMock

from ambassador.config import Config
from ambassador.ir import IR
from ambassador.ir.irretrypolicy import IRRetryPolicy


class TestIRRetryPolicyGrpc:
    def setup_method(self):
        self.ir = MagicMock(spec=IR)
        self.ir.ambassador_namespace = "default"
        self.ir.logger = MagicMock()
        self.aconf = MagicMock(spec=Config)

    def test_retry_grpc_on_valid_values(self):
        """Test that valid gRPC retry conditions are accepted"""
        valid_grpc_conditions = [
            "cancelled",
            "deadline-exceeded", 
            "internal",
            "resource-exhausted",
            "unavailable"
        ]
        
        for condition in valid_grpc_conditions:
            policy = IRRetryPolicy(
                ir=self.ir,
                aconf=self.aconf,
                retry_grpc_on=condition
            )
            assert policy.validate_retry_policy() is True

    def test_retry_grpc_on_invalid_values(self):
        """Test that invalid gRPC retry conditions are rejected"""
        invalid_grpc_conditions = [
            "invalid-condition",
            "5xx",  # This is an HTTP condition, not gRPC
            "gateway-error",  # This is an HTTP condition, not gRPC
            "unknown"
        ]
        
        for condition in invalid_grpc_conditions:
            policy = IRRetryPolicy(
                ir=self.ir,
                aconf=self.aconf,
                retry_grpc_on=condition
            )
            assert policy.validate_retry_policy() is False

    def test_retry_on_and_retry_grpc_on_both_valid(self):
        """Test that both HTTP and gRPC retry conditions can be specified together"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_on="5xx",
            retry_grpc_on="unavailable"
        )
        assert policy.validate_retry_policy() is True

    def test_retry_on_valid_retry_grpc_on_invalid(self):
        """Test that invalid gRPC condition fails validation even with valid HTTP condition"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_on="5xx",
            retry_grpc_on="invalid-grpc-condition"
        )
        assert policy.validate_retry_policy() is False

    def test_retry_on_invalid_retry_grpc_on_valid(self):
        """Test that invalid HTTP condition fails validation even with valid gRPC condition"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_on="invalid-http-condition",
            retry_grpc_on="unavailable"
        )
        assert policy.validate_retry_policy() is False

    def test_neither_retry_condition_specified(self):
        """Test that at least one retry condition must be specified"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            num_retries=3
        )
        assert policy.validate_retry_policy() is False

    def test_as_dict_combines_retry_conditions(self):
        """Test that as_dict() combines retry_on and retry_grpc_on into single retry_on field"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_on="5xx",
            retry_grpc_on="unavailable",
            num_retries=3
        )
        
        result = policy.as_dict()
        
        # Should combine both conditions
        assert result["retry_on"] == "5xx,unavailable"
        # Should not have separate retry_grpc_on field
        assert "retry_grpc_on" not in result
        # Should preserve other fields
        assert result["num_retries"] == 3

    def test_as_dict_only_retry_on(self):
        """Test that as_dict() works with only retry_on specified"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_on="gateway-error",
            num_retries=2
        )
        
        result = policy.as_dict()
        
        # Should keep only retry_on
        assert result["retry_on"] == "gateway-error"
        assert "retry_grpc_on" not in result
        assert result["num_retries"] == 2

    def test_as_dict_only_retry_grpc_on(self):
        """Test that as_dict() works with only retry_grpc_on specified"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_grpc_on="cancelled",
            num_retries=1
        )
        
        result = policy.as_dict()
        
        # Should move retry_grpc_on to retry_on
        assert result["retry_on"] == "cancelled"
        assert "retry_grpc_on" not in result
        assert result["num_retries"] == 1

    def test_as_dict_removes_internal_fields(self):
        """Test that as_dict() removes internal fields"""
        policy = IRRetryPolicy(
            ir=self.ir,
            aconf=self.aconf,
            retry_grpc_on="internal",
            _active=True,
            _errored=False,
            kind="IRRetryPolicy"
        )
        
        result = policy.as_dict()
        
        # Should remove internal fields
        assert "_active" not in result
        assert "_errored" not in result
        assert "kind" not in result
        # Should keep retry condition
        assert result["retry_on"] == "internal"
