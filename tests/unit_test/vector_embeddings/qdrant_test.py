import os

from unittest import mock
from mongoengine import connect

import pytest

from kairon import Utility
from kairon.exceptions import AppException
from kairon.shared.actions.exception import ActionFailure
from kairon.shared.actions.utils import ActionUtility
from kairon.shared.admin.constants import BotSecretType
from kairon.shared.admin.data_objects import BotSecrets
from kairon.shared.data.data_objects import LLMSettings
from kairon.shared.vector_embeddings.db.factory import VectorEmbeddingsDbFactory
from kairon.shared.vector_embeddings.db.qdrant import Qdrant
import litellm
from kairon.shared.llm.processor import LLMProcessor
import numpy as np

class TestQdrant:

    @pytest.fixture(autouse=True, scope="class")
    def init_connection(self):
        os.environ["system_file"] = "./tests/testing_data/system.yaml"
        Utility.load_environment()
        connect(**Utility.mongoengine_connection(Utility.environment['database']["url"]))

    @pytest.mark.asyncio
    @mock.patch.dict(Utility.environment, {'vector': {"key": "TEST", 'db': 'http://localhost:6333'}})
    @mock.patch.object(litellm, "aembedding", autospec=True)
    @mock.patch.object(ActionUtility, "execute_http_request", autospec=True)
    async def test_embedding_search_valid_request_body(self, mock_http_request, mock_embedding):
        embedding = list(np.random.random(LLMProcessor.__embedding__))
        user = "test"
        Utility.load_environment()
        secret = BotSecrets(secret_type=BotSecretType.gpt_key.value, value="key_value", bot="5f50fd0a56v098ca10d75d2g",
                            user="user").save()
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        request_body = {"ids": [0], "with_payload": True, "with_vector": True, 'text': "Hi"}
        mock_http_request.return_value = 'expected_result'
        mock_embedding.return_value = {'data': [{'embedding': embedding}]}
        result = await qdrant.embedding_search(request_body, user=user)
        assert result == 'expected_result'

    @pytest.mark.asyncio
    @mock.patch.object(ActionUtility, "execute_http_request", autospec=True)
    async def test_payload_search_valid_request_body(self, mock_http_request):
        Utility.load_environment()
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        request_body = {"filter": {"should": [{"key": "city", "match": {"value": "London"}},
                                              {"key": "color", "match": {"value": "red"}}]}}
        mock_http_request.return_value = 'expected_result'
        result = await qdrant.payload_search(request_body, user="test")
        assert result == 'expected_result'

    @pytest.mark.asyncio
    @mock.patch.object(ActionUtility, "execute_http_request", autospec=True)
    async def test_perform_operation_valid_op_type_and_request_body(self, mock_http_request):
        Utility.load_environment()
        user = "test"
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        request_body = {}
        mock_http_request.return_value = 'expected_result'
        result_embedding = await qdrant.perform_operation('embedding_search', request_body, user=user)
        assert result_embedding == 'expected_result'
        result_payload = await qdrant.perform_operation('payload_search', request_body, user=user)
        assert result_payload == 'expected_result'

    @pytest.mark.asyncio
    async def test_embedding_search_empty_request_body(self):
        Utility.load_environment()
        user = "test"
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        with pytest.raises(ActionFailure):
            await qdrant.embedding_search({}, user=user)

    @pytest.mark.asyncio
    async def test_payload_search_empty_request_body(self):
        Utility.load_environment()
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        with pytest.raises(ActionFailure):
            await qdrant.payload_search({}, user="test")

    @pytest.mark.asyncio
    async def test_perform_operation_invalid_op_type(self):
        Utility.load_environment()
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        request_body = {}
        with pytest.raises(AppException, match="Operation type not supported"):
            await qdrant.perform_operation("vector_search", request_body, user="test")

    def test_get_instance_raises_exception_when_db_not_implemented(self):
        with pytest.raises(AppException, match="Database not yet implemented!"):
            VectorEmbeddingsDbFactory.get_instance("mongo")

    @pytest.mark.asyncio
    @mock.patch.object(ActionUtility, "execute_http_request", autospec=True)
    async def test_embedding_search_valid_request_body_payload(self, mock_http_request):
        Utility.load_environment()
        qdrant = Qdrant('5f50fd0a56v098ca10d75d2g', '5f50fd0a56v098ca10d75d2g',
                        LLMSettings(provider="openai").to_mongo().to_dict())
        request_body = {'ids': [0], 'with_payload': True, 'with_vector': True}
        mock_http_request.return_value = 'expected_result'
        result = await qdrant.embedding_search(request_body, user="test")
        assert result == 'expected_result'

        mock_http_request.assert_called_once()
        called_args = mock_http_request.call_args
        called_payload = called_args.kwargs['request_body']
        assert called_payload == request_body
        assert called_args.kwargs['http_url'] == 'http://localhost:6333/collections/5f50fd0a56v098ca10d75d2g/points'
        assert called_args.kwargs['request_method'] == 'POST'
