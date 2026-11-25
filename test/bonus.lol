HAI 1.2
WAZZUP
    I HAS A x ITZ 0
    I HAS A y ITZ 0
    I HAS A i ITZ 0
    I HAS A j ITZ 0
BUHBYE

BTW Soft-line / command breaks (,)
x R 1 , y R 2 , VISIBLE "Soft break: " + x + " " + y

BTW Special characters in a YARN / strings (:), :>, :", ::)
VISIBLE "Newline:)Tab:>Quote:\"Colon::"

BTW Line continuation (...)
VISIBLE "Line continuation " + ...
"works across lines"

BTW Suppress newline after VISIBLE with !
VISIBLE "Same line "!
VISIBLE "output"

BTW MEBBE / Else-if clauses
x R 2
BOTH SAEM x AN 1
O RLY?
    YA RLY
        VISIBLE "x is 1"
    MEBBE BOTH SAEM x AN 2
        VISIBLE "x is 2 (MEBBE)"
    NO WAI
        VISIBLE "x is other"
OIC

BTW If-else nesting
x R 1
y R 2
BOTH SAEM x AN 1
O RLY?
    YA RLY
        BOTH SAEM y AN 2
        O RLY?
            YA RLY
                VISIBLE "If-else nesting: inner YA RLY"
            NO WAI
                VISIBLE "If-else nesting: inner NO WAI"
        OIC
    NO WAI
        VISIBLE "If-else nesting: outer NO WAI"
OIC

BTW Switch-nesting
x R 1
y R 2
x
WTF?
    OMG 1
        y
        WTF?
            OMG 1
                VISIBLE "Switch nesting: 1-1"
                GTFO
            OMG 2
                VISIBLE "Switch nesting: 1-2"
                GTFO
            OMGWTF
                VISIBLE "Switch nesting: 1-default"
        OIC
        GTFO
    OMGWTF
        VISIBLE "Switch nesting: outer default"
OIC

BTW Loop-nesting
i R 0
IM IN YR outerLoop UPPIN YR i TIL BOTH SAEM i AN 2
    j R 0
    IM IN YR innerLoop UPPIN YR j TIL BOTH SAEM j AN 2
        VISIBLE "Loop nesting: " + i + "," + j
    IM OUTTA YR innerLoop
IM OUTTA YR outerLoop

BTW Nesting of different flow control statements (Loop -> Switch -> If-Else)
i R 0
IM IN YR mixLoop UPPIN YR i TIL BOTH SAEM i AN 2
    i
    WTF?
        OMG 0
            BOTH SAEM i AN 0
            O RLY?
                YA RLY
                    VISIBLE "Mixed nesting: loop -> switch -> if"
            OIC
            GTFO
        OMGWTF
            VISIBLE "Mixed nesting: loop -> switch -> default"
    OIC
IM OUTTA YR mixLoop

KTHXBYE