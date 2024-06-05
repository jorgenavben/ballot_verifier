from unittest.mock import MagicMock

import pytest
import falcon
from falcon import testing
from keri.app import habbing

from verifier.verify import setupVerifier

test_oobi_params = {
    "oobi" : "sample_oobi"
}

test_verify_params = {
    "aid": "sample_aid",
    "signature": "sample_signature",
    "payload": "sample_payload"
}

@pytest.fixture
def client():
    with habbing.openHab(name="test", transferable=True, temp=True, salt=b'0123456789abcdef') as (hby, hab):
        app, doers = setupVerifier(hby, hab)
        test_client = testing.TestClient(app)
        test_client.hby = hby
        test_client.hab = hab
        return test_client

def test_get_oobi(client):
    mock_get = MagicMock()
    mock_get.return_value = MagicMock(cid="sample_cid")
    client.hby.db.roobi.get = mock_get

    response = client.simulate_get('/oobi', json=test_oobi_params)

    assert response.status == falcon.HTTP_200
    assert response.text == 'sample_cid'

def test_get_oobi_not_found(client):
    mock_get = MagicMock()
    mock_get.return_value = None
    client.hby.db.roobi.get = mock_get

    response = client.simulate_get('/oobi', json=test_oobi_params)

    assert response.status == falcon.HTTP_404

def test_post_oobi(client):
    response = client.simulate_post('/oobi', json=test_oobi_params)

    assert response.status == falcon.HTTP_202
    client.hby.db.oobis.put.assert_called_once()

def test_post_verify_success(client):
    client.hab = MagicMock()
    kever = MagicMock()
    kever.verfers = [MagicMock()]
    kever.verfers[0].verify.return_value = True
    client.hab.kevers = {'sample_aid': kever}

    response = client.simulate_post('/verify', json=test_verify_params)

    assert response.status == falcon.HTTP_200
    assert response.text == 'Verification successful'

def test_post_verify_unknown_aid(client):
    client.hab = MagicMock()
    client.hab.kevers = {}

    response = client.simulate_post('/verify', json=test_verify_params)

    assert response.status == falcon.HTTP_404
    assert 'Unknown AID' in response.text

def test_post_verify_invalid_signature(client):
    client.hab = MagicMock()
    kever = MagicMock()
    kever.verfers = [MagicMock()]
    kever.verfers[0].verify.return_value = False
    client.hab.kevers = {'sample_aid': kever}

    response = client.simulate_post('/verify', json=test_verify_params)

    assert response.status == falcon.HTTP_400
    assert 'Signature is invalid' in response.text

def test_post_verify_invalid_signature_format(client):
    client.hab = MagicMock()
    kever = MagicMock()
    kever.verfers = [MagicMock()]
    client.hab.kevers = {'sample_aid': kever}

    response = client.simulate_post('/verify', json=test_verify_params)

    assert response.status == falcon.HTTP_400
    assert 'Invalid signature format' in response.text