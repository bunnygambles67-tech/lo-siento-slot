# Math Notes

The first rough prototype previously produced ~27.8% RTP, showing that the
feature economy is nowhere near final. Do not call the 96% target achieved.

Tuning order:
1. Base reel strips/weights.
2. Scatter frequency.
3. Regular/Super/Epic feature EV.
4. Collector and prize frequencies.
5. Multiplier ladders.
6. Retriggers/redrops.
7. Bonus Buy pricing.
8. Mystery EV.
9. Large simulations (tens/hundreds of millions).
10. Independent math/RNG audit.

Enforce `min(win, 50000 * bet)` at every payout boundary.
