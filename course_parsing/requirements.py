import re
from .ascii_translator import get_char, get_index
from .parse_tree import remove_dup_bracket, translate_to_python, denote_coreqs, fix_logic
import json


def letters_to_courses(options, courses):
    """
    Depreciated
    """
    output = ""
    for option in options:
        for char in option:
            output += courses[get_index(char)] + " & "
        output = output[:-3] + " | "
    output = output[:-3]
    return output

def load_prereqs(prereqs, course_code=""):
    """
    Parses the necessary prerequisite data.

    :param prereqs: string
    :return: boolean
    """
    prereqs = prereqs.replace("Prereq: ", "")
    prereqs = prereqs.replace("Coreq: ", "***")
    prereqs_alt = re.split("[;.]", prereqs)

    # Remove single upper characters
    prereqs = re.sub("^[A-Z] ", "", prereqs)
    prereqs = re.sub("([^A-Za-z0-9])[A-Z] ", "\1 ", prereqs)

    # Deal with corequisite options in the prereq by deonoting all courses after ### as a coreq
    prereqs = re.sub("[Cc]o(?:-)?req(?:uisite)?(?::)?", "###", prereqs)

    # Convert to numbers for parsing readability
    prereqs = prereqs.replace("One ", "1 ").replace("one ", "1 ").replace("0.50", "1").replace("0.5", "1")
    prereqs = prereqs.replace("Two ", "2 ").replace("two ", "2 ").replace("1.00", "2").replace("1.0", "2")
    prereqs = prereqs.replace("Three ", "3 ").replace("three ", "3 ").replace("1.50", "3").replace("1.5", "3")
    prereqs = prereqs.replace("Four ", "4 ").replace("four ", "4 ").replace("2.00", "4").replace("2.0", "4")
    prereqs = prereqs.replace("Five ", "5 ").replace("five ", "5 ").replace("2.50", "5").replace("2.5", "5")
    prereqs = prereqs.replace("Six ", "6 ").replace("six ", "6 ").replace("3.00", "6").replace("3.0", "6")

    # Remove all numbers longer than 3 digits
    prereqs = re.sub("[0-9][0-9][0-9][0-9]+", "", prereqs)

    # <year> year ABC becomes ABC 1000
    prereqs = re.sub("first year ([A-Z][A-Z]+)", r"\1 1000", prereqs)
    prereqs = re.sub("second year ([A-Z][A-Z]+)", r"\1 2000", prereqs)
    prereqs = re.sub("third year ([A-Z][A-Z]+)", r"\1 3000", prereqs)
    prereqs = re.sub("fourth year ([A-Z][A-Z]+)", r"\1 4000", prereqs)

    # Remove all words that are separated with / that aren't part of courses
    prereqs = re.sub(" [a-zA-Z\\-]*[a-z][a-zA-Z\\-]*/[a-zA-Z\\-]+", "", prereqs)
    prereqs = re.sub(" [a-zA-Z\\-]+/[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", prereqs)

    # Replace brackets with < >
    prereqs = prereqs.replace("(", " < ").replace(")", " > ")

    # Convert and's into &
    prereqs = re.sub("[^A-Za-z]and", " & ", prereqs)
    # Convert or's into |
    prereqs = re.sub("([0-9>])\\s*or\\s*([A-Z0-9<])", r"\1 | \2", prereqs)
    prereqs = re.sub("([^A-Za-z])\\s*or", r"\1 | ", prereqs)

    # Replace all course slashes with < course /| course ... >
    pattern = "([A-Z]+[ ]?(?:[0-9][0-9][0-9][A-Z0]?)?|(?:[A-Z]+)?[ ]?[0-9][0-9][0-9][A-Z0]?)/"
    replace = r" < \1 /| \2 /| \3 /| \4 /| \5 /| \6 /| \7 /| \8 /| \9 >"
    for i in range(9, 1, -1):
        m_pattern = (i * pattern)[:-1]
        prereqs = re.sub(m_pattern, replace, prereqs)
        replace = replace[:-8] + replace[-2:]

    # X00-level becomes X000
    prereqs = prereqs.replace("-level", "0")

    # Remove -
    prereqs = prereqs.replace("-", " ")

    # Any XXX course becomes XXX 0000
    prereqs = re.sub("[Aa]ny ([A-Z]+)(?: course)?", r"\1 0000", prereqs)
    prereqs = re.sub("([1-9]) unit(?:s)? (?:in|of) ([A-Z]+)", r"\1 \2 0000", prereqs)

    # Add not condition for antireqs in prereq
    prereqs = re.sub("Not open to students who(?: have)? received credit for ", "~", prereqs)

    # Remove PD
    prereqs = re.sub("PD [1-9][0-9]", "", prereqs)

    # Remove entire block that includes "Open only ...;" and "Level at ...;"
    prereqs = re.sub("((?:Open only to students in .+[.;])|"
                        "(?:[Ll]ev(?:el)? at [^.;>&<,]+))", " ", prereqs)

    # Remove XX% and 2A like text
    prereqs = re.sub("((?:[1-9][0-9]%)|"
                        "(?:[^0-9][1-9][A-Z]))", " ",
                        prereqs)

    # Remove all words
    prereqs = re.sub("[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", prereqs)

    # Replace all "; |" with "| ;"
    prereqs = re.sub(";\\s*\\|", " | ;", prereqs)

    # Replace . with &
    prereqs = prereqs.replace(".", " & ")

    # Clean spaces
    prereqs = re.sub("\\s+", " ", prereqs)

    # Strip < from end, > from start
    while True:
        old_prereqs = prereqs
        while prereqs.endswith(" <"):
            prereqs = prereqs[:-2]
        while prereqs.startswith("> "):
            prereqs = prereqs[2:]

        # Replace [block] | ; [block] with [block] | [block]
        prereqs = re.sub("([^;]+)\\|\\s*;([^;]+)", r"< \1 > | < \2 >", prereqs).strip(" &|,/;")

        # Replace [block] ; [block] with [block] & [block]
        prereqs = re.sub("([^;]+);([^;]+)", r"< \1 > & < \2 >", prereqs).strip(" &|,/;")

        # If changes cannot be made, exit loop
        if prereqs == old_prereqs:
            break

    # Clean spaces
    prereqs = re.sub("\\s+", " ", prereqs)

    # Reverse 2000 XXX to XXX 2000
    prereqs = re.sub("([0-9]{4})\\s([A-Z]+)", r"\2 \1", prereqs)

    # Replace "CS 135 | 145 & MATH 135" with "CS 135 /| 145 & MATH 135"
    while True:
        new_prereqs = re.sub("([A-Z]+\\s*[0-9]{3}[A-Z0]?\\s*)\\|(\\s*[0-9]{3}[A-Z0]?)", r"\1 /| \2", prereqs)
        if new_prereqs == prereqs:
            break
        else:
            prereqs = new_prereqs

    # Find all courses and their indexes
    grep = "[A-Z]+ /\\||(?:[A-Z]+[ ]?)?[0-9][0-9][0-9][A-Z0]?|[A-Z][A-Z]+"
    courses = re.findall(grep, prereqs)
    indexes = [(m.start(0), m.end(0)) for m in
                re.finditer(grep, prereqs)]

    # Generate new course codes by turning ["CS 135", "145"] into ["CS 135", "CS 145"]
    new_courses = []
    code = ""
    for i, course in enumerate(courses):
        new_number = re.findall("[0-9][0-9][0-9][A-Z0]?", course)
        course = re.sub("[0-9][0-9][0-9][A-Z0]?", "", course)
        new_code = re.findall("[A-Z]+", course)
        if len(new_code):
            code = new_code[0]
        if len(new_number):
            number = new_number[0]
        else:
            number = ""
        course = code + " " + number
        new_courses.append(course)

    # Loop backwards to replace each course with a respective letter
    courses = new_courses
    for i in range(len(courses)-1, -1, -1):

        # If course had no number, use the number from lookahead
        if courses[i].endswith(" "):
            if i < len(courses)-1:
                courses[i] += re.findall("[0-9][0-9][0-9][A-Z0]?", courses[i+1])[0]
            else:
                courses[i] += "0000"

        # If the course ahead ends with a letter, the current does not and they have different codes, add the
        # letter from lookahead to the end if the current course.
        elif i < len(courses)-1 and courses[i][-1] in "1234567890" and \
                courses[i+1][-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and \
                courses[i][-3:] != courses[i+1][-4:-1] and prereqs[indexes[i][1]+1:indexes[i][1]+3] == "/|":
            courses[i] += courses[i+1][-1]

        # Generate a condition string for the current course to the next
        string = " "
        if prereqs[indexes[i][1]-1] == "|":
            if prereqs[indexes[i][1]-2] == "/":
                string = " /| "
            else:
                string = " | "

        # Convert course to letter
        prereqs = prereqs[:indexes[i][0]] + " " + get_char(i) + string + prereqs[indexes[i][1]:]

    # Any cases of courses without codes get assigned the same as the original course
    for i in range(len(courses)):
        if courses[i][0] == " ":
            courses[i] = course_code + courses[i]

    # Convert , | to /|
    prereqs = prereqs.strip(" &|,").replace(", |", "/|")

    # Clean spaces
    prereqs = re.sub("\\s+", " ", prereqs)

    # Replace "2 A , < B & C > /| D" with "< 2 A | < B & C > | D >"
    comma_indices = [(m.start(0), m.end(0)) for m in
                        re.finditer("[1-9] ([A-Za-z]|< [^>]+ >)(?:\\s*(,|/\\||\\|)\\s*([A-Za-z]|< [^>]+ >))+", prereqs)]
    for i in range(len(comma_indices)-1, -1, -1):
        start, end = comma_indices[i]
        prereqs = prereqs[:start] + " < " + prereqs[start:end].replace(",", " | ") + \
                    " > " + prereqs[end:]

    # Enclose all remaining /| groupings with < >
    prereqs = re.sub("((?:[A-Za-z]|< .+ >)(?:\\s*/\\|\\s*(?:[A-Za-z]|< .+ >))+)", r"< \1 >", prereqs)
    prereqs = prereqs.replace("/|", "|")

    # Enclose all remaining , groupings with < >
    prereqs = re.sub("((?:[A-Za-z]|< [^>]+ >)(?:\\s*,\\s*(?:[A-Za-z]|< [^>]+ >))+)", r"< \1 >", prereqs)
    prereqs = prereqs.replace(",", " & ")

    # Clean spaces
    prereqs = re.sub("\\s+", " ", prereqs)

    # Remove need for "one of" since it already covered by "A or B or C" logically
    prereqs = prereqs.replace("1 ", "")

    # Encapsulate prereqs with < >
    prereqs  = "< " + prereqs.strip() + " >"

    # try:
    if not len(courses):
        prereqs = "( True )"
    else:
        while (True):
            new_prereqs = remove_dup_bracket(prereqs)
            if new_prereqs == prereqs:
                break
            prereqs = new_prereqs

        # Modify courses to indicate coreqs
        courses = denote_coreqs(prereqs, courses)
        prereqs = translate_to_python(prereqs)


        # print(prereqs)
        # print(courses)

        #     if self.logic:
        #         self.logic = "( " + self.logic + " and " + prereqs + " )"
        #         self.courses += courses
        #         self.logic = fix_logic(self.logic)
        #     else:
        #         self.logic = prereqs
        #         self.courses = courses

        #     print(prereqs)
        #     print(courses)

        # except Exception as e:
        #     print(e)
        #     print(prereqs)
        #     print(courses)
        #     self.logic = "( True )"
        #     self.courses = []

        # self.__not_open(prereqs_alt)
        # self.__students_only(prereqs_alt)
        # self.__min_level(prereqs_alt)

    prereq_json = json.dumps(courses)

    return {"logic": prereqs, "courses": prereq_json}

def __prereqs(self, prereqs):
    """
    Depreciated

    Modifies the field(s):
    prereqs
    min_grade

    :param prereqs: list(string)
    :return: None
    """
    for category in prereqs:
        if "ne of" not in category:
            category = category.split(", ")
        else:
            category = [category]

        for c in category:
            pre = []
            grades = []
            '''Cases:
            STAT 220 with a grade of at least 70%
            at least 60% in MTHEL 131
            At least 60% in ACTSC 231
            
            '''

            change = True
            match = re.findall("(?:..% (?:or higher )?in (?:one of )?)?(?:[A-Z]+ )?[1-9][0-9][0-9]" +
                                "(?: with (?:(?:a )?(?:minimum )?grade of )?(?:at least )?..%)?", c)
            for m in match:
                if "or" in m:
                    change = False
                m = m.replace(" or higher", "").replace("one of ", "")
                if m[-1] == "%":
                    grade = int(m[-3:-1])
                    course = re.search("(?:[A-Z]+ )?[1-9][0-9][0-9]", m).group()
                elif "%" not in m:
                    course = m
                    if change:
                        grade = 50
                else:
                    course = m[7:]
                    grade = int(m[:2])
                pre.append(course)
                grades.append(grade)

            if len(pre):
                self.prereqs.append(pre)
                self.min_grade.append(grades)

def __not_open(self, prereqs):
    """
    Modifies the field(s):
    not_open

    :param prereqs: list(string)
    :return: None
    """
    for category in prereqs:
        m = re.search("Not open to (.*) students", category)
        if m:
            self.not_open = re.split(',| & ', m.group(1))
        m2 = re.search("Not open to students who have received credit for ([A-Z]+ [1-9][0-9][0-9])+", category)
        if m2:
            self.not_open = re.split(',| & ', m2.group(1))

def __students_only(self, prereqs):
    """
    Modifies the field(s):
    students_only

    :param prereqs: list(string)
    :return: None
    """
    for category in prereqs:
        m = re.search("(.*) students only", category)
        if m:
            m = m.group(1).strip()
            self.students_only = re.split(" and | or ", m)
            break
        m2 = re.search("Open only to students in the following [Ff]aculties: (.*)", category)
        if m2:
            m2 = m2.group(1).strip()
            self.students_only = re.split(", | or ", m2)
            break

def __min_level(self, prereqs):
    """
    Modifies the field(s):
    min_level

    :param prereqs: list(string)
    :return: None
    """
    for category in prereqs:
        m = re.search("Level at least ..", category)
        if m:
            self.min_level = m.group()[-2:]
            break

def prettyprint(self, printer=True):
    output =  "Prereqs:\t\t" + str(self.prereqs) + "\n"
    output += "Min Grades:\t\t" + str(self.min_grade) + "\n"
    output += "Not open:\t\t" + str(self.not_open) + "\n"
    output += "Students only:\t" + str(self.students_only) + "\n"
    output += "Min level:\t\t" + str(self.min_level) + "\n"
    if printer:
        print(output)
    else:
        return output

def __print_prereqs(self):
    output = ""
    for i, courses in enumerate(self.prereqs):
        for j, course in enumerate(courses):
            course = course.split()
            if len(course) == 2:
                id = course[0]
                num = course[1]
            else:
                num = course[0]
            try:
                output += id + " " + num
            except Exception as e:
                print(courses)
                print(course)
                raise e

            if j != len(courses) - 1:
                output += " or "
        if i != len(self.prereqs) - 1:
            output += ", "
    return output

def __print_grades(self):
    output = ""
    for i, grades in enumerate(self.min_grade):
        for j, grade in enumerate(grades):
            output += str(grade)
            if i != len(self.min_grade) - 1 or j != len(grades) - 1:
                output += ", "
    return output

def __print_not_open(self):
    output = ""
    for i, not_open in enumerate(self.not_open):
        output += not_open.replace("'", "")
        if i != len(self.not_open) - 1:
            output += ", "
    return output

def __print_only(self):
    output = ""
    for i, only in enumerate(self.students_only):
        output += only.replace("'", "")
        if i != len(self.students_only) - 1:
            output += ", "
    return output

def __print_level(self):
    return self.min_level

def str(self, flag="prereqs"):
    """
    Returns a string form of data.

    The flag field can be filled in with any of the following options:
    1. prereqs  - ex. "CS 241 or CS 245, SE 212"
    2. grades   - ex. "50, 60, 70"
    3. not_open - ex. "Software Engineering, Computer Science"
    4. only     - ex. "Computer Science"
    5. level    - ex. "3A"
    6. pretty   - prettyprint()
    7. logic    - ex. "( ( A and B ) or C )"
    8. courses  - ex. "CS 123,CS 234,CS 345"

    :param flag: string (default="prereqs")
    :return: string
    """
    output = ""
    if flag == "prereqs":
        output = self.__print_prereqs()
    if flag == "grades":
        output = self.__print_grades()
    if flag == "not_open":
        output = self.__print_not_open()
    if flag == "only":
        output = self.__print_only()
    if flag == "level":
        output = self.__print_level()
    if flag == "pretty":
        output = self.prettyprint(printer=False)
    if flag == "logic":
        output = self.logic
    if flag == "courses":
        output = ",".join(self.courses)
    return output


def load_antireqs(antireqs):
    antireqs = antireqs.replace("Antireq: ", "")
    antireqs = re.sub("[0-9]{3}[0-9]", "", antireqs)
    antireqs = re.sub("[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", antireqs)

    for _ in range(1):
        antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3})([A-Z])\\s*/\\s*([A-Z])",
                            r"\1 \2\3, \1 \2\4", antireqs)
        antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)(?:\\s*/\\s*|\\s*,\\s*)([0-9]{3}[A-Z]?[A-Z]?)",
                            r"\1 \2, \1 \3", antireqs)
        antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)(?:\\s*/\\s*|\\s*,\\s*)"
                            "([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)",
                            r"\1 \2, \3 \4", antireqs)
        antireqs = re.sub("([A-Z][A-Z]+)\\s*(?:\\s*/\\s*|\\s*,\\s*)([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)",
                            r"\1 \3, \2 \3", antireqs)

    antireqs = re.findall("(?:[A-Z]+ )?[1-9][0-9][0-9][A-Z]?[A-Z]?", antireqs)
    extra_info = antireqs if not len(antireqs) else ""
    fix_antireqs(antireqs)

    antireqs_json = json.dumps(antireqs)

    return {"courses": antireqs_json, "extra_info": extra_info}

def fix_antireqs(antireqs):
    code = ""

    for i in range(len(antireqs)):
        antireq = antireqs[i]
        code_num = antireq.split()

        if len(code_num) == 2:
            code = code_num[0]
        else:
            antireq = code + " " + antireq

        antireqs[i] = antireq

def str(self, flag="antireqs"):
    output = ""

    if flag == "antireqs":
        for i, antireq in enumerate(self.antireqs):
            output += antireq
            if i != len(self.antireqs) - 1:
                output += ", "

    elif flag == "extra":
        output = self.extra_info

    return output
    

# Examples
examples = [
    "Actuarial Science Masters Students",
    "Antireq: AE 121, BME 121, CS 115, 137, 138, 145, CIVE 121, ECE 150, ME 101, MSCI 121, PHYS 236, SYDE 121",
    "Antireq: AFM 231/LS 283, ECE 290; (For Mathematics students only) BUS 231W, CIVE 491, ENVS 201, GENE 411, ME 401, MTHEL 100",
    "Coreq: CHEM 120. Antireq: CHEM 121L",
    "Pre/Co-req: ECE 650 or 750 Tpc 26, or instructor consent. Antireq: ECE 355, ECE 451, CS 445, CS 645, SE 463, ECE 452, CS 446, CS 646, SE 464",
    "Prereq/coreq: ECE 650 or 750 Tpc 26 or instructor consent. Antireq: CS 447, 647, ECE 453, SE 465",
    "Prereq: ((MATH 106 with a grade of at least 70% or MATH 136 or 146) and (MATH 135 with a grade of at least 60% or MATH 145)) or level at least 2A Software Engineering; Honours Mathematics students only. Antireq: CO 220, MATH 229, 249",
    "Prereq: (CHEM 233 or 237), 360; Antireq: CHEM 482"
]
# p = Prereqs()
# Parse and print results
for example in examples:
    result = load_antireqs(example)
    print(result)
    