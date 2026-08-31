
import sys, os
sys.path.insert(0, 'D:/TrustShield')
sys.path.insert(0, 'D:/TrustShield/backend')

from fastapi.testclient import TestClient
from app.main import app

def run_contract_checks():
    client = TestClient(app)
    
    # 1. Health contract
    h = client.get('/health').json()
    assert h['status'] == 'ok'
    assert isinstance(h['ai_readiness'], dict)
    print('1. Health Contract: OK')
    
    # 2. Fresh session creation
    sess = client.post('/api/v1/sessions', json={'interaction_type': 'text', 'consent': True}).json()
    s_id = sess['session_id']
    assert s_id
    print('2. Session Creation: OK')
    
    # 3. WebSocket contract test with adversarial bank OTP
    with client.websocket_connect(f'/api/v1/sessions/{s_id}/stream') as ws:
        start_evt = ws.receive_json()
        assert start_evt['type'] == 'SESSION_STARTED'
        
        # Send text
        ws.send_json({'action': 'send_text', 'text': 'This is your bank manager. Your account will be blocked. Tell me the OTP immediately.'})
        
        events = []
        for _ in range(5):
            e = ws.receive_json()
            events.append(e)
            
        types = [e['type'] for e in events]
        assert 'TEXT_RECEIVED' in types
        assert 'SIGNAL_UPDATE' in types
        assert 'RISK_UPDATE' in types
        assert 'CLAIM_VERIFICATION' in types
        assert 'PROTECTION_UPDATE' in types
        
        # Verify policy violations structure
        risk_evt = next(e for e in events if e['type'] == 'RISK_UPDATE')
        pols = risk_evt['payload'].get('safety_policy_violations', [])
        assert len(pols) > 0
        assert isinstance(pols[0], dict)
        assert 'policy_id' in pols[0]
        assert 'reason' in pols[0]
        print('3. WebSocket Event & Policy Object Contract: OK')

    # 4. Rythu Bharosa verification
    sess2 = client.post('/api/v1/sessions', json={'interaction_type': 'text', 'consent': True}).json()
    s_id2 = sess2['session_id']
    with client.websocket_connect(f'/api/v1/sessions/{s_id2}/stream') as ws:
        ws.receive_json() # start
        ws.send_json({'action': 'send_text', 'text': 'Telangana Rythu Bharosa payment released. Pay fee and tell me your OTP.'})
        events2 = [ws.receive_json() for _ in range(5)]
        claim_evt = next(e for e in events2 if e['type'] == 'CLAIM_VERIFICATION')
        assert claim_evt['payload']['entity']['name'] == 'Telangana Rythu Bharosa'
        assert claim_evt['payload']['verification']['overall_status'] in ['VERIFIED', 'NOT_VERIFIED', 'CONTRADICTED']
        print('4. Rythu Bharosa Contract: OK')
        
    print('ALL RUNTIME CONTRACT TESTS PASSED!')

if __name__ == '__main__':
    run_contract_checks()
