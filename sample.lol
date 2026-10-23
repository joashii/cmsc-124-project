BTW ====================================================================
BTW  LOLCode sample: every keyword, every comment form, and nesting.
BTW  Functions may appear before HAI or after KTHXBYE.
BTW ====================================================================

OBTW
  A multi-line comment. OBTW and TLDR each sit alone on their own lines.
  Keywords inside a comment are ignored: I HAS A x ITZ 1, VISIBLE, KTHXBYE
TLDR

BTW ---------- functions (defined before HAI) ----------
HOW IZ I square YR n
  FOUND YR PRODUKT OF n AN n
IF U SAY SO

HOW IZ I max_of YR a AN YR b
  FOUND YR BIGGR OF a AN b
IF U SAY SO

HOW IZ I clamp YR v AN YR low AN YR high
  FOUND YR SMALLR OF high AN BIGGR OF low AN v
IF U SAY SO

HOW IZ I factorial YR n
  BOTH SAEM n AN 0
  O RLY?
    YA RLY
      FOUND YR 1
    NO WAI
      FOUND YR PRODUKT OF n AN I IZ factorial YR DIFF OF n AN 1 MKAY
  OIC
IF U SAY SO

HOW IZ I greet
  VISIBLE "Hello from a function with no parameters"
  GTFO
IF U SAY SO

HAI
BTW ---------- variable declarations (only allowed inside WAZZUP) ----------
WAZZUP
  I HAS A empty                          BTW uninitialised, so it is NOOB
  I HAS A total ITZ 10                   BTW NUMBR
  I HAS A ratio ITZ 3.14                 BTW NUMBAR
  I HAS A neg ITZ -7                     BTW negative NUMBR
  I HAS A name ITZ "Lolcat Lab"          BTW YARN
  I HAS A flag ITZ WIN                   BTW TROOF
  I HAS A other ITZ FAIL
  I HAS A copy ITZ total                 BTW initialised from another variable
  I HAS A calc ITZ SUM OF 5 AN 4         BTW initialised from an expression
  I HAS A joined ITZ SMOOSH "a" AN "b" AN "c"
  I HAS A tricky ITZ "I HAS A BTW OBTW TLDR, all inside a YARN"
  OBTW
    A multi-line comment is allowed inside the WAZZUP block too.
  TLDR
  I HAS A text
  I HAS A i, I HAS A j                   BTW a soft break (comma) separates two statements
  I HAS A result
BUHBYE

BTW ---------- output ----------
VISIBLE "=== output ==="
VISIBLE "name:: " + name + " | ratio:: " + ratio + " | neg:: " + neg
VISIBLE "no newline after this"!
VISIBLE " <- same line"
VISIBLE "a"!, VISIBLE "b"!, VISIBLE "c"      BTW "!" and soft breaks together
VISIBLE tricky
VISIBLE SMOOSH "SMOOSH " AN "as " AN "an operand" + " ok"
VISIBLE ALL OF WIN AN total AN flag MKAY
SUM OF 1 AN 2                                BTW an expression statement: the result goes to IT
VISIBLE "IT = " + IT

BTW ---------- arithmetic: all seven operators, plus nesting ----------
result R SUM OF total AN 2
result R DIFF OF total AN 2
result R PRODUKT OF total AN 2
result R QUOSHUNT OF total AN 4
result R MOD OF total AN 3
result R BIGGR OF total AN ratio
result R SMALLR OF total AN ratio
result R SUM OF PRODUKT OF 2 AN 3 AN QUOSHUNT OF 8 AN 2      BTW (2*3)+(8/2)
result R SUM OF SUM OF SUM OF 3 AN 4 AN 2 AN 1               BTW ((3+4)+2)+1
VISIBLE "result:: " + result

BTW ---------- assignment ----------
copy R 5                                     BTW from a literal
copy R total                                 BTW from another variable
copy R SUM OF total AN neg                   BTW from an expression
total R 1, result R 2, copy R 3              BTW three statements on one line

BTW ---------- boolean ----------
flag R BOTH OF WIN AN FAIL
flag R EITHER OF flag AN WIN
flag R WON OF flag AN WIN
flag R NOT flag
flag R ALL OF WIN AN NOT FAIL AN BOTH OF WIN AN WIN MKAY     BTW infinite arity, needs MKAY
flag R ANY OF FAIL AN FAIL AN WIN MKAY

BTW ---------- comparison (and relational operators built from BIGGR/SMALLR) ----------
total R 10
other R BOTH SAEM total AN 10
other R DIFFRINT total AN 10
other R BOTH SAEM total AN BIGGR OF total AN 3               BTW total >= 3
other R BOTH SAEM total AN SMALLR OF total AN 3              BTW total <= 3
other R DIFFRINT total AN SMALLR OF total AN 3               BTW total > 3
other R DIFFRINT total AN BIGGR OF total AN 3                BTW total < 3

BTW ---------- concatenation ----------
joined R SMOOSH "total=" AN total AN ", ratio=" AN ratio AN ", flag=" AN flag
VISIBLE joined

BTW ---------- typecasting ----------
MAEK ratio A NUMBR                           BTW explicit cast: result goes to IT, ratio is unchanged
MAEK total YARN                              BTW the "A" is optional
result R MAEK ratio A NUMBAR
result R MAEK total YARN
text R MAEK empty YARN                       BTW explicit cast of a NOOB is allowed
ratio IS NOW A NUMBR                         BTW re-cast the variable itself
ratio IS NOW A NUMBAR
empty IS NOW A TROOF

BTW ---------- input ----------
VISIBLE "Type something:: "!
GIMMEH text
VISIBLE "You typed:: " + text

BTW ---------- if / else-if / else ----------
BOTH SAEM total AN 10
O RLY?
  YA RLY
    VISIBLE "total is ten"
  MEBBE BOTH SAEM total AN 20
    VISIBLE "total is twenty"
  MEBBE DIFFRINT total AN 30
    VISIBLE "total is not thirty"
  NO WAI
    VISIBLE "total is something else:)not this"
OIC

BTW if-else nested inside if-else
BOTH SAEM flag AN WIN
O RLY?
  YA RLY
    BOTH SAEM total AN 10
    O RLY?
      YA RLY
        VISIBLE "flag is WIN and total is 10"
      NO WAI
        VISIBLE "flag is WIN, total is not 10"
    OIC
  NO WAI
    VISIBLE "flag is FAIL"
OIC

BTW ---------- switch-case: every literal type, fall-through, GTFO, default ----------
total
WTF?
  OMG 5
    VISIBLE "five"
    GTFO
  OMG 3.5
    VISIBLE "three point five"
    GTFO
  OMG 10
    VISIBLE "ten, and without a GTFO control falls through"
  OMG "ten"
    VISIBLE "the YARN ten"
    GTFO
  OMG WIN
    VISIBLE "WIN"
    GTFO
  OMGWTF
    VISIBLE "no case matched"
OIC

BTW ---------- loops ----------
i R 2
IM IN YR counter UPPIN YR i TIL BOTH SAEM i AN 5           BTW TIL: repeats while the test is FAIL
  VISIBLE "up:: " + i
IM OUTTA YR counter

i R 3
IM IN YR countdown NERFIN YR i WILE DIFFRINT i AN 0        BTW WILE: repeats while the test is WIN
  VISIBLE "down:: " + i
IM OUTTA YR countdown

i R 0
IM IN YR forever UPPIN YR i                                BTW no TIL or WILE: leaves only through GTFO
  BOTH SAEM i AN 3
  O RLY?
    YA RLY
      GTFO
  OIC
IM OUTTA YR forever

BTW loop nested in a loop; GTFO leaves only the inner loop
i R 0
IM IN YR outer UPPIN YR i TIL BOTH SAEM i AN 2
  j R 0
  IM IN YR inner UPPIN YR j WILE DIFFRINT j AN 3
    VISIBLE "i=" + i + " j=" + j
    BOTH SAEM j AN 1
    O RLY?
      YA RLY
        GTFO
    OIC
  IM OUTTA YR inner
IM OUTTA YR outer

BTW ---------- different flow-control statements nested: loop > switch > if ----------
i R 0
IM IN YR walker UPPIN YR i TIL BOTH SAEM i AN 4
  i
  WTF?
    OMG 1
      VISIBLE "one"
      GTFO
    OMG 2
      BOTH SAEM total AN 10
      O RLY?
        YA RLY
          VISIBLE "two, and total is ten"
        NO WAI
          VISIBLE "two"
      OIC
      GTFO
    OMGWTF
      VISIBLE "other:: " + i
  OIC
IM OUTTA YR walker

BTW ---------- function calls ----------
VISIBLE "square of 7 = " + I IZ square YR 7 MKAY
VISIBLE "5 factorial = " + I IZ factorial YR 5 MKAY
VISIBLE "square of square of 2 = " + I IZ square YR I IZ square YR 2 MKAY MKAY
VISIBLE "clamp(15, 0, 10) = " + I IZ clamp YR 15 AN YR 0 AN YR 10 MKAY
result R I IZ max_of YR total AN YR 99 MKAY
VISIBLE "max_of = " + result
I IZ greet MKAY                              BTW a call used as a statement
VISIBLE "=== done ==="
KTHXBYE
BTW comments are allowed after KTHXBYE
OBTW
  And so are functions. This one is defined after KTHXBYE and never called.
TLDR

HOW IZ I unused_helper YR x
  FOUND YR x
IF U SAY SO
