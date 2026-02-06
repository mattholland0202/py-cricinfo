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
