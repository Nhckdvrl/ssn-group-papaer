"""L34 E01 — bioS-style synthetic biography generator.

Six independent attributes, partitioned into two mirrored query families.
Everything is deterministic given GEN_SEED.
"""
import json, random, os

GEN_SEED = 20260914

FAMILY_A = ["birth_date", "university", "work_city"]
FAMILY_B = ["birth_city", "company", "major"]
ATTRS = FAMILY_A + FAMILY_B
FAMILY = {a: "A" for a in FAMILY_A} | {a: "B" for a in FAMILY_B}

FIRST = """Aaron Abigail Adrian Alan Albert Alexis Alfred Alicia Allison Alvin Amanda Amber Andre Angela
Anita Anthony April Arthur Ashley Audrey Austin Barbara Barry Beatrice Bernard Bethany Beverly Blake Bonnie
Bradley Brandon Brenda Brian Bridget Brooke Bruce Bryan Caleb Cameron Candace Carl Carla Carmen Carol Carrie
Casey Cecil Cedric Celia Chad Charles Chelsea Cheryl Chester Chloe Christian Christy Clara Clarence Claude
Clayton Clifford Colin Connie Conrad Corey Courtney Craig Crystal Curtis Cynthia Dale Dana Daniel Danielle
Darren Daryl Dawn Dean Deborah Delia Dennis Derek Desmond Diana Dionne Dolores Dominic Donald Donna Dora
Douglas Drew Duane Dustin Dwight Earl Edgar Edith Edmund Edwin Eileen Elaine Eleanor Elias Elise Ellen Elmer
Eloise Elsie Emanuel Emily Enrique Eric Erin Ernest Esther Ethan Eugene Eunice Evan Evelyn Everett Fay Felix
Fernando Fiona Flora Floyd Frances Franklin Fred Gabriel Gail Garrett Gavin Gayle Gene Geoffrey Georgia Gerald
Gilbert Gina Glenn Gloria Gordon Grace Grant Gregory Gwen Hannah Harold Harriet Harvey Hazel Heather Hector
Helen Henry Herbert Hilda Holly Homer Hope Horace Howard Hugh Ian Ida Imelda Ingrid Irene Irving Isaac Ivan
Jacob Jacqueline Jared Jasmine Jasper Jeanette Jeffrey Jenna Jeremy Jerome Jesse Jillian Joan Joel Jolene
Jonathan Jordan Josephine Joshua Joyce Juanita Judith Julian Juliet June Justin Karen Karl Kate Kathleen
Kayla Keith Kelvin Kendra Kenneth Kent Kevin Kimberly Kirk Kristin Kurt Kyle Lance Larry Laura Lawrence Leah
Leon Leonard Leroy Leslie Lester Lewis Lila Lillian Lionel Lloyd Logan Lois Lorraine Louis Lucas Lucille Luther
Lydia Lyle Lynn Mabel Madeline Malcolm Mallory Marcia Marcus Margaret Marian Marilyn Mario Marjorie Marlon
Marsha Martin Marvin Mason Matthew Maureen Maurice Maxine Megan Melanie Melvin Mercedes Meredith Michele
Mildred Miles Milton Miranda Mitchell Molly Monica Morgan Moses Muriel Myra Myron Nadine Nancy Naomi Natalie
Nathan Neal Nelson Nicholas Nicole Nina Noah Nora Norman Octavia Olive Oliver Ollie Opal Oscar Owen Pamela
Patricia Patrick Paula Pearl Percy Perry Peter Philip Phoebe Phyllis Preston Priscilla Quentin Rachel Ralph
Ramona Randall Raymond Rebecca Regina Renee Reuben Rhonda Ricardo Rita Roberta Robin Roderick Rodney Roger
Roland Rosalind Rosemary Ross Roy Ruben Rudolph Rufus Russell Ruth Ryan Sabrina Salvador Samantha Sandra
Saul Selena Seth Shane Shannon Sharon Sheila Shelby Sheldon Sherman Sidney Silas Simon Sonia Spencer Stacey
Stanley Stella Stephanie Sterling Stuart Sylvia Tamara Tanya Terrence Thelma Theodore Theresa Tiffany Timothy
Tobias Todd Tracy Travis Trevor Trisha Troy Tyrone Ulysses Ursula Valerie Vanessa Vaughn Velma Vera Vernon
Veronica Victor Vincent Viola Virgil Vivian Wade Wallace Walter Wanda Warren Wayne Wendell Wesley Whitney
Wilbur Wilfred Willard Willis Wilma Winifred Woodrow Yolanda Yvette Zachary Zelda""".split()

LAST = """Abbott Ackerman Adkins Aguilar Alderman Aldrich Almeida Alvarado Ambrose Anderson Applegate Archer
Arrington Ashby Atwater Aubrey Babcock Bagley Bainbridge Baldwin Ballard Bancroft Banister Barclay Barlow
Barnaby Barrett Bartlett Bassett Batchelder Bateman Baxter Beaumont Beckwith Bellamy Bennington Berkeley
Bergstrom Bethune Bickford Billings Birchwood Blackwell Blakely Blanchard Bledsoe Bolton Bonham Boswell
Bourne Bowditch Bradbury Bradshaw Braithwaite Brandenburg Brennan Brewster Bridgeman Brockway Brookings
Broughton Brunswick Buckingham Bullard Burgess Burnham Burroughs Butterfield Cadwallader Caldwell Calloway
Camden Canfield Carlisle Carrington Cartwright Castellano Caswell Chadwick Chamberlin Chandler Chapman
Charlton Chesterton Chilton Clapham Claridge Clarkson Claypool Cleveland Clifton Coburn Colborne Colefax
Collingwood Compton Conway Copeland Cornelius Cotswold Courtland Covington Cranston Crawford Crenshaw
Crichton Crocker Cromwell Crosby Cullen Cunningham Dalrymple Danvers Darlington Davenport Dearborn Delacroix
Denholm Dennison Derwent Devereux Dinsmore Doncaster Donnelly Dorchester Dorsey Doughty Drayton Driscoll
Dunbarton Duncombe Dunmore Durham Eastwood Eddington Edgerton Ellsworth Elmhurst Emerson Endicott Ericson
Esterbrook Everhart Fairbanks Fairchild Falconer Farnsworth Faulkner Fenwick Ferguson Fielding Finnegan
Fitzgerald Flanagan Fleetwood Fletcher Forsythe Fothergill Frampton Fitzwilliam Gallagher Galloway Garfield
Garrison Gatlinburg Gentry Gibbons Gilchrist Gillespie Glendale Godfrey Goodwin Gorham Granville Greenfield
Greenleaf Gresham Griffiths Grimsby Grosvenor Hadley Haggerty Halliwell Hammond Hampstead Hancock Hargrove
Harlow Harrington Hartley Harwood Hastings Hathaway Haverford Hawthorne Haywood Hazelton Heathcote Hedgepeth
Helmsley Henderson Herrington Hewlett Hightower Hildreth Hillingdon Hobson Holbrook Hollister Holloway
Hopkinson Hornsby Houghton Hufford Huntington Hurlbert Ingersoll Inglewood Irwin Ivanhoe Jefferson Jennings
Jessup Johannsen Kendrick Kenilworth Kensington Kerrigan Kettering Kilbride Kingsbury Kirkpatrick Knightley
Lancaster Langford Lansdowne Larkspur Lathrop Laughlin Lavender Leatherwood Ledbetter Lexington Lindqvist
Litchfield Livingston Lockridge Loughlin Lovelace Ludlow Lyndhurst Macalister Mansfield Marchetti Marlborough
Marlowe Mathison Maxfield Mayweather Mcallister Meriwether Merriman Middleton Millbrook Montgomery Moorcroft
Mortimer Mulholland Nethercott Newberry Newcomb Nightingale Norcross Northrop Oakhurst Ockenden Ogilvie
Olmstead Osbourne Ottoway Overton Paddington Palgrave Pemberton Pendleton Penhallow Pennington Percival
Pettigrew Pickering Pinkerton Plimpton Ponsonby Prescott Prichard Quarrington Quinlan Radcliffe Ramsbottom
Ravensworth Redmayne Remington Renshaw Rhodesdale Ridgeway Rockwell Rothwell Rutherford Salisbury Sandringham
Satterfield Saunders Scarborough Scrivener Selwyn Shackleton Sheffield Shelburne Sheridan Sherwood Shropshire
Silverthorne Sinclair Slaughter Somerville Southgate Spalding Stanhope Stapleton Sterling Stockbridge
Stonebridge Strickland Summerfield Sutherland Swinburne Tallmadge Tanhouse Tewkesbury Thackeray Thorndike
Threlkeld Tillingham Torrington Trembath Trenholm Trevelyan Truesdale Underhill Vanderberg Vansittart
Verrinder Wadsworth Wainwright Wakefield Waldgrave Wallingford Warrington Waterhouse Weatherby Wellington
Wentworth Westbrook Wetherall Wheatley Whitcomb Whitfield Whittaker Wickersham Willoughby Winchester
Windermere Wingfield Winthrop Witherspoon Wolcott Woodbridge Woolrich Worthington Wycherley Yarborough""".split()

_US = """Akron Albany Allentown Amarillo Anaheim Annapolis Appleton Arlington Asheville Athens Auburn Augusta
Aurora Bakersfield Baltimore Bangor Baton Bellevue Bellingham Beloit Bend Berkeley Bethlehem Billings Biloxi
Binghamton Bismarck Bloomington Boise Boulder Bozeman Bradenton Bremerton Bridgeport Bristol Brockton
Brownsville Bryan Buffalo Burbank Burlington Camden Canton Carlsbad Cary Cedar Champaign Chandler Charleston
Charlotte Chattanooga Cheyenne Chico Cincinnati Clarksville Clearwater Cleveland Clovis Columbia Columbus
Concord Corvallis Cranston Dalton Danbury Davenport Dayton Daytona Dearborn Decatur Denton Derry Dothan
Dover Dubuque Duluth Dunedin Durham Eugene Evanston Everett Fairbanks Fargo Fayetteville Flagstaff Flint
Florence Fresno Frederick Fremont Gainesville Galveston Gastonia Geneva Gilbert Glendale Goldsboro Greeley
Greenville Hagerstown Hammond Hampton Hanover Harrisburg Hartford Hattiesburg Helena Hoboken Hollywood
Honolulu Hoover Houma Huntsville Independence Irvine Ithaca Jacksonville Janesville Jonesboro Joplin Juneau
Kalamazoo Kankakee Kearney Kenosha Kingston Knoxville Kokomo Lafayette Lakeland Lancaster Lansing Laredo
Lawrence Lebanon Lewiston Lexington Lima Lincoln Longmont Longview Lorain Lowell Lubbock Lynchburg Macon
Madison Manchester Mankato Mansfield Marietta Marion McAllen Medford Melbourne Meridian Merced Mesa Midland
Missoula Mobile Modesto Moline Monroe Montgomery Muncie Muskegon Nampa Napa Nashua Natchez Newark Newport
Norfolk Norman Norwalk Oakland Ocala Odessa Ogden Olympia Omaha Ontario Orem Oshkosh Owensboro Oxnard Paducah
Palmdale Parkersburg Pasadena Paterson Pensacola Peoria Petaluma Pittsfield Plano Pocatello Pomona Ponca
Portsmouth Poughkeepsie Prescott Provo Pueblo Racine Raleigh Reading Redding Redmond Reno Richmond Riverside
Roanoke Rochester Rockford Roswell Sacramento Saginaw Salem Salinas Sandusky Sanford Sarasota Savannah
Schenectady Scranton Sheboygan Shreveport Sioux Slidell Sparks Spokane Springfield Stamford Stockton
Sunnyvale Syracuse Tacoma Tallahassee Tempe Terre Texarkana Toledo Topeka Torrance Trenton Tucson Tulsa
Tupelo Tuscaloosa Tyler Utica Valdosta Vallejo Vancouver Ventura Vicksburg Victoria Vineland Visalia Waco
Waterbury Waterloo Watertown Waukesha Wausau Weirton Wenatchee Westminster Wheeling Wichita Williamsport
Wilmington Winchester Woonsocket Worcester Wyoming Yakima Yonkers Youngstown Yuma Zanesville""".split()

UNIS = ["the University of " + c for c in _US[:170]]
COMPANIES = [c + " Industries" for c in _US[170:]] + [c + " Systems" for c in _US[:120]]

MAJORS = """Accounting Acoustics Aeronautics Agronomy Anthropology Archaeology Architecture Astronomy
Astrophysics Biochemistry Bioinformatics Biophysics Botany Cartography Ceramics Chemistry Climatology
Criminology Cryptography Cytology Demography Dentistry Dermatology Ecology Econometrics Economics Education
Egyptology Electronics Entomology Epidemiology Ergonomics Ethnomusicology Finance Forestry Genetics Geodesy
Geology Geophysics Gerontology Glaciology Graphic Hematology Herpetology Histology Horticulture Hydrology
Immunology Journalism Kinesiology Limnology Linguistics Lithography Logistics Marketing Metallurgy
Meteorology Microbiology Mineralogy Musicology Mycology Nanotechnology Neurobiology Neuroscience Nursing
Nutrition Oceanography Oncology Optics Ornithology Orthodontics Paleontology Parasitology Pathology Pedagogy
Pharmacology Philology Philosophy Phonetics Photogrammetry Physiology Phytopathology Planetology Podiatry
Primatology Psychology Radiology Rheology Robotics Sedimentology Seismology Semiotics Sociology Soil
Statistics Stratigraphy Taxonomy Textiles Theology Thermodynamics Topology Toxicology Urbanism Virology
Viticulture Volcanology Zoology""".split()

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
STATES = "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()


def build_pools(rng):
    """Disjoint city pools for birth_city vs work_city (no cross-family 'answer a city' transfer)."""
    cities = [f"{c}, {rng.choice(STATES)}" for c in _US]
    rng.shuffle(cities)
    half = len(cities) // 2
    return {
        "birth_date": [f"{m} {d}, {y}" for m in MONTHS for d in (3, 9, 14, 21, 27) for y in range(1948, 2004, 7)],
        "birth_city": cities[:half],
        "university": list(UNIS),
        "major": list(MAJORS),
        "company": list(COMPANIES),
        "work_city": cities[half:],
    }


# --- biography templates: 5 orderings, one clause per attribute, no pronouns ---
CLAUSES = {
    "birth_date": "{n} was born on {v}.",
    "birth_city": "{n} spent their earliest years in {v}.",
    "university": "{n} completed their degree at {v}.",
    "major": "{n} concentrated their studies on {v}.",
    "company": "{n} took up a post at {v}.",
    "work_city": "{n} carried out that work in {v}.",
}
ORDERS = [
    ["birth_date", "birth_city", "university", "major", "company", "work_city"],
    ["university", "major", "birth_date", "company", "work_city", "birth_city"],
    ["company", "work_city", "birth_city", "birth_date", "university", "major"],
    ["major", "company", "birth_date", "work_city", "university", "birth_city"],
    ["birth_city", "university", "work_city", "major", "birth_date", "company"],
]

# --- QA templates: index 0 is trained (held-in); 1,2 are held-out paraphrases (eval only) ---
QA_T = {
    "birth_date": ["What is the birth date of {n}?",
                   "On what date was {n} born?",
                   "{n} came into the world on which date?"],
    "birth_city": ["What is the birth city of {n}?",
                   "In which city was {n} born?",
                   "{n} was brought up in which city?"],
    "university": ["Which university did {n} attend?",
                   "Where did {n} earn their degree?",
                   "{n} graduated from which institution?"],
    "major": ["What did {n} major in?",
              "Which field did {n} specialise in?",
              "{n} devoted their studies to which subject?"],
    "company": ["Which company did {n} work for?",
                "Who was the employer of {n}?",
                "{n} was on the staff of which firm?"],
    "work_city": ["In which city did {n} work?",
                  "Where was {n} based for work?",
                  "{n} did that job in which city?"],
}


def qa_text(name, attr, value, t=0):
    return f"Question: {QA_T[attr][t].format(n=name)}\nAnswer: ", value


def bio_text(p, order_idx):
    return " ".join(CLAUSES[a].format(n=p["name"], v=p["attrs"][a]) for a in ORDERS[order_idx])


def generate(n_format=600, n_old=2000, n_pit=1500, n_new=2000, seed=GEN_SEED):
    rng = random.Random(seed)
    pools = build_pools(rng)
    total = n_format + n_old + n_pit + n_new
    names = set()
    while len(names) < total:
        names.add(f"{rng.choice(FIRST)} {rng.choice(LAST)}")
    names = sorted(names)
    rng.shuffle(names)
    people = []
    for nm in names:
        people.append({"name": nm, "attrs": {a: rng.choice(pools[a]) for a in ATTRS}})
    i = 0
    sets = {}
    for k, n in [("FORMAT", n_format), ("OLD", n_old), ("PIT", n_pit), ("NEW", n_new)]:
        sets[k] = people[i:i + n]
        i += n
    return sets, pools


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out, exist_ok=True)
    sets, pools = generate()
    json.dump({k: v for k, v in sets.items()}, open(os.path.join(out, "people.json"), "w"), indent=0)
    json.dump(pools, open(os.path.join(out, "pools.json"), "w"), indent=0)
    for k, v in sets.items():
        print(k, len(v), v[0]["name"], "|", bio_text(v[0], 0)[:110])
    print({k: len(v) for k, v in pools.items()})
