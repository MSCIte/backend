import re

class Stack:
    def __init__(self):
        self._data = []
    def push(self, x):
        self._data.append(x)
    def pop(self):
        return self._data.pop()
    def peek(self):
        return self._data[-1]
    def __len__(self):
        return len(self._data)
    
class Prereqs:
    def __init__(self):
        self.prereqs = []
        self.min_grade = []  # Parallel list to prereqs
        self.not_open = []
        self.students_only = []
        self.min_level = "1A"

        self.logic = ""
        self.courses = []

    def get_char(i):
        if i + ord('A') > ord('Z'):
            return chr(i - 26 + ord('a'))
        return chr(i + ord('A'))

    def get_index(self, c):
        if ord(c) - ord('A') > 26:
            return ord(c) - ord('a') + 26
        return ord(c) - ord('A')


    def denote_coreqs_helper(self, logic, courses, i):
        while logic[i] != ">":
            i += 1
            if logic[i] == "<":
                i, courses = self.denote_coreqs_helper(logic, courses, i)
            else:
                index = self.get_index(logic[i])
                if 0 <= index < len(courses) and courses[index][0] != "_":
                    courses[index] = "_" + courses[index]
        i += 1
        return i, courses

    def convert(s):
        # initialization of string to " "
        new = " "

        # traverse in the string
        for x in s:
            if x != "True":
                new += re.sub("[A-Z][A-Za-z]+", "", x) + " "

            # return string
        return new

    def remove_dup_bracket(self, logic):
        logic = logic.split()
        n = len(logic)
        s = logic.copy()
        stack = Stack()

        for i in range(n):
            if s[i] != "$":
                s[i] = logic[i]
                if s[i] == "<":
                    if i + 1 < n and s[i+1] in "&|":
                        s[i+1] = "$"
                        stack.push(i)
                    elif i + 1 < n and s[i+1] == ">":
                        if i == 0 or s[i-1] in "&|":
                            s[i] = "True"
                        else:
                            s[i] = "$"
                        s[i+1] = "$"
                    elif i + 2 < n and s[i+2] == ">":
                        s[i] = "$"
                        s[i+2] = "$"
                    else:
                        stack.push(i)

                elif s[i] == ">":
                    if len(stack):
                        start = stack.pop()
                        if (start == 0 and i == n - 1) or \
                        (i > 0 and s[start-1] == "<" and i < n - 1 and s[i+1] == ">"):
                            s[start] = "$"
                            s[i] = "$"
                        if s[i-1] in ("&", "|", "not"):
                            s[i-1] = "$"
                    else:
                        s[i] = "$"
                elif s[i] == "~":
                    s[i] = "not"
                elif (i + 1 < n and s[i+1] == s[i]) or s[i] == "-":
                    s[i] = "$"
        while len(stack):
            i = stack.pop()
            s[i] = "$"

        return "<" + self.convert(list(filter(lambda a: a != "$", s))) + ">"

    def denote_coreqs(self, logic, courses):
        print(logic)
        logic = logic.split()
        coreq_indicators = []
        coreq_all = []

        for i in range(len(logic)):
            if logic[i] == "###":
                coreq_indicators.append(i)
            if logic[i] == "***":
                coreq_all.append(i)

        for i in coreq_all:
            i += 1
            while i < len(logic):
                index = self.get_index(logic[i])
                if 0 <= index < len(courses) and courses[index][0] != "_":
                    courses[index] = "_" + courses[index]
                i += 1

        for i in coreq_indicators:
            i, courses = self.denote_coreqs_helper(logic, courses, i)

        return courses


    def translate_to_python(self, logic, courses=None):
        logic = logic.replace("<", "(").replace(">", ")")
        logic = logic.split()
        in_cond = False
        i = 0
        while i < len(logic):
            if logic[i] in "123456":  # Does not support nested "X of" statements
                logic[i] = "(" + logic[i] + " <= len(tuple(filter(None,["
                in_cond = True
            elif in_cond and logic[i] == "(":
                i += logic[i:].index(")")
            elif in_cond and logic[i] in "&)":
                in_cond = False
                logic[i] = "])))))"
            elif in_cond and logic[i] == "|":
                logic[i] = ","
            i += 1

        if isinstance(courses, list):
            start = 0
            for i in range(len(courses)):
                x = logic[start:].index(self.get_char(i))
                logic[start+x] = courses[i]
                start = x + 1

        logic = " ".join(logic)
        return logic.replace("|", "or").replace("&", "and").replace(" ***", "").replace(" ###", "")


    def load_prereqs(self, prereqs, course_code=""):
            """
            Parses the necessary prerequisite data.

            :param prereqs: string
            :return: boolean
            """
            if isinstance(prereqs, str):
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
                    prereqs = prereqs[:indexes[i][0]] + " " + self.get_char(i) + string + prereqs[indexes[i][1]:]

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

                # return courses

                # try:
                if not len(courses):
                    prereqs = "( True )"
                else:
                    while (True):
                        new_prereqs = self.remove_dup_bracket(prereqs)
                        if new_prereqs == prereqs:
                            break
                        prereqs = new_prereqs

                    print(courses)
                    # Modify courses to indicate coreqs
                    courses = self.denote_coreqs(prereqs, courses)
                    prereqs = self.translate_to_python(prereqs)
                    print(prereqs)
                    print(courses)

                    # if self.logic:
                    #     self.logic = "( " + self.logic + " and " + prereqs + " )"
                    #     self.courses += courses
                    #     self.logic = fix_logic(self.logic)
                    # else:
                    #     self.logic = prereqs
                    #     self.courses = courses

                # except Exception as e:
                #     print(e)
                #     print(prereqs)
                #     print(courses)
                #     self.logic = "( True )"
                #     self.courses = []

                # self.__not_open(prereqs_alt)
                # self.__students_only(prereqs_alt)
                # self.__min_level(prereqs_alt)

                return True
            return False

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

# Parse and print results
for example in examples:
    result = Prereqs.load_prereqs(example)
    # print(result)