from functools import wraps
from typing import Dict, Tuple, Optional

from grpc._channel import _InactiveRpcError

from pinecone import Config
from .utils import _generate_request_id
from .config import GRPCClientConfig
from pinecone.utils.constants import REQUEST_ID, CLIENT_VERSION
from pinecone.exceptions.exceptions import PineconeException
from grpc import CallCredentials, Compression
from google.protobuf.message import Message
from pinecone.openapi_support.api_version import API_VERSION


class GrpcRunner:
    def __init__(self, index_name: str, config: Config, grpc_config: GRPCClientConfig):
        self.config = config
        self.grpc_client_config = grpc_config

        # Avoid unnecessary dict.copy()/update in hot call path by merging metadata at construction time if static
        self.fixed_metadata = {
            "api-key": config.api_key,
            "service-name": index_name,
            "client-version": CLIENT_VERSION,
            "x-pinecone-api-version": API_VERSION,
        }
        if self.grpc_client_config.additional_metadata:
            self.fixed_metadata.update(self.grpc_client_config.additional_metadata)

    def run(
        self,
        func,
        request: Message,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        credentials: Optional[CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[Compression] = None,
    ):
        user_provided_metadata = metadata or {}
        _metadata = self._prepare_metadata(user_provided_metadata)
        try:
            return func(
                request,
                timeout=timeout,
                metadata=_metadata,
                credentials=credentials,
                wait_for_ready=wait_for_ready,
                compression=compression,
            )
        except _InactiveRpcError as e:
            raise PineconeException(e._state.debug_error_string) from e

    async def run_asyncio(
        self,
        func,
        request: Message,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        credentials: Optional[CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[Compression] = None,
    ):
        @wraps(func)
        async def wrapped():
            user_provided_metadata = metadata or {}
            _metadata = self._prepare_metadata(user_provided_metadata)
            try:
                return await func(
                    request,
                    timeout=timeout,
                    metadata=_metadata,
                    credentials=credentials,
                    wait_for_ready=wait_for_ready,
                    compression=compression,
                )
            except _InactiveRpcError as e:
                raise PineconeException(e._state.debug_error_string) from e

        return await wrapped()

    def _prepare_metadata(
        self, user_provided_metadata: Dict[str, str]
    ) -> Tuple[Tuple[str, str], ...]:
        return tuple(
            (k, v)
            for k, v in {
                **self.fixed_metadata,
                **self._request_metadata(),
                **user_provided_metadata,
            }.items()
        )

    def _request_metadata(self) -> Dict[str, str]:
        return {REQUEST_ID: _generate_request_id()}

    def _prepare_metadata(self, user_metadata: Dict[str, str]) -> Dict[str, str]:
        """Efficiently merge fixed metadata with possibly empty user metadata dict."""
        if not user_metadata:
            # user metadata empty or not provided, return fixed_metadata as-is
            return self.fixed_metadata
        # Fast path: Avoid double dict copying if user_metadata is small
        # Create a new dict and update user_metadata first, then fixed_metadata (fixed_metadata should override)
        merged_metadata = {}
        merged_metadata.update(user_metadata)
        merged_metadata.update(self.fixed_metadata)
        return merged_metadata
