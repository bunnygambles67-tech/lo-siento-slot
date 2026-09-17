"""
Lo Siento! Slot - math prototype v0.1
Original gameplay/math prototype. Not a certified gambling engine.
"""
from __future__ import annotations
import json, random
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

MAX_WIN = 50_000.0
RTP_TARGET = 0.96
REELS, ROWS, PAYLINES = 5, 6, 28

PAYTABLE = {
    "FEATHER": (0.10,0.20,0.40), "CORN": (0.10,0.20,0.50),
    "BUCKET": (0.10,0.25,0.70), "SLIPPER": (0.20,0.50,1.00),
    "PHONE": (0.75,1.50,3.00), "WAVE": (1.00,2.00,4.00),
    "BOAT": (1.25,2.50,6.00), "MAN": (1.50,3.00,8.00),
    "HEN": (2.00,5.00,15.00),
}
SYMBOLS = list(PAYTABLE) + ["WILD","SCATTER"]
WEIGHTS = [18,15,12,10,5,4,3,2.5,1.5,1.5,0.8]
PRIZES = [1,2,3,5,10,25,50,100,250,500,1000,2500,5000,10000,25000,50000]
PRIZE_WEIGHTS = [36,25,15,9,6,3.5,2,1.2,0.7,0.35,0.15,0.06,0.025,0.01,0.003,0.0002]

PAYLINES_DEF = [
[3,3,3,3,3],[2,2,2,2,2],[4,4,4,4,4],[1,1,1,1,1],[5,5,5,5,5],[6,6,6,6,6],
[2,3,4,3,2],[4,3,2,3,4],[1,2,3,2,1],[5,4,3,4,5],[3,2,1,2,3],[3,4,5,4,3],
[2,1,2,1,2],[4,5,4,5,4],[1,3,1,3,1],[6,4,6,4,6],[2,4,2,4,2],[5,3,5,3,5],
[1,2,4,2,1],[6,5,3,5,6],[2,3,5,3,2],[5,4,2,4,5],[1,3,5,3,1],[6,4,2,4,6],
[3,1,3,1,3],[4,6,4,6,4],[2,5,2,5,2],[5,2,5,2,5]
]

MULTIPLIERS = {
"BASE":[2,3,5,10,25,50,100],
"REGULAR":[2,3,5,10,15,25,50,100,250,500],
"SUPER":[5,10,15,25,50,100,250,500,1000,2500],
"EPIC":[10,25,50,100,250,500,1000,2500,5000,10000,25000,50000]}
GLOBAL_MULT = {"BASE":[2,3,5],"REGULAR":[2,3,5,10],"SUPER":[3,5,10,15],"EPIC":[5,10,25,50,100]}
BONUS_SPINS = {"REGULAR":8,"SUPER":12,"EPIC":16}

@dataclass
class Prize:
    value: float
    collected: bool=False

@dataclass
class FeatureState:
    mode: str
    spins_left: int
    global_mult: int=1
    collection_mult: int=1
    prizes: List[Prize]=field(default_factory=list)

def weighted_symbol(rng):
    return rng.choices(SYMBOLS, weights=WEIGHTS, k=1)[0]

def weighted_prize(rng):
    return float(rng.choices(PRIZES, weights=PRIZE_WEIGHTS, k=1)[0])

def make_grid(rng):
    return [[weighted_symbol(rng) for _ in range(ROWS)] for _ in range(REELS)]

def count_scatter(grid):
    return sum(c=="SCATTER" for reel in grid for c in reel)

def line_symbol_win(symbols):
    best_symbol, best_count = None, 0
    for symbol in PAYTABLE:
        count = 0
        for cell in symbols:
            if cell == symbol or cell == "WILD":
                count += 1
            else:
                break
        if count >= 3 and count > best_count:
            best_symbol, best_count = symbol, count
    return best_symbol, best_count

def base_line_wins(grid, bet=1.0):
    total=0.0
    for line in PAYLINES_DEF:
        cells=[grid[col][row-1] for col,row in enumerate(line)]
        symbol,count=line_symbol_win(cells)
        if symbol:
            total += PAYTABLE[symbol][count-3]*bet
    return total

def spawn_prizes(rng, mode):
    checks={"BASE":2,"REGULAR":5,"SUPER":8,"EPIC":12}[mode]
    chance={"BASE":.035,"REGULAR":.075,"SUPER":.12,"EPIC":.20}[mode]
    return [Prize(weighted_prize(rng)) for _ in range(checks) if rng.random()<chance]

def collector_event(state, rng):
    if not state.prizes: return 0.0
    effective=state.collection_mult+state.global_mult-1
    total=sum(p.value*effective for p in state.prizes)
    state.prizes.clear()
    return total

def choose_bonus(scatter_count):
    if scatter_count>=5: return "EPIC"
    if scatter_count==4: return "SUPER"
    if scatter_count==3: return "REGULAR"
    return None

def mystery_bonus(rng):
    return rng.choices([None,"REGULAR","SUPER","EPIC"],weights=[72,20,7,1],k=1)[0]

def upgrade_value(value):
    ladder=[1,2,3,5,10,25,50,100,250,500,1000,2500,5000,10000,25000,50000]
    return float(ladder[min(ladder.index(value)+1,len(ladder)-1)]) if value in ladder else value

def run_bonus(mode, rng, bet=1.0):
    state=FeatureState(mode,BONUS_SPINS[mode])
    total=0.0
    ladder=MULTIPLIERS[mode]
    while state.spins_left:
        state.spins_left-=1
        grid=make_grid(rng)
        total += base_line_wins(grid,bet)
        state.prizes.extend(spawn_prizes(rng,mode))
        if rng.random()<{"REGULAR":.14,"SUPER":.22,"EPIC":.30}[mode]:
            state.collection_mult=rng.choice(ladder)
            if rng.random()<{"REGULAR":.12,"SUPER":.18,"EPIC":.28}[mode]:
                state.collection_mult=min(max(state.collection_mult,rng.choice([2,3,5,10,15,20])),ladder[-1])
            total += collector_event(state,rng)
        if rng.random()<{"REGULAR":.08,"SUPER":.13,"EPIC":.20}[mode]:
            state.global_mult=rng.choice(GLOBAL_MULT[mode])
        if state.prizes and rng.random()<{"REGULAR":.04,"SUPER":.08,"EPIC":.14}[mode]:
            for p in state.prizes: p.value=upgrade_value(p.value)
        if mode=="EPIC" and rng.random()<.10:
            state.collection_mult=max(state.collection_mult,rng.choice(ladder))
            total += collector_event(state,rng)
        if count_scatter(grid)>=3:
            state.spins_left += 2 if mode!="EPIC" else 3
        total=min(total,MAX_WIN*bet)
    return min(total,MAX_WIN*bet)

def spin(mode="BASE",seed=None,bet=1.0):
    rng=random.Random(seed)
    grid=make_grid(rng)
    line_win=base_line_wins(grid,bet)
    scatters=count_scatter(grid)
    bonus=choose_bonus(scatters)
    bonus_win=run_bonus(bonus,rng,bet) if bonus else 0.0
    mystery=None
    if mode=="BASE" and rng.random()<.002:
        mystery=mystery_bonus(rng)
        if mystery: bonus_win+=run_bonus(mystery,rng,bet)
    return {"grid":grid,"line_win":line_win,"scatters":scatters,"bonus":bonus,"mystery":mystery,
            "bonus_win":bonus_win,"win":min(line_win+bonus_win,MAX_WIN*bet)}

def run_sim(spins=100_000,mode="BASE",seed=7):
    rng=random.Random(seed); total=0.0; hits=0; max_win=0.0
    scat=Counter(); bonuses=Counter(); buckets=Counter()
    for _ in range(spins):
        grid=make_grid(rng); line=base_line_wins(grid); s=count_scatter(grid)
        b=choose_bonus(s); bw=run_bonus(b,rng) if b else 0.0
        win=min(line+bw,MAX_WIN); total+=win; max_win=max(max_win,win)
        scat[s]+=1; bonuses[b or "NONE"]+=1; hits += win>0
        if win==0:k="0"
        elif win<1:k="<1x"
        elif win<5:k="1-5x"
        elif win<25:k="5-25x"
        elif win<100:k="25-100x"
        elif win<500:k="100-500x"
        elif win<2500:k="500-2500x"
        elif win<10000:k="2500-10000x"
        else:k="10000x+"
        buckets[k]+=1
    return {"spins":spins,"rtp":total/spins,"hit_rate":hits/spins,"max_win":max_win,
            "scatter_distribution":dict(scat),"bonus_distribution":dict(bonuses),"win_distribution":dict(buckets)}

if __name__=="__main__":
    print(json.dumps(run_sim(100_000),indent=2))
