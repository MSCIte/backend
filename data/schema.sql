CREATE TABLE terms
(
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    termCode               TEXT     NOT NULL,
    name                   TEXT     NOT NULL,
    nameShort              TEXT     NOT NULL,
    termBeginDate          DATE     NOT NULL,
    termEndDate            DATE     NOT NULL,
    sixtyPercentDate       DATE     NOT NULL,
    associatedAcademicYear INTEGER  NOT NULL,
    created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

create unique index terms_termCode_uindex
    on terms (termCode);

CREATE TABLE courses
(
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    courseId                    TEXT     NOT NULL,
    courseOfferNumber           INTEGER  NOT NULL,
    termCode                    TEXT,
    termName                    TEXT,
    associatedAcademicCareer    TEXT,
    associatedAcademicGroupCode TEXT,
    associatedAcademicOrgCode   TEXT,
    subjectCode                 TEXT,
    catalogNumber               TEXT,
    title                       TEXT,
    descriptionAbbreviated      TEXT,
    description                 TEXT,
    gradingBasis                TEXT,
    courseComponentCode         TEXT,
    enrollConsentCode           TEXT,
    enrollConsentDescription    TEXT,
    dropConsentCode             TEXT,
    dropConsentDescription      TEXT,
    requirementsDescription     TEXT,
    created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

create unique index courses_courseId_