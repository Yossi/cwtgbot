import bisect
from datetime import datetime, timezone, timedelta

import pytz
from pyluach import dates, hebrewcal
from lunarcalendar import Converter, Solar
import astral
from timezonefinder import TimezoneFinder

from util import hebrew_numeral
import sesDate

CW_OFFSET = -11_093_806_800
CW3_OFFSET = -11_093_803_200
SPEED = 3

CW_MONTHS = ["Hailag", "Wintar", "Hornung", "Lenzin", "Ōstar", "Winni", "Brāh", "Hewi", "Aran", "Witu", "Wīndume", "Herbist", "Hailag", "Wintar"]
CW_PERIODS = ["Night", "Morning", "Day", "Evening", "Night"]
CW_SEASONS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries"]
CW3_SEASONS = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы", "Овен"]
CW_WEEKDAYS = ["Mânotag", "Ziestag", "Mittawehha", "Jhonarestag", "Frîatag", "Sunnûnabund", "Sunnûntag", "Mânotag"]
CW3_WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье", "Понедельник"]
HEB_MONTHS_ENG = ["Adar", "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Marcheshvan", "Kislev", "Tevet", "Shevat", "Adar", "Adar"]
HEB_MONTHS_VRT = ["אדר", "ניסן", "אייר", "סיוון", "תמוז", "אב", "אלול", "תשרי", "מרחשוון", "כסלו", "טבת", "שבט", "אדר", "אדר"]
SEASON_EMOJI = "♈♉♊♋♌♍♎♏♐♑♒♓"
CLOCK_EMOJI = "🕛🕧🕐🕜🕑🕝🕒🕞🕓🕟🕔🕠🕕🕡🕖🕢🕗🕣🕘🕤🕙🕥🕚🕦🕛"

DEPRESSION = 8 + 3/5
SUN_YAT_SEN_ERA = 2698
WRITERS_ERA = 2637

def tealeyes(user_data):
    output = []
    hmsformat = ("%H:%M:%S")
    weekdayhmformat = ("%A %H:%M")
    ymdhmsformat = ("%F %H:%M:%S")
    fullformat = ("%A %F %H:%M:%S")
    countdownformat= ("{H}﻿h {M}′ {S}″")
    longcountdownformat= ("{D}﻿d {H}﻿h {M}′")

    timeshown = ( #these should be chat-specific or possibly guild-specific settings
        ( (37.791279, -122.399218), "San Francisco, San Diego" ), # Union Square
        ( (42.356528, -71.055808), "Boston, Augusta, Havana" ), # Haymarket Square
        ( (5.545631, -0.208266), "Accra" ), # Rawlings Park
        ( (52.374366, 4.898069), "Amsterdam, Bern" ), # De Oude Kerk
        ( (55.754118, 37.620386), "Moscow" ), # Red Square
        ( (1.292379, 103.852276), "Singapore, Manila, Hong Kong" ), # St. Andrew's Cathedral
        ( (-37.787329, 175.282472), "Kirikiriroa" ) # Garden Place
    )

    adjustment = -37.0 #there should be admin settings for this, as we may find these need adjusting
    adjustment3 = -37.0
    utcdt = datetime.now(timezone.utc)
    #utcdt = datetime(1912,1,1,10,0,0,0,timezone.utc) #for testing
    cwtdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() + CW_OFFSET), tz=timezone.utc)
    cw3tdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() + CW3_OFFSET), tz=timezone.utc)
    cwadt = datetime.fromtimestamp(cwtdt.timestamp() + SPEED * adjustment, tz=timezone.utc)
    cw3adt = datetime.fromtimestamp(cw3tdt.timestamp() + SPEED * adjustment3, tz=timezone.utc)

    def strfdelta(tdelta, fmt):
        d = {"D": tdelta.days}
        d["H"], rem = divmod(tdelta.seconds, 3600)
        d["M"], d["S"] = divmod(rem, 60)
        return fmt.format(**d)

    def get_moon():
        a = astral.Astral()
        moon_phase = a.moon_phase(utcdt, rtype=float)
        lunation = moon_phase / 27.99

        PRECISION = 0.05
        NEW =   0 / 4.0
        FIRST = 1 / 4.0
        FULL = 2 / 4.0
        LAST = 3 / 4.0
        NEXTNEW = 4 / 4.0

        phase_strings = (
            (NEW + PRECISION, "🌑"),
            (FIRST - PRECISION, "🌒"),
            (FIRST + PRECISION, "🌓"),
            (FULL - PRECISION, "🌔"),
            (FULL + PRECISION, "🌕"),
            (LAST - PRECISION, "🌖"),
            (LAST + PRECISION, "🌗"),
            (NEXTNEW - PRECISION, "🌘"),
            (NEXTNEW + PRECISION, "🌑")
        )

        i = bisect.bisect([a[0] for a in phase_strings], lunation)
        return phase_strings[i][1]

    sunmoon = '🌞' if (6 < cwadt.hour < 18) else '🌙'
    countdownArena = (datetime(1, 1, 1, 8, 15, 0, 0, timezone.utc) - utcdt) % timedelta(hours=24)
    countdownBattle = ((datetime(1, 1, 1, 6, 0, 0, 0, timezone.utc) - cwtdt) / SPEED) % timedelta(hours=8)
    countdownPeriod = ((datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc) - cwadt) / SPEED) % timedelta(hours=2)

    nextCwMonth = (cwadt.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1)
    countdownMonth = (nextCwMonth - cwadt) / SPEED

    season_int = ((12 * utcdt.year + utcdt.month) // 3 + 11) % 12
    nextCwSeason = (utcdt.replace(year=utcdt.year + (utcdt.month == 12), month=((((utcdt.month) // 3) + 1) * 3) % 12, day=1, hour=0, minute=0, second=0, microsecond=0))
    countdownSeason = (nextCwSeason - utcdt)

    output.append(f"<b>Chat Wars (EU)</b>:")
    output.append(f'{CW_WEEKDAYS[cwadt.weekday()]} {cwadt.strftime(ymdhmsformat)} (estimated)')
    output.append(f'{CW_WEEKDAYS[cwtdt.weekday()]} {cwtdt.strftime(hmsformat)} (tabular)')
    output.append(f'{sunmoon} {CW_PERIODS[cwadt.hour//6]}: {CW_PERIODS[cwadt.hour//6 + 1]} in ≈{strfdelta(countdownPeriod, countdownformat)}')
    output.append(f'⚔ next battle in {strfdelta(countdownBattle, countdownformat)}')
    output.append(f'📯 arena resets in {strfdelta(countdownArena, countdownformat)}')

    output.append(f"🗓 month of {CW_MONTHS[cwadt.month]}: {CW_MONTHS[cwadt.month+1]} in ≈{strfdelta(countdownMonth, longcountdownformat)}")
    output.append(f"{SEASON_EMOJI[season_int]} {CW_SEASONS[season_int]} season: {CW_SEASONS[season_int + 1]} in ≈{strfdelta(countdownSeason, longcountdownformat)}")
    output.append(f'')

    output.append(f"<b>Chat Wars 3 (RU)</b>: {CW3_WEEKDAYS[cw3adt.weekday()]} {cw3adt.strftime(hmsformat)} /time3")
    output.append(f'')

    usertz_str = user_data.get('timezone')
    if usertz_str:
        worktz = pytz.timezone(usertz_str)
        workdt = utcdt.astimezone(worktz)
        heb = dates.HebrewDate.from_pydate(workdt)
        heb_tom = None
        yin = Converter.Solar2Lunar(Solar(workdt.year, workdt.month, workdt.day))
        ses = sesDate.sesDate(utcdt.timestamp(), workdt.utcoffset().total_seconds())

        latlon = user_data.get('location')
        if latlon:
            loc = astral.Location(('', '', latlon[0], latlon[1], usertz_str, 0))
            sunset = loc.time_at_elevation(-.8, direction=astral.SUN_SETTING)
            nightfall = loc.time_at_elevation(-8.5, direction=astral.SUN_SETTING)

            if workdt < sunset:
                pass
            elif sunset < workdt < nightfall:
                heb_tom = heb + 1
            else:
                heb = heb + 1

        output.append(f"<b>Your time</b>: {workdt.tzname()} (GMT{workdt.strftime('%z')})")
        output.append(f'{get_moon()} {workdt.strftime(fullformat)}')
        output.append(
            f'{heb.year} {HEB_MONTHS_ENG[heb.month]}{(" II" if heb.month == 13 else " I")if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""} ' +
            f'{heb.day} · {hebrew_numeral(heb.day)}' +
            f' {HEB_MONTHS_VRT[heb.month]}{(" ב" if heb.month == 13 else " א") if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""} {hebrew_numeral(heb.year)}')
        if heb_tom:
            heb = heb_tom
            output.append(
                f'{heb.year} {HEB_MONTHS_ENG[heb.month]}{(" II" if heb.month == 13 else " I")if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""} ' +
                f'{heb.day} · {hebrew_numeral(heb.day)}' +
                f' {HEB_MONTHS_VRT[heb.month]}{(" ב" if heb.month == 13 else " א") if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""} {hebrew_numeral(heb.year)}')
        output.append(f'{yin.year + SUN_YAT_SEN_ERA}/{yin.year + WRITERS_ERA}年{yin.month}月{yin.day}日')
        output.append(f'{ses.natural.year:0>5d}.{ses.natural.season:0>1d}.{ses.natural.day:0>2d} · cyclic {ses.cyclic.great}.{ses.cyclic.small}.{ses.cyclic.year}:{ses.cyclic.season}.{ses.cyclic.week}.{ses.cyclic.day}')
        output.append(f'')

    for worktime in timeshown:
        tz_str = TimezoneFinder().timezone_at(lat=worktime[0][0], lng=worktime[0][1])
        tz = pytz.timezone(tz_str)
        workdt = utcdt.astimezone(tz)
        minutes = 60 * workdt.hour + workdt.minute
        clockface = CLOCK_EMOJI[(minutes + 10) // 30 % 24]
        if (clockface == '🕛'):
            ampmindicator = '☀️' if (11 * 60 < minutes < 13 * 60) else '⚫'
        else:
            ampmindicator = '🅰' if minutes < 12 * 60 else '🅿️'
        loc = astral.Location(('', '', worktime[0][0], worktime[0][1], tz_str, 0))
        loc.solar_depression = DEPRESSION
        if loc.sunrise(workdt) > workdt or loc.dusk(workdt) < workdt:
            sunprogress = '🌃'
        elif loc.sunset(workdt) < workdt < loc.dusk(workdt):
            sunprogress = '🌆'
        else:
            sunprogress = '🏙️'
        output.append(f'{clockface}{ampmindicator}{sunprogress} {utcdt.astimezone(tz).strftime(weekdayhmformat)} {utcdt.astimezone(tz).tzname()}')
        output.append(f"  ╰ GMT{utcdt.astimezone(tz).strftime('%z')} {worktime[1]}")

    return '\n'.join(output)

if __name__ == '__main__':
    user_data = {}
    print(tealeyes(user_data))
