from datetime import datetime, timezone
import pytz
from pyluach import dates, hebrewcal
from lunarcalendar import Converter, Solar

import sesDate

def emeryradio():
    output = []
    wkdyformat = ("%A")
    dateformat = ("%F")
    timeformat = ("%H:%M")
    secondsformat = ("%H:%M:%S")

    adjustment = -37.0
    #utcdt = datetime(2019,2,1,17,22,35,0,timezone.utc)
    utcdt = datetime.now(timezone.utc)
    cwtdt = datetime.fromtimestamp(3 * (utcdt.timestamp() - 11_093_806_800), tz=timezone.utc)
    cwadt = datetime.fromtimestamp(cwtdt.timestamp() + 3 * adjustment, tz=timezone.utc)
    PT = pytz.timezone("US/Pacific")
    MT = pytz.timezone("US/Mountain")
    CT = pytz.timezone("US/Central")
    ET = pytz.timezone("US/Eastern")
    GMT = pytz.timezone("Etc/GMT")
    CET = pytz.timezone("Europe/Zurich")
    IST = pytz.timezone("Asia/Kolkata")
    WIB = pytz.timezone("Asia/Jakarta")
    WPS = pytz.timezone("Asia/Singapore")
    heb = dates.HebrewDate.from_pydate(utcdt.astimezone(PT))
    yin = Converter.Solar2Lunar(Solar(utcdt.astimezone(PT).year, utcdt.astimezone(PT).month, utcdt.astimezone(PT).day))
    ses = sesDate.sesDate(utcdt.timestamp(), utcdt.astimezone(PT).utcoffset().total_seconds())

    sunmoon = "🌞" if (6 < cwadt.hour < 18) else ("🌚" if (yin.day < 3) else "🌙")
    cwMonthNames = ["Hailag", "Wintar", "Hornung", "Lenzin", "Ōstar", "Winni", "Brāh", "Hewi", "Aran", "Witu", "Wīndume", "Herbist", "Hailag", "Wintar"]
    cwWeekdayNames = ["Mânotag", "Ziestag", "Mittawehha", "Jhonarestag", "Frîatag", "Sunnûnabund", "Sunnûntag", "Mânotag"]
    cwPeriodNames = ["Night", "Morning", "Day", "Evening", "Night"]
    hebMonthNames = ["Adar", "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Marcheshvan", "Kislev", "Tevet", "Shevat", "Adar", "Adar"]
    timeToPeriodChange = (-(cwadt.timestamp() % 21600) + 21600) / 3
    timeToBattle = (-((cwtdt.timestamp() - 21600) % 86400) + 86400) / 3
    timeToArena = (-((cwtdt.timestamp() + 51300) % 259200) + 259200) / 3

    output.append("**Current time**:")
    output.append(f'{cwWeekdayNames[int(cwadt.weekday())]} {cwadt.strftime("%Y-%m-%d %H:%M.%S")} (adjusted; estimated)')
    output.append(f'{cwWeekdayNames[int(cwtdt.weekday())]} {cwtdt.strftime("%H:%M.%S")} (tabular)')
    output.append(f'{sunmoon} {cwPeriodNames[int(cwadt.hour/6)]}: next change in ≈{int(timeToPeriodChange/3600)}h {int((timeToPeriodChange%3600)/60)}′ {int(timeToPeriodChange%60)}″')
    output.append(f'⚔ next battle in {int(timeToBattle/3600)}h {int((timeToBattle%3600)/60)}′ {int(timeToBattle%60)}″')
    output.append(f'📯 arena resets in {int(timeToArena/3600)}h {int((timeToArena%3600)/60)}′ {int(timeToArena%60)}″')
    output.append(f'this month: {cwMonthNames[int(cwadt.month)]}')
    output.append(f'next month: {cwMonthNames[int(cwadt.month)+1]}{"("+str(cwadt.year+1)+")" if cwadt.month == 12 else ""}')
    output.append('')

    pacificD = 'D' if (utcdt.astimezone(PT).utcoffset().total_seconds() == -25200) else 'S'
    mountainD = 'D' if (utcdt.astimezone(MT).utcoffset().total_seconds() == -21600) else 'S'
    centralD = 'D' if (utcdt.astimezone(CT).utcoffset().total_seconds() == -18000) else 'S'
    easternD = 'D' if (utcdt.astimezone(ET).utcoffset().total_seconds() == -14400) else 'S'
    europeanS = 'S' if (utcdt.astimezone(CET).utcoffset().total_seconds() == 7200) else ''

    output.append(f'{utcdt.astimezone(PT).strftime("%A %F %H:%M.%S")} P{pacificD}T (UTC standard)')
    output.append(f"  ╰ GMT−{8 - (pacificD == 'D')}: San Francisco, San Diego")
    output.append(f'{utcdt.astimezone(ET).strftime("%A %H:%M")} E{easternD}T')
    output.append(f"  ╰ GMT−{5 - (easternD == 'D')}: Boston, Augusta, Havana")
    output.append(f'{utcdt.astimezone(GMT).strftime("%A %H:%M")} GMT')
    output.append("  ╰ GMT±0: Accra")
    output.append(f'{utcdt.astimezone(CET).strftime("%A %H:%M")} CE{europeanS}T')
    output.append(f"  ╰ GMT+{1 + (europeanS == 'S')}: Amsterdam, Bern")
    output.append(f'{utcdt.astimezone(WPS).strftime("%A %H:%M")} WPS')
    output.append("  ╰ GMT+8: Singapore, Manila, Hong Kong")
    output.append('')
    
    output.append(f"Equivalent dates (in P{pacificD}T; dates change at midnight)")
    output.append(f'{heb.year} {hebMonthNames[heb.month]}{" I" if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""}{"I" if (hebrewcal.Year(heb.year).leap and heb.month == 13) else ""} {heb.day}')
    output.append(f'{yin.year+2698}/{yin.year+2638}年{yin.month}月{yin.day}日')
    output.append(f'{ses.natural.year:0>5d}.{ses.natural.season:0>1d}.{ses.natural.day:0>2d} (cyclic: {ses.cyclic.great}.{ses.cyclic.small}.{ses.cyclic.year}:{ses.cyclic.season}.{ses.cyclic.week}.{ses.cyclic.day})')

    return '\n'.join(output)

if __name__ == '__main__':
    print(emeryradio())