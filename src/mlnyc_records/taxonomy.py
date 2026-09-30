import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class ComponentFormat(StrEnum):
    lprint = "Large print"
    dvd = "DVD"
    book = "book"
    playaway = "Playaway audiobook"


class GradeReadingLevel(StrEnum):
    A = "Pre-K"
    B = "K-2"
    C = "3-5"
    D = "6-8"
    E = "9-12"


class Language(StrEnum):
    ENG = "English"
    SPA = "Spanish"
    CHI = "Chinese"
    FRE = "French"
    OTHER = "Other"


class SetTypeFormat(StrEnum):
    AUDIO = "Audio & Digital Devices"
    CLUB = "Book Club"
    GAME = "Game"
    LPRINT = "Large Print"
    PHONIC = "Phonics & Decodeables"
    STORY = "Storytelling"
    TOPIC = "Topic"


class SubjectStudyProgram(StrEnum):
    ART = "Arts & Music"
    ENG = "Engineering"
    ELA = "Language Arts ENG"
    CHLA = "Language Arts CHI"
    FRLA = "Language Arts FRE"
    SPLA = "Language Arts SPA"
    MAT = "Math"
    PDE = "Professional Development"
    SCI = "Science"
    SEL = "Social Emotional Learning"
    SOC = "Social Studies"
    TEC = "Technology"
    WorldLang = "Language Arts"
    GAME = "Game"


class TaxonomyGenre(StrEnum):
    adventure = "Adventure"
    award_winners = "Award Winners"
    biography = "Biography"
    comics_graphic_novels = "Comics & Graphic Novels"
    coming_of_age = "Coming of Age"
    fantasy = "Fantasy"
    fiction = "Fiction"
    folklore = "Folklore"
    manga = "Manga"
    memoir = "Memoir"
    mystery = "Mystery"
    nonfiction = "Nonfiction"
    poetry = "Poetry"
    romance = "Romance"


class TaxonomyTopic(StrEnum):
    african_americans = "African Americans"
    ancient_civilization = "Ancient Civilization"
    animals = "Animals"
    asian_americans = "Asian Americans"
    astronomy = "Astronomy"
    autism = "Autism"
    behavior = "Behavior"
    bullying = "Bullying"
    chinese_americans = "Chinese Americans"
    civil_rights = "Civil Rights"
    community = "Community"
    concepts = "Concepts"
    cooking = "Cooking"
    courage = "Courage"
    cultural_heritage = "Cultural Heritage"
    dance = "Dance"
    family = "Family"
    health_wellness = "Health & Wellness"
    immigration = "Immigration"
    music = "Music"
    new_york_city = "New York City"
    plants = "Plants"
    sports = "Sports"
    weather = "Weather"
