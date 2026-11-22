import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlparse,parse_qs
from ont.integrations.coding import publish_draft
from ont.integrations.delivery import verify
from ont.integrations.identity import PKCE,Principals

class ReleaseIntegrationTests(unittest.TestCase):
    def result(self):return {'commit':'a'*40,'checkout':'/trusted/checkout','summary':'change','verification':{'passed':True,'commit':'a'*40}}
    def test_publish_blocks_missing_or_mismatched_verification_before_git(self):
        for evidence in [{},{'passed':False,'commit':'a'*40},{'passed':True,'commit':'b'*40}]:
            r=self.result();r['verification']=evidence
            with patch('ont.integrations.coding.command') as run,self.assertRaises(ValueError):publish_draft(r,'o/r',['o/r'],'ont/task','main','body.md')
            run.assert_not_called()
    def test_publish_blocks_wrong_remote_without_push(self):
        with patch('ont.integrations.coding.command',side_effect=['','a'*40,'https://github.com/other/repo.git']) as run,self.assertRaises(ValueError):
            publish_draft(self.result(),'o/r',['o/r'],'ont/task','main','body.md')
        self.assertFalse(any('push' in call.args[0][:2] for call in run.call_args_list))
    def test_publish_uses_authorized_explicit_remote(self):
        with patch('ont.integrations.coding.command',side_effect=['','a'*40,'https://github.com/o/r.git','']) as run,patch('ont.integrations.coding.GitHubDelivery.draft_pr',return_value={'url':'example','created':True}):
            self.assertTrue(publish_draft(self.result(),'o/r',['o/r'],'ont/task','main','body.md')['created'])
        self.assertEqual(run.call_args_list[-1].args[0],['git','push','https://github.com/o/r.git','a'*40+':refs/heads/ont/task'])
    def test_verifier_rejects_malformed_digest_before_docker(self):
        with tempfile.TemporaryDirectory() as tmp,patch('ont.integrations.delivery.command',side_effect=['a'*40,'']),patch('ont.integrations.delivery.subprocess.run') as docker,self.assertRaises(ValueError):
            verify(tmp,'a'*40,'image@sha256:not-a-digest',['test'])
        docker.assert_not_called()
    def test_authentication_requires_bearer_scheme(self):
        p=Principals({'a'*40:{'tenant':'one','role':'admin'}})
        for value in ['a'*40,'Basic '+'a'*40]:
            with self.assertRaises(PermissionError):p.authenticate(value)
        self.assertEqual(p.authenticate('Bearer '+'a'*40)['tenant'],'one')
    def test_oauth_preserves_existing_query_and_replaces_reserved_fields(self):
        p=PKCE();url=p.begin('https://id.example/auth?audience=ont&state=attacker','client','https://ont.example/callback','openid')
        query=parse_qs(urlparse(url).query)
        self.assertEqual(query['audience'],['ont']);self.assertEqual(len(query['state']),1);self.assertNotEqual(query['state'],['attacker'])
        self.assertTrue(p.consume(query['state'][0]))
