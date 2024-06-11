from unittest.mock import MagicMock, patch

import falcon
import pytest
from falcon import testing
from keri import kering

from verifier.verify import setupVerifier

oobi_params = {
    "oobi" : "sample_oobi"
}

verify_params = {
    "aid": "sample_aid",
    "signature": "sample_signature",
    "payload": "sample_payload"
}

invalid_params = {
    "invalid_param": "sample"
}

response_no_params = "empty JSON body"
response_missing_params = ["required field", "missing from request"]

@pytest.fixture
def mock_hby():
    # Mock the hby object
    mock = MagicMock()
    mock.db.roobi.get.return_value = None
    mock.db.oobis.put.return_value = None
    return mock
@pytest.fixture
def mock_hab():
    # Mock the hab object
    mock = MagicMock()
    mock.kevers = {}
    return mock

@pytest.fixture
def client(mock_hby, mock_hab):
    app, _ = setupVerifier(mock_hby, mock_hab)
    return testing.TestClient(app)

class TestOOBIEnd:
    def test_get_oobi(self, client, mock_hby):
        mock_get = MagicMock()
        mock_get.return_value = MagicMock(cid="sample_cid")
        mock_hby.db.roobi.get = mock_get

        response = client.simulate_get('/oobi', json=oobi_params)

        assert response.status == falcon.HTTP_200
        assert response.text == 'sample_cid'

    def test_get_oobi_not_found(self, client, mock_hby):
        mock_get = MagicMock()
        mock_get.return_value = None
        mock_hby.hby.db.roobi.get = mock_get

        response = client.simulate_get('/oobi', json=oobi_params)

        assert response.status == falcon.HTTP_404

    def test_get_oobi_no_params(self, client):
        response = client.simulate_get('/oobi')

        assert response.status == falcon.HTTP_400
        assert response_no_params in response.text

    def test_get_oobi_empty_params(self, client):
        response = client.simulate_get('/oobi', json={})

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text

    def test_get_oobi_invalid_params(self, client):
        response = client.simulate_get('/oobi', json=invalid_params)

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text

    def test_post_oobi(self, client, mock_hby):
        response = client.simulate_post('/oobi', json=oobi_params)

        # Retrieve the arguments that were passed to the put method
        kwargs = mock_hby.db.oobis.put.call_args.kwargs

        # Check the key and value arguments
        key = kwargs['keys'][0]
        value = kwargs['val']

        print(key, value)

        assert response.status == falcon.HTTP_202
        assert key == 'sample_oobi'
        from keri.db.basing import OobiRecord
        assert isinstance(value, OobiRecord)

    def test_post_oobi_no_params(self, client):
        response = client.simulate_post('/oobi')

        assert response.status == falcon.HTTP_400
        assert response_no_params in response.text

    def test_post_oobi_empty_params(self, client):
        response = client.simulate_post('/oobi', json={})

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text

    def test_post_oobi_invalid_params(self, client):
        response = client.simulate_post('/oobi', json=invalid_params)

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text

class TestVerificationEnd:
    def test_post_verify_success(self, client, mock_hab):
        mock_kever = MagicMock()
        mock_verfer = MagicMock()
        mock_verfer.verify.return_value = True
        mock_kever.verfers = [mock_verfer]
        mock_hab.kevers = {"sample_aid": mock_kever}

        with patch('keri.core.coring.Cigar', return_value=MagicMock(verfer=mock_verfer)):
            response = client.simulate_post('/verify', json=verify_params)

        assert response.status == falcon.HTTP_200
        assert response.text == 'Verification successful'

    def test_post_verify_unknown_aid(self, client, mock_hab):
        mock_hab.kevers = {}

        response = client.simulate_post('/verify', json=verify_params)

        assert response.status == falcon.HTTP_404
        assert "Unknown AID" in response.text

    def test_post_verify_invalid_signature(self, client, mock_hab):
        mock_kever = MagicMock()
        mock_verfer = MagicMock()
        mock_verfer.verify.return_value = False  # Simulate signature verification failure
        mock_kever.verfers = [mock_verfer]
        mock_hab.kevers = {"sample_aid": mock_kever}

        with patch('keri.core.coring.Cigar', return_value=MagicMock(verfer=mock_verfer)):
            response = client.simulate_post('/verify', json=verify_params)

        assert response.status == falcon.HTTP_400
        assert "Signature is invalid" in response.text

    def test_post_verify_invalid_signature_format(self, client):
        with patch('keri.core.coring.Cigar') as mock_cigar:
            mock_cigar.side_effect = kering.UnexpectedCodeError("Unsupported code =s.")

            response = client.simulate_post('/verify', json={**verify_params, 'signature': 'invalid'})

        assert response.status == falcon.HTTP_400
        assert "Invalid signature format" in response.text

    def test_post_verify_no_params(self, client):
        response = client.simulate_post('/verify')

        assert response.status == falcon.HTTP_400
        assert response_no_params in response.text

    def test_post_verify_empty_params(self, client):
        response = client.simulate_post('/verify', json={})

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text

    def test_post_verify_invalid_params(self, client):
        response = client.simulate_post('/verify', json=invalid_params)

        assert response.status == falcon.HTTP_400
        for substring in response_missing_params:
            assert substring in response.text