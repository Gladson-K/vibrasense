import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "software"))
from models import AlarmFSM

def test_escalation():
    f = AlarmFSM()
    assert f.state == "OK"
    f.step(1, 3.0); assert f.state == "WATCH"
    f.step(4, 4.5); f.step(4, 4.5); f.step(4, 4.5)
    assert f.state == "ALARM"

def test_votes_alone_raise_alarm():
    f = AlarmFSM()
    f.step(3, 2.0); f.step(3, 2.0); f.step(3, 2.0)   # 3-feature vote
    assert f.state == "ALARM"

def test_auto_clear():
    f = AlarmFSM()
    for _ in range(3): f.step(4, 5.0)
    assert f.state == "ALARM"
    f.normal_since = time.time() - 1900
    f.step(0, 0.0)
    assert f.state == "OK"
