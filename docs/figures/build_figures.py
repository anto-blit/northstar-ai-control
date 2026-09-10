"""Build NorthStar's editable SVG graphics with the Python standard library."""
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
INK = "#102d3b"
MUTED = "#55717b"
TEAL = "#087f79"
CORAL = "#c5673a"
PAPER = "#f6f4ee"
FONT = "Segoe UI,Arial,Helvetica,sans-serif"


def text(x, y, value, size=24, color=INK, weight=400, anchor="start", spacing=0):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}" '
            f'letter-spacing="{spacing}">{escape(value)}</text>')


def rect(x, y, w, h, fill, stroke="none", radius=18):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def path(d, color=TEAL, width=3, dash=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{dash}"/>'


def circle(x, y, radius, fill, stroke="none", width=2):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def star(x, y, size, color):
    return f'<path d="M{x} {y-size} L{x+size*.19} {y-size*.19} L{x+size} {y} L{x+size*.19} {y+size*.19} L{x} {y+size} L{x-size*.19} {y+size*.19} L{x-size} {y} L{x-size*.19} {y-size*.19} Z" fill="{color}"/>'


def write_svg(name, title, description, body, height=700, background=PAPER, defs=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-labelledby="title desc">\n'
           f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(description)}</desc>\n'
           f'<defs>{defs}</defs>\n<rect width="1600" height="{height}" fill="{background}"/>\n'
           + "\n".join(body) + "\n</svg>\n")
    (HERE / name).write_text(svg, encoding="utf-8", newline="\n")


def heading(kicker, title, subtitle):
    return [star(68, 56, 16, TEAL), text(102, 64, kicker, 18, TEAL, 700, spacing=3),
            text(52, 133, title, 45, weight=700), text(54, 178, subtitle, 24, MUTED)]


def footer(label, height):
    return [path(f"M54 {height-62} H1546", "#d7dfda", 1),
            text(54, height-28, "NORTHSTAR  /  CALIBRATED VISION", 15, MUTED, 600, spacing=1),
            text(1546, height-28, label, 17, MUTED, anchor="end")]


def hero():
    defs = '''<radialGradient id="glow"><stop stop-color="#187f80" stop-opacity=".65"/><stop offset="1" stop-color="#071923" stop-opacity="0"/></radialGradient>
    <linearGradient id="route" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#2d676f"/><stop offset="1" stop-color="#83f1d2"/></linearGradient>
    <pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse"><path d="M64 0H0V64" fill="none" stroke="#60818c" stroke-opacity=".09"/></pattern>'''
    b = ['<rect width="1600" height="720" fill="url(#grid)"/>',
         '<ellipse cx="1260" cy="320" rx="460" ry="440" fill="url(#glow)"/>']
    for radius in (125, 210, 298):
        b.append(circle(1258, 289, radius, "none", "#24505c", 1.5))
    b += [path("M948 720 C924 545 1060 569 1127 456 S1208 375 1258 289", "url(#route)", 5),
          path("M1080 710 C1140 580 1270 629 1355 516 S1447 375 1258 289", "#316675", 2),
          path("M1600 442 L1450 390 L1375 223 L1258 289 L1097 197 L989 70", "#3e737a", 2),
          path("M1135 91 L1258 289 L1475 113", "#335c65", 2, "5 10"),
          path("M1097 197 L1114 371 L1258 289 L1409 438", "#4c8e8a", 2)]
    for x, y, r in [(948,650,7),(1050,530,6),(1127,456,8),(1200,364,5),(1097,197,5),
                    (1114,371,4),(1375,223,6),(1450,390,5),(1355,516,6),(1135,91,4),(1475,113,5)]:
        b += [circle(x,y,r+7,"#0d2631"), circle(x,y,r,"#69c6b4")]
    b += [circle(1258,289,60,"#0e3841","#589b97",1), star(1258,289,89,"#c0fff0"),
          star(1258,289,43,"#ffffff"),
          text(1514,61,"CALIBRATED VISION",16,"#a9c9c8",600,anchor="end",spacing=2),
          text(1514,87,"AN OPEN RESEARCH PROJECT",12,"#7ba0a5",anchor="end",spacing=1.8),
          star(94,86,22,"#83f1d2"), text(135,96,"NORTHSTAR",27,"#e5f4ef",700,spacing=6),
          text(80,218,"Protecting humanity’s",66,"#f6f4ee",700),
          text(80,297,"freedom and future",66,"#f6f4ee",700),
          text(80,376,"in an AI world.",66,"#f6f4ee",700),
          text(84,443,"Archetype-guided AI control research",28,"#bed1d2"),
          text(84,482,"for preserving human recoverability.",28,"#bed1d2"),
          rect(83,528,362,49,"#153c44","#36666a",25),
          circle(107,553,5,"#83f1d2"), text(127,560,"BUILD  /  CHALLENGE  /  REPLICATE",16,"#a6ead8",600),
          path("M84 618 H820","#2d4852",1),
          text(84,660,"github.com/anto-blit/northstar-ai-control",22,"#e7bc90"),
          rect(1110,581,303,47,"#102e38","#3d6870",8),
          text(1261,611,"HUMAN FREEDOM",18,"#b8e4d8",600,anchor="middle",spacing=2)]
    write_svg("northstar-hero.svg", "NorthStar: Protecting humanity’s freedom and future in an AI world",
              "A luminous north star guides branching paths. Archetype-guided AI control research for preserving human recoverability. Build, challenge, and replicate.",
              b, 720, "#071923", defs)


def archetypes():
    b = heading("THE SEARCH HYPOTHESIS", "Old warnings. Testable failure mechanisms.",
                "Five story patterns suggest where to look. Experiments decide whether the safeguards hold.")
    cards = [
        ("01", "Camel's nose", ["Small permissions.", "Growing authority."], ["Track what permissions", "can do together."]),
        ("02", "Trojan horse", ["Useful function.", "Hidden effect."], ["Inspect what a component", "can actually change."]),
        ("03", "Faust", ["Success today.", "An obligation later."], ["Follow queued commitments", "beyond the checkpoint."]),
        ("04", "Pandora", ["One action.", "No taking it back."], ["Check authority before", "the irreversible commit."]),
        ("05", "Sorcerer's apprentice", ["The parent stops.", "The work continues."], ["Revoke the authority", "of every descendant."]),
    ]
    icons = [
        path("M10 86H42V66H74V44H106V20H133",TEAL,5)+path("M121 20H133V32",TEAL,5),
        path("M25 40L75 16L125 40V93L75 117L25 93Z M25 40L75 65L125 40 M75 65V117",TEAL,3)+circle(103,87,16,"#f5d7c4")+star(103,87,10,CORAL),
        circle(66,59,42,"none",TEAL,3)+path("M66 32V59L89 72",TEAL,4)+path("M103 89H133 M125 81L133 89L125 97",CORAL,3),
        path("M20 61L73 84L126 61 M20 61V102L73 126L126 102V61 M73 84V125 M24 52L57 25L99 44",TEAL,3)+path("M103 26L127 8 M114 8H127V21",CORAL,4),
        path("M74 26V55 M27 83V55H122V83",TEAL,3)+circle(74,19,12,"#f3d7c6",CORAL)+circle(27,96,13,"#d9efdf",TEAL)+circle(122,96,13,"#d9efdf",TEAL)+path("M69 19H79",CORAL,3),
    ]
    for i,(number,name,lines,detail) in enumerate(cards):
        x = 52 + i*302
        b += [rect(x,225,284,386,"#ffffff","#d9e2dc",18),
              text(x+22,260,number,16,MUTED,600,spacing=2),
              f'<g transform="translate({x+61},278)">{icons[i]}</g>',
              text(x+22,441,name,21,TEAL,700),
              text(x+22,478,lines[0],22,weight=650),text(x+22,507,lines[1],22,weight=650),
              text(x+22,551,detail[0],17,MUTED),text(x+22,576,detail[1],17,MUTED)]
    b += footer("Hypotheses to investigate — not proof of an advantage",700)
    write_svg("northstar-overview.svg","Five archetypes, five testable mechanisms",
              "Camel's nose: cumulative authority. Trojan horse: hidden effects. Faust: deferred commitments. Pandora: irreversible release. Sorcerer's apprentice: work continuing after stop.",b)


def pipeline():
    b = heading("FROM DISCOVERY TO PREVENTION", "A good story is only the beginning.",
                "The goal is a safeguard that survives a fresh challenge and still lets people do useful work.")
    labels = [("01","HYPOTHESIS",["Identify a causal", "failure pattern."]),
              ("02","EXECUTABLE TEST",["Make the failure", "happen in simulation."]),
              ("03","BENIGN TWIN",["Change the decisive", "fact. Keep the task."]),
              ("04","OBSERVED EFFECT",["Score the episode", "and pending work."]),
              ("05","REPAIR",["Enforce the missing", "boundary."]),
              ("06","FRESH CHALLENGE",["Try unfamiliar cases", "and adaptive attacks."])]
    for i,(number,label,lines) in enumerate(labels):
        x=52+i*251
        b += [rect(x,253,234,219,"#102f3d" if i==5 else "#ffffff","#d9e2dc",14),
              circle(x+35,291,17,"#254e57" if i==5 else "#e0efea"),
              text(x+35,297,number,14,"#b5ebd9" if i==5 else TEAL,700,anchor="middle"),
              text(x+20,342,label,16,"#b5ebd9" if i==5 else TEAL,700),
              text(x+20,386,lines[0],20,"#f6f4ee" if i==5 else INK,600),
              text(x+20,416,lines[1],20,"#f6f4ee" if i==5 else INK,600)]
        if i<5:
            b += [path(f"M{x+235} 364H{x+247}",TEAL,2),path(f"M{x+242} 359L{x+247} 364L{x+242} 369",TEAL,2)]
    b += [rect(52,510,1489,75,"#e4eee6",radius=10),
          text(81,555,"THE BAR:",18,TEAL,700,spacing=1),
          text(195,555,"Better prevention at useful capability — compared with strong conventional methods.",24,INK,600)]
    b += footer("The full comparative discovery-to-prevention study remains to be run",680)
    write_svg("archetype-to-control-test.svg","From causal hypothesis to independently challenged repair",
              "Six stages: hypothesis, executable test, benign twin, observed effect, repair, and fresh challenge. The primary goal is improved prevention with legitimate usefulness.",b,680)


def enforcement():
    b=heading("THE PROPOSED CONTROL BOUNDARY","The agent proposes. The broker controls effects.",
              "Hard constraints, current authority, and intervention powers must hold even under deliberate subversion.")
    b += [rect(490,220,376,66,"#dfede5"),text(678,248,"INDEPENDENT HUMAN AUTHORITY",16,TEAL,700,anchor="middle"),
          text(678,273,"Stop / revoke scope",19,INK,anchor="middle"),
          path("M678 287V324",TEAL,3),path("M671 317L678 324L685 317",TEAL,3),
          rect(910,220,356,66,"#ece8df"),text(1088,248,"FALLIBLE MONITOR",16,MUTED,700,anchor="middle"),
          text(1088,273,"A verdict cannot override hard checks",16,INK,anchor="middle"),
          path("M947 287L867 323",MUTED,2,"5 6")]
    blocks=[(52,320,292,"UNTRUSTED AGENT",["Proposes actions", "May try to defeat safeguards"]),
            (408,320,502,"EFFECT BROKER",["Check scope + shared state", "Revalidate before committing"]),
            (974,320,245,"STATE + LEDGER",["Record the transition", "and its receipt together"]),
            (1283,320,265,"SIMULATED EFFECT",["Release or dispatch", "inside the declared model"])]
    for x,y,w,label,lines in blocks:
        dark=label=="EFFECT BROKER"
        b += [rect(x,y,w,144,"#102f3d" if dark else "#ffffff","#d9e2dc",14),
              text(x+22,y+34,label,18,"#9fe0cc" if dark else TEAL,700),
              text(x+22,y+79,lines[0],21,"#f6f4ee" if dark else INK,600),
              text(x+22,y+113,lines[1],17,"#c0d7d6" if dark else MUTED)]
    for x1,x2 in [(345,405),(912,971),(1221,1280)]:
        b += [path(f"M{x1} 392H{x2}",TEAL,3),path(f"M{x2-8} 385L{x2} 392L{x2-8} 399",TEAL,3)]
    b += [path("M503 465V512",CORAL,3),rect(407,512,193,48,"#f5e2d5",radius=9),
          text(503,542,"HOLD / REJECT",18,CORAL,700,anchor="middle"),
          path("M1414 465V572H753V466",TEAL,2,"6 7"),
          path("M746 473L753 466L760 473",TEAL,2),
          rect(880,550,450,44,PAPER,radius=0),
          text(1105,578,"Queued work returns through the broker",20,TEAL,600,anchor="middle")]
    b += footer("Specified architecture; full isolation and enforcement boundary not yet validated",695)
    write_svg("reference-enforcement-architecture.svg","Execution authority stays outside the untrusted agent",
              "Independent human authority and a fallible monitor feed an effect broker. The broker checks proposed actions, records state and ledger together, and mediates effects. Deferred work returns through the same broker.",b,695)


def irreversibility():
    b=heading("WHY INTERVENTION TIMING MATTERS","A warning after release is already too late.",
              "For a prohibited non-recallable effect, prevention must happen before the committing action.")
    b += [rect(52,233,960,275,"#e4eee6",radius=16),rect(1034,233,514,275,"#f3e3d6",radius=16),
          text(80,275,"THE INTERVENTION WINDOW",17,TEAL,700,spacing=1),
          text(1062,275,"COMMITTED HISTORY",17,CORAL,700,spacing=1),
          path("M120 353H1468",MUTED,3),
          path("M1460 346L1468 353L1460 360",MUTED,3)]
    points=[(190,"Stage", "Inspect the proposed effect."),(573,"Review + revalidate","Check current authority."),
            (1023,"Commit","The boundary is crossed."),(1430,"Record", "The effect remains.")]
    for x,label,detail in points:
        commit=label=="Commit"
        b += [circle(x,353,22,"#f6f4ee",CORAL if commit else TEAL,3),
              circle(x,353,7,CORAL if commit else TEAL),
              text(x,421,label,28,CORAL if commit else INK,700,anchor="middle"),
              text(x,458,detail,19,MUTED,anchor="middle")]
    b += [path("M1023 214V327 M1023 379V389 M1023 480V528",CORAL,3,"6 7"),
          text(82,565,"Stop, revoke, or hold while intervention can still work.",25,TEAL,600),
          text(82,607,"Score the whole episode. A later shutdown cannot erase a prohibited release.",24,INK,500)]
    b += footer("An authorized irreversible action is not automatically a failure",705)
    write_svg("irreversibility-boundary.svg","Intervene before a prohibited irreversible commit",
              "A timeline shows a reviewable stage, review and revalidation, the committing boundary, and persistent history. Later shutdown does not erase a prohibited release.",b,705)


if __name__ == "__main__":
    for build in (hero,archetypes,pipeline,enforcement,irreversibility):
        build()
    print("Built NorthStar cover and four explanatory SVG figures.")
