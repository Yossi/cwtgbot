from collections import namedtuple

SES_EPOCH_00000 = 377_449_632_000
SES_EPOCH_09984 = 62_385_292_800

SES_LENGTH_OF = { # in seconds
  "128-CYCLE": 4_039_286_400,
  "4-CYCLE": 126_230_400,
  "COMMON_YEAR": 31_536_000,
  "COMMON_SEASON": 7_862_400,
  "WEEK": 604_800,
  "DAY": 86_400
}

def sesDate(time, offset):
  seconds = time + offset + SES_EPOCH_00000
  
  elapsed = { "128-cycle": seconds % SES_LENGTH_OF["128-CYCLE"],
    "4-cycle": 0, "year": 0, "season": 0, "week": 0 }
  elapsed["4-cycle"] = elapsed["128-cycle"] % SES_LENGTH_OF["4-CYCLE"]
  elapsed["year"] = elapsed["4-cycle"] % SES_LENGTH_OF["COMMON_YEAR"]
  elapsed["season"] = elapsed["year"] % SES_LENGTH_OF["COMMON_SEASON"]
  elapsed["week"] = elapsed["season"] % SES_LENGTH_OF["WEEK"]

  current = {
    "128-cycle": int(seconds / SES_LENGTH_OF["128-CYCLE"]),
    "4-cycle": int(elapsed["128-cycle"] / SES_LENGTH_OF["4-CYCLE"]),
    "year": int(elapsed["4-cycle"] / SES_LENGTH_OF["COMMON_YEAR"]),
    "season": int(elapsed["year"] / SES_LENGTH_OF["COMMON_SEASON"]),
    "week": int(elapsed["season"] / SES_LENGTH_OF["WEEK"]),
    "day": int(elapsed["week"] / SES_LENGTH_OF["DAY"]),
    "naturalYear": 0, "naturalDay": 0, "bitfield" : 0 }

  if (current["year"] == 4): current["year"] = 3; current["season"] = 3; current["week"] = 13; current["day"] = 1 # at the end of leap years
  if (current["season"] == 4): current["season"] = 3; current["week"] = 13; current["day"] = 0 # at the end of common years

  current["naturalYear"] = 128 * current["128-cycle"] + 4 * current["4-cycle"] + current["year"]
  current["naturalDay"] = 7 * current["week"] + current["day"]
  current["bitfield"] = current["day"] + (current["week"] << 3) + (current["season"] << 7) + (current["naturalYear"] << 9)

  nat = namedtuple("natural", ["year", "season", "day"])
  cyc = namedtuple("cyclic", ["great", "small", "year", "season", "week", "day"])
  form = namedtuple("formatted", ["natural", "cyclic"])

  natural = nat(current["naturalYear"], current["season"], current["naturalDay"])
  cyclic = cyc(current["128-cycle"], current["4-cycle"], current["year"], current["season"], current["week"], current["day"])

  sesDate = namedtuple("sesDate", ["natural", "cyclic", "bitfield"])
  return sesDate(natural, cyclic, current["bitfield"])