from enum import Enum

from aenum import MultiValueEnum


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


class MatchNoteType(MultiValueEnum):
    SERIES_NOTE = "seriesnote", "Series note"
    POINTS = "points", "Points"
    MATCH_NUMBER = "matchnumber", "Match number"
    SEASON = "season", "Season"
    MATCH_DAYS = "matchdays", "Match days"
    TOSS = "toss", "Toss"
    LIVE_COMMENTATOR = "livecommentator", "Live commentator"
    LIVE_SCORER = "livescorer", "Live scorer"
    MATCH_NOTE = "matchnote", "Match note"
    CLOSE_OF_PLAY = "closeofplay", "Close of play"
    HOURS_OF_PLAY = "hoursofplay", "Hours of play"
    PLAYER_REPLACEMENT = "playerreplacement", "Player replacement"
    HAWKEYE = "hawkeye", "Hawkeye"


class DeliveryPlayTypes(int, Enum):
    RUN = 1
    NO_RUN = 2
    FOUR = 3
    SIX = 4
    BYE = 7
    LEG_BYE = 8
    OUT = 9
