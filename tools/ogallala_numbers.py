"""Own calculations for the ogallala-aquifer episode, from the figures in its research.md."""
STORAGE_2019_MAF = 2910.0  # R1: recoverable water in storage in 2019, 2.91 billion acre-feet
LOST_MAF = 286.4  # R1: decline since predevelopment (about 1950)
AVG_DECLINE_FT = 16.5  # R1: area-weighted average
MAX_DECLINE_FT = 265.0  # R1: largest decline at a single well
LAKE_MEAD_FULL_MAF = 26.1  # episodes/colorado-river research; check there before use on screen
PUMP_CUT, YEARS = 0.05, 20  # R6: 5 % a year for 20 years

before = STORAGE_2019_MAF + LOST_MAF
print(f"share of the aquifer's water gone: {LOST_MAF / before:.1%} ({LOST_MAF} of {before:.1f} million acre-feet)")
print(f"worst well against the average: {MAX_DECLINE_FT / AVG_DECLINE_FT:.0f} x")
print(f"water lost in full Lake Meads: {LOST_MAF / LAKE_MEAD_FULL_MAF:.1f}")
print(f"5 % of the previous year, compounded {YEARS} years: {1 - (1 - PUMP_CUT) ** YEARS:.1%} less; "
      f"5 % of today's pumping every year would be {PUMP_CUT * YEARS:.0%}")
print(f"27.7 % as an average of the two readings is not assumed; the district's own figure is quoted (R6)")
