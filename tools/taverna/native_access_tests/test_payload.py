"""NP-05/06: actual iOS core and official peer, fresh state for every test."""
import hashlib
import os
import time
import unittest
import uuid
from urllib.parse import parse_qs, urlsplit

from payload_session import PayloadSession


class NativePayload(unittest.TestCase):
    def setUp(self):
        self.s = PayloadSession(self)
        self.addCleanup(self.s.close)
        self.s.start()

    def test_01_exact_messages_both_directions(self):
        s = self.s
        invitation = s.app('/_connect 1')
        self.assertEqual(invitation['type'], 'invitation')
        joined = s.peer('/connect '+invitation['connLinkInvitation']['connFullLink'])
        self.assertEqual(joined['type'], 'sentConfirmation')
        s.wait(lambda: len(s.app('/contacts').get('contacts', [])) == 1 and
               len(s.peer('/contacts').get('contacts', [])) == 1, 30, 'mutual contact')
        for sender, receiver, target, source in [(s.app, s.peer, 'Proof-bob', 'Native-proof'),
                                                 (s.peer, s.app, 'Native-proof', 'Proof-bob')]:
            text = 'Taverna fixture '+uuid.uuid4().hex
            s.wait(lambda: sender('@'+target+' '+text)['type'] == 'newChatItems', 15, 'send')
            expected = {'type': 'rcvMsgContent', 'msgContent': {'type': 'text', 'text': text}}
            def received():
                values = s.contents(receiver('/tail @'+source+' 20'))
                return expected in values
            s.wait(received, 30, 'exact received message')
            self.assertIn(expected, s.contents(receiver('/tail @'+source+' 20')))
        s.record('exact_messages_both_directions')

    def test_02_exact_files_both_directions(self):
        s = self.s
        for sender, receiver, who, other in [(s.app, s.peer, 'ios', 'bob'),
                                            (s.peer, s.app, 'bob', 'ios')]:
            payload = os.urandom(2*1024*1024+137)
            name = 'payload-'+uuid.uuid4().hex+'.bin'
            source = s.files(who)/name
            source.write_bytes(payload)
            sent = sender('/_upload 1 '+s.client_path(who, name))
            self.assertEqual(sent['type'], 'sndStandaloneFileCreated')
            file_id = sent['fileTransferMeta']['fileId']
            done = s.event(who, 'sndStandaloneFileComplete', file_id, 120)
            links = done['rcvURIs']
            self.assertIsInstance(links, list)
            self.assertGreater(len(links), 0)
            for link in links:
                parsed = urlsplit(link)
                self.assertEqual((parsed.scheme, parsed.path), ('simplex', '/file'))
                self.assertTrue(parse_qs(parsed.fragment.removeprefix('/?')).get('desc'))
            dest_name = 'received-'+name
            downloaded = receiver('/_download 1 '+done['rcvURIs'][0]+' '+s.client_path(other, dest_name))
            self.assertEqual(downloaded['type'], 'rcvStandaloneFileCreated')
            s.event(other, 'rcvStandaloneFileComplete', downloaded['rcvFileTransfer']['fileId'], 120)
            received = s.files(other)/dest_name
            self.assertTrue(received.is_file())
            self.assertEqual(received.read_bytes(), payload)
            s.evidence.append({'check': 'exact_file', 'sender': who, 'receiver': other,
                               'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
        s.record('exact_files_both_directions')

    def test_03_revocation_during_file(self):
        self.assert_interruption('revoke')

    def test_04_missing_authorization_during_file(self):
        self.assert_interruption('missing')

    def assert_interruption(self, mode):
        s = self.s
        payload = os.urandom(32*1024*1024+73)
        name = 'inflight-'+uuid.uuid4().hex+'.bin'
        (s.files('ios')/name).write_bytes(payload)
        sent = s.app('/_upload 1 '+s.client_path('ios', name))
        self.assertEqual(sent['type'], 'sndStandaloneFileCreated')
        file_id = sent['fileTransferMeta']['fileId']
        progress = s.event('ios', 'sndFileProgressXFTP', file_id, 120,
                           predicate=lambda x: 0 < x['sentSize'] < x['totalSize'])
        self.assertGreater(progress['sentSize'], 0)
        self.assertLess(progress['sentSize'], progress['totalSize'])
        active = s.active_connections()
        self.assertTrue(any(x['protocol'] == 'xftp' for x in active))
        started = time.monotonic()
        s.deny(mode)
        s.wait(lambda: s.closed_by_authorization(active), 60, 'all pre-existing streams closed')
        elapsed = time.monotonic()-started
        self.assertLessEqual(elapsed, 60)
        # Both new real protocol tests must fail while the authority denies this device.
        for protocol in ('smp', 'xftp'):
            tested = s.app('test:'+protocol)
            self.assertIs(tested['failed'], True)
        self.assertFalse(any(x['type'] == 'sndStandaloneFileComplete' and x.get('fileId') == file_id
                             for x in s.events('ios')))
        self.assertTrue(any(x['event'] == 'denied_before_backend' for x in s.audit()))
        s.evidence.append({'check': mode+'_inflight', 'sent_before': progress['sentSize'],
                           'total': progress['totalSize'], 'cutoff_seconds': elapsed,
                           'new_smp_denied': True, 'new_xftp_denied': True})
        s.record(mode+'_inflight')

    def test_05_reachable_sentinel_no_direct_fallback(self):
        s = self.s
        with s.sentinel() as sentinel:
            sentinel.positive_control()
            self.assertEqual(sentinel.count, 1)
            tested = s.app('sentinel:'+str(sentinel.port))
            self.assertIs(tested['failed'], True)
            time.sleep(.3)
            self.assertEqual(sentinel.count, 1, 'unauthorized direct connection reached sentinel')
        s.record('sentinel_no_direct_fallback')


if __name__ == '__main__':
    unittest.main(verbosity=2)
