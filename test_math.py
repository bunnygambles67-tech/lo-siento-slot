from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from math.lo_siento_math_v01 import *

def test_28_paylines(): assert len(PAYLINES_DEF)==28
def test_bonus_triggers():
    assert choose_bonus(2) is None
    assert choose_bonus(3)=="REGULAR"
    assert choose_bonus(4)=="SUPER"
    assert choose_bonus(5)=="EPIC"
def test_cap(): assert spin(seed=123)["win"] <= MAX_WIN
