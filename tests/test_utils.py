from socks5_tune.model import TunnelInfo


def test_version():
    info = TunnelInfo()
    assert info.status.restarts == 0
    assert info.status.last_msg == ''
