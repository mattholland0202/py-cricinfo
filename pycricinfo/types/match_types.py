from enum import Enum


class MatchTypeNames(str, Enum):
    TESTS = "Tests"
    ODIs = "One-Day Internationals"
    T20Is = "Twenty20 Internationals"
    FIRST_CLASS = "First-class"
    LIST_A = "List A"
    T20 = "Twenty20"
    WOMENS_ODIs = "Women's One-Day Internationals"
    WOMENS_T20Is = "Women's Twenty20 Internationals"
    YOUTH_TESTS = "Youth Tests"
    YOUTH_ODIs = "Youth One-Day Internationals"
    WOMENS_T20 = "Women's Twenty20"
    TOUR = "Tour"
    MINOR_TOUR = "Minor tour"
    OTHER_MATCHES = "Other matches"
    OTHER_ODI_MATCHES = "Other one-day/limited-overs matches"
    OTHER_T20_MATCHES = "Other Twenty20 matches"


class MatchNoteType(Enum):
    SERIES_NOTE = "seriesnote"
    POINTS = "points"
    MATCH_NUMBER = "matchnumber"
    SEASON = "season"
    MATCH_DAYS = "matchdays"
    TOSS = "toss"
    LIVE_COMMENTATOR = "livecommentator"
    LIVE_SCORER = "livescorer"
    MATCH_NOTE = "matchnote"
    CLOSE_OF_PLAY = "closeofplay"
    HOURS_OF_PLAY = "hoursofplay"
    PLAYER_REPLACEMENT = "playerreplacement"
    HAWKEYE = "hawkeye"


class DeliveryPlayTypes(int, Enum):
    RUN = 1
    NO_RUN = 2
    FOUR = 3
    SIX = 4
    BYE = 7
    LEG_BYE = 8
    OUT = 9
