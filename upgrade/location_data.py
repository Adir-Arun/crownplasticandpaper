"""Service-area data for the location pages. Distances are approximate road miles from the
Houston warehouse (7350 Langfield Rd); transit is a typical LTL estimate after an order ships.
Every city carries its own route, food-scene and seasonal notes so no two pages are alike.
Not served from the site: the New York area and California."""

# slug: (name, state_code, county/region, miles, route, [food notes], seasonal note, [product slugs], [nearby slugs])
TEXAS = {
    'houston': ('Houston', 'TX', 'Harris County', 0, 'our own warehouse on Langfield Rd, inside Beltway 8 off US-290',
                ['One of the most diverse food cities in the country: Gulf seafood, Tex-Mex, barbecue and the Viet-Cajun crawfish style that started here.',
                 'Dense concentrations of restaurants along Bellaire Blvd, Westheimer and in the Heights keep to-go packaging moving year-round.'],
                'Rodeo season (late February to March) and crawfish season (roughly January to June) are the busiest stretches for trays, foil and gloves; hurricane season (June to November) is when kitchens stock extra.',
                ['black-nitrile-gloves', 'paper-boat-trays', 'round-foil-pans', 'deli-containers', 'black-containers'],
                ['katy', 'sugar-land', 'pasadena']),
    'katy': ('Katy', 'TX', 'Harris, Fort Bend and Waller counties', 30, 'I-10 West, about 40 minutes',
             ['A fast-growing western suburb with Katy Asian Town and a long line of family and fast-casual restaurants along Grand Parkway and I-10.',
              'Katy ISD is one of the largest school districts in Texas, so cafeteria trays and portion cups move in volume.'],
             'Back-to-school (August) and the holiday catering season are the peaks.',
             ['school-trays', 'portion-cups', 'black-hinged-containers', 'pet-cups', 'dinner-napkins'],
             ['houston', 'sugar-land', 'the-woodlands']),
    'sugar-land': ('Sugar Land', 'TX', 'Fort Bend County', 20, 'US-59 / I-69 South, about 30 minutes',
                   ['One of the most diverse suburbs in Texas, with South Asian, Chinese, Vietnamese and Nigerian restaurants alongside chains.',
                    'Town Square and the Imperial district bring event and catering demand.'],
                   'Festival weekends at Town Square and holiday catering lift orders in spring and late fall.',
                   ['deli-containers', 'black-containers', 'disposable-cutlery-kits', 'portion-cups', 'interfold-napkins'],
                   ['houston', 'katy', 'pearland']),
    'the-woodlands': ('The Woodlands', 'TX', 'Montgomery County', 30, 'I-45 North, about 40 minutes',
                      ['Market Street, the Waterway and Hughes Landing pack sit-down and fast-casual restaurants into a planned community.',
                       'Corporate campuses keep boxed-lunch and office catering steady through the week.'],
                      'The outdoor concert season at the Cynthia Woods Mitchell Pavilion (spring to fall) drives concession supplies.',
                      ['pet-cups', 'pet-cup-lids', 'black-containers', 'disposable-cutlery-kits', 'beverage-napkins'],
                      ['conroe', 'houston', 'katy']),
    'pasadena': ('Pasadena', 'TX', 'Harris County', 15, 'TX-225 East, about 20 minutes',
                 ['Home of the Port of Houston industrial corridor and the Ship Channel plants, where crew meals and plant cafeterias buy in bulk.',
                  'A long-standing Tex-Mex and taqueria scene along Spencer Highway and Red Bluff.'],
                 'Plant turnarounds (often spring and fall) bring surges of crew catering and glove orders.',
                 ['blue-nitrile-gloves', 'black-hinged-containers', 'trash-liners', 'food-film', 'c-fold-towel'],
                 ['houston', 'baytown', 'league-city']),
    'pearland': ('Pearland', 'TX', 'Brazoria County', 18, 'TX-288 South, about 25 minutes',
                 ['One of the fastest-growing suburbs in the Houston area, with new restaurant pads opening along Broadway and Shadow Creek.',
                  'Youth sports complexes and churches are steady buyers of plates, cups and napkins.'],
                 'Spring sports season and holiday events are the peaks.',
                 ['round-plates', 'pet-cups', 'dinner-napkins', 'deli-containers', 'trash-liners'],
                 ['houston', 'sugar-land', 'league-city']),
    'baytown': ('Baytown', 'TX', 'Harris and Chambers counties', 30, 'I-10 East, about 35 minutes',
                ['An industrial city built around one of the largest refining and petrochemical complexes in the country.',
                 'Contractor camps, plant cafeterias and family restaurants along Garth Rd buy gloves, liners and hinged containers.'],
                'Plant turnaround seasons and summer boating traffic on Trinity Bay lift volumes.',
                ['black-nitrile-gloves', 'black-hinged-containers', 'trash-liners', 'stretch-film', 'kraft-white-kitchen-roll-towels'],
                ['pasadena', 'houston', 'beaumont']),
    'conroe': ('Conroe', 'TX', 'Montgomery County seat', 40, 'I-45 North, about 50 minutes',
               ['The county seat north of Houston, with a historic downtown restaurant district and fast growth along I-45.',
                'Lake Conroe marinas and lakeside restaurants bring weekend and summer demand.'],
               'Summer lake season (May to September) is the busiest stretch for cups, liners and to-go containers.',
               ['pet-cups', 'black-containers', 'trash-liners', 'paper-bags', 'beverage-napkins'],
               ['the-woodlands', 'houston', 'college-station']),
    'league-city': ('League City', 'TX', 'Galveston County', 28, 'I-45 South, about 35 minutes',
                    ['Between Clear Lake and the Kemah Boardwalk, with seafood restaurants, marinas and NASA-area offices nearby.',
                     'Seafood boils and to-go orders lean on foil pans, boat trays and food film.'],
                    'Summer boardwalk and marina season is the peak; hurricane season is when kitchens stock extra.',
                    ['round-foil-pans', 'paper-boat-trays', 'food-film', 'checker-deli-paper-wrap', 'trash-liners'],
                    ['galveston', 'pasadena', 'pearland']),
    'galveston': ('Galveston', 'TX', 'Galveston County', 50, 'I-45 South to the causeway, about an hour',
                  ['An island tourism economy: Seawall Boulevard restaurants, The Strand, and one of the busiest cruise terminals in the US.',
                   'Seafood houses and beach concessions run on boat trays, deli paper and portion cups.'],
                  'Mardi Gras Galveston (February) and the summer beach season are the peaks; storm season means stocking ahead.',
                  ['paper-boat-trays', 'checker-deli-paper-wrap', 'portion-cups', 'pet-cups', 'trash-liners'],
                  ['league-city', 'houston', 'pasadena']),
    'beaumont': ('Beaumont', 'TX', 'Jefferson County', 85, 'I-10 East, about an hour and a half',
                 ['The Golden Triangle with Port Arthur and Orange: refinery country with a strong Cajun and Creole food influence from next-door Louisiana.',
                  'Boudin shops, seafood boils and plant catering keep foil pans and gloves moving.'],
                 'Crawfish season (spring) and refinery turnarounds are the busiest periods.',
                 ['round-foil-pans', 'deep-steam-table-pans', 'black-nitrile-gloves', 'paper-boat-trays', 'trash-liners'],
                 ['baytown', 'houston', 'new-orleans']),
    'college-station': ('College Station', 'TX', 'Brazos County', 95, 'US-290 and TX-6 northwest, about an hour and 45 minutes',
                        ['Home of Texas A&M, where campus dining, Northgate bars and restaurants serve a city that swells on game weekends.',
                         'Tailgating at Kyle Field is one of the largest in college football.'],
                        'Football season (September to November) and graduation weekends are the peaks.',
                        ['pet-cups', 'paper-boat-trays', 'round-plates', 'trash-liners', 'disposable-cutlery-kits'],
                        ['houston', 'austin', 'waco']),
    'austin': ('Austin', 'TX', 'Travis County', 165, 'US-290 West, about two and a half hours',
               ['A food-trailer capital, with parks of trucks across East Austin and South Congress alongside central-Texas barbecue.',
                'Tech campuses run large office catering programs.'],
               'SXSW (March) and Austin City Limits (October) bring the biggest event surges of the year.',
               ['black-hinged-containers', 'bagasse-hinged-containers', 'pet-cups', 'checker-deli-paper-wrap', 'portion-cups'],
               ['san-antonio', 'college-station', 'waco']),
    'san-antonio': ('San Antonio', 'TX', 'Bexar County', 200, 'I-10 West, about three hours',
                    ['Tex-Mex heartland: the River Walk, Pearl district and neighborhood taquerias, plus large military bases.',
                     'Tortilla factories and taco shops lean on foil sheets, deli paper and portion cups.'],
                    'Fiesta San Antonio (April) and the holiday River Walk season are the peaks.',
                    ['foil-sheets', 'checker-deli-paper-wrap', 'portion-cups', 'black-containers', 'interfold-napkins'],
                    ['austin', 'corpus-christi', 'laredo']),
    'dallas': ('Dallas', 'TX', 'Dallas County', 240, 'I-45 North, about three and a half hours',
               ['The center of the largest metro in Texas and headquarters to many national restaurant groups.',
                'Deep Ellum, Bishop Arts and Uptown pack independent restaurants next to chain locations.'],
               'The State Fair of Texas (late September to October) is the biggest concession event of the year.',
               ['black-containers', 'pet-cups', 'deli-containers', 'black-nitrile-gloves', 'paper-bags'],
               ['fort-worth', 'arlington', 'plano']),
    'fort-worth': ('Fort Worth', 'TX', 'Tarrant County', 265, 'I-45 North to I-20 West, about four hours',
                   ['Cowtown: the Stockyards, steakhouses and barbecue, with a growing food hall scene downtown and on Magnolia Avenue.',
                    'Ranch events and rodeos need plates, foil pans and boat trays in volume.'],
                   'The Fort Worth Stock Show & Rodeo (January to February) is the peak.',
                   ['round-foil-pans', 'paper-boat-trays', 'round-plates', 'black-nitrile-gloves', 'foil-rolls'],
                   ['dallas', 'arlington', 'waco']),
    'arlington': ('Arlington', 'TX', 'Tarrant County', 255, 'I-45 North to I-20 West, about four hours',
                  ['The entertainment district between Dallas and Fort Worth: AT&T Stadium, Globe Life Field and Six Flags Over Texas.',
                   'Stadium concessions and tailgates run on boat trays, PET cups and napkins.'],
                  'Football season, baseball season and summer park traffic overlap for most of the year.',
                  ['paper-boat-trays', 'pet-cups', 'pet-cup-lids', 'beverage-napkins', 'trash-liners'],
                  ['dallas', 'fort-worth', 'plano']),
    'plano': ('Plano', 'TX', 'Collin County', 260, 'I-45 North to US-75, about four hours',
              ['A corporate hub north of Dallas, with Legacy West and many company headquarters driving office catering.',
               'Dense suburban dining along the Dallas North Tollway and US-75.'],
              'Corporate catering peaks before the holidays; the Plano Balloon Festival (September) brings event demand.',
              ['disposable-cutlery-kits', 'black-containers', 'deli-containers', 'interfold-napkins', 'pet-cups'],
              ['dallas', 'arlington', 'fort-worth']),
    'el-paso': ('El Paso', 'TX', 'El Paso County', 745, 'I-10 West across Texas, about 11 hours',
                ['A border city with deep Mexican food traditions and Fort Bliss, one of the largest Army posts in the country.',
                 'Burrito shops and caterers lean on foil sheets and hinged containers.'],
                'Summer heat and the holiday season shape demand; schedule orders ahead because the trip is long.',
                ['foil-sheets', 'black-hinged-containers', 'portion-cups', 'black-nitrile-gloves', 'paper-bags'],
                ['san-antonio', 'lubbock', 'albuquerque']),
    'corpus-christi': ('Corpus Christi', 'TX', 'Nueces County', 210, 'US-59 / I-69 South and US-77, about three and a half hours',
                       ['A coastal city with a working port, Gulf seafood and North Padre Island beach traffic.',
                        'Seafood restaurants and beach concessions use boat trays, foil and liners.'],
                       'Summer beach season and spring break are the peaks; hurricane season means stocking ahead.',
                       ['paper-boat-trays', 'round-foil-pans', 'pet-cups', 'trash-liners', 'checker-deli-paper-wrap'],
                       ['san-antonio', 'mcallen', 'houston']),
    'mcallen': ('McAllen', 'TX', 'Hidalgo County', 350, 'US-59 / I-69 South and US-77, about five and a half hours',
                ['The heart of the Rio Grande Valley, with Mexican food traditions and cross-border retail.',
                 'Winter Texans swell the population and restaurant traffic every year.'],
                'Winter Texan season (November to March) is the peak.',
                ['foil-sheets', 'black-containers', 'portion-cups', 'dinner-napkins', 'black-nitrile-gloves'],
                ['corpus-christi', 'laredo', 'san-antonio']),
    'laredo': ('Laredo', 'TX', 'Webb County', 315, 'US-59 / I-69W southwest, about five hours',
               ['The busiest inland port in the US, with trucking, warehousing and a strong Mexican food scene.',
                'Truck stops and taquerias need hinged containers, foil and gloves.'],
               'Steady through the year; the Washington\'s Birthday Celebration (February) is a local peak.',
               ['black-hinged-containers', 'foil-sheets', 'black-nitrile-gloves', 'stretch-film', 'paper-bags'],
               ['san-antonio', 'mcallen', 'corpus-christi']),
    'lubbock': ('Lubbock', 'TX', 'Lubbock County', 520, 'US-290 West and US-84, about eight hours',
                ['Home of Texas Tech and the commercial center of the South Plains cotton and farming region.',
                 'Campus dining, game days and agricultural events drive demand.'],
                'Football season (fall) and the cotton harvest are the busy stretches.',
                ['pet-cups', 'paper-boat-trays', 'round-plates', 'trash-liners', 'black-nitrile-gloves'],
                ['el-paso', 'fort-worth', 'oklahoma-city']),
    'waco': ('Waco', 'TX', 'McLennan County', 185, 'TX-6 northwest, about three hours',
             ['Home of Baylor University and Magnolia Market, which draws visitors from across the country.',
              'A central I-35 stop between Austin and Dallas, with truck-stop and travel-center food service.'],
             'Baylor football and spring tourism are the peaks.',
             ['pet-cups', 'black-containers', 'paper-bags', 'disposable-cutlery-kits', 'trash-liners'],
             ['college-station', 'austin', 'dallas']),
}

# Out of state (no New York area, no California)
STATES = {
    'LA': ('Louisiana', 'louisiana'), 'OK': ('Oklahoma', 'oklahoma'), 'AR': ('Arkansas', 'arkansas'),
    'TN': ('Tennessee', 'tennessee'), 'GA': ('Georgia', 'georgia'), 'FL': ('Florida', 'florida'),
    'AL': ('Alabama', 'alabama'), 'MS': ('Mississippi', 'mississippi'), 'NC': ('North Carolina', 'north-carolina'),
    'AZ': ('Arizona', 'arizona'), 'CO': ('Colorado', 'colorado'), 'NV': ('Nevada', 'nevada'), 'MO': ('Missouri', 'missouri'),
    'IL': ('Illinois', 'illinois'), 'NM': ('New Mexico', 'new-mexico'), 'TX': ('Texas', 'texas'),
}

METROS = {
    'new-orleans': ('New Orleans', 'LA', 'Orleans Parish', 350, 'I-10 East, about five and a half hours',
                    ['Cajun and Creole cooking, po-boy shops and seafood boils, plus one of the busiest tourism and convention economies in the South.',
                     'Crawfish boils and catering lean on foil pans, boat trays and deli paper.'],
                    'Mardi Gras (January to February), Jazz Fest (late April to May) and crawfish season are the peaks.',
                    ['round-foil-pans', 'paper-boat-trays', 'checker-deli-paper-wrap', 'pet-cups', 'trash-liners'],
                    ['baton-rouge', 'jackson', 'beaumont']),
    'baton-rouge': ('Baton Rouge', 'LA', 'East Baton Rouge Parish', 270, 'I-10 East, about four hours',
                    ['The state capital and home of LSU, where Tiger Stadium tailgates are legendary.',
                     'Petrochemical plants along the Mississippi run plant cafeterias and crew catering.'],
                    'Football season (fall) and plant turnarounds are the peaks.',
                    ['paper-boat-trays', 'round-foil-pans', 'pet-cups', 'black-nitrile-gloves', 'trash-liners'],
                    ['new-orleans', 'jackson', 'beaumont']),
    'oklahoma-city': ('Oklahoma City', 'OK', 'Oklahoma County', 440, 'I-45 North and I-35 North, about six and a half hours',
                      ['A steakhouse and barbecue town with Bricktown\'s entertainment district and a growing food hall scene.',
                       'Energy-sector offices and events keep catering steady.'],
                      'Thunder basketball season and the State Fair of Oklahoma (September) are peaks.',
                      ['black-containers', 'round-foil-pans', 'pet-cups', 'paper-bags', 'black-nitrile-gloves'],
                      ['tulsa', 'dallas', 'lubbock']),
    'tulsa': ('Tulsa', 'OK', 'Tulsa County', 490, 'US-59 North and US-69, about seven and a half hours',
              ['Route 66 diners, barbecue and a busy Brady and Blue Dome district.',
               'Aerospace and energy employers run large cafeterias.'],
              'Summer festivals and holiday catering are the peaks.',
              ['black-hinged-containers', 'pet-cups', 'deli-containers', 'trash-liners', 'dinner-napkins'],
              ['oklahoma-city', 'little-rock', 'kansas-city']),
    'little-rock': ('Little Rock', 'AR', 'Pulaski County', 440, 'US-59 / I-69 North and I-30 East, about six and a half hours',
                    ['The Arkansas capital, with Southern comfort food, catfish and barbecue, and the River Market district.',
                     'State government and hospital campuses run steady cafeteria demand.'],
                    'Razorback football weekends and holiday catering are the peaks.',
                    ['school-trays', 'black-containers', 'round-foil-pans', 'dinner-napkins', 'trash-liners'],
                    ['memphis', 'tulsa', 'jackson']),
    'memphis': ('Memphis', 'TN', 'Shelby County', 560, 'I-30 East and I-40 East, about eight and a half hours',
                ['A barbecue capital (dry-rub ribs) and Beale Street nightlife, plus one of the largest freight and distribution hubs in the US.',
                 'Barbecue joints and caterers lean on foil pans, boat trays and deli paper.'],
                'Memphis in May, home to the World Championship Barbecue Cooking Contest, is the peak.',
                ['round-foil-pans', 'deep-steam-table-pans', 'paper-boat-trays', 'checker-deli-paper-wrap', 'black-nitrile-gloves'],
                ['little-rock', 'nashville', 'jackson']),
    'nashville': ('Nashville', 'TN', 'Davidson County', 780, 'I-10 East, I-12, I-59 and I-65 North, about 11 and a half hours',
                  ['Hot chicken, honky-tonks on Broadway and one of the fastest-growing restaurant scenes in the country.',
                   'Tourism and bachelorette weekends keep to-go and bar supplies moving.'],
                  'Summer tourism and CMA Fest (June) are the peaks.',
                  ['black-hinged-containers', 'paper-boat-trays', 'pet-cups', 'beverage-napkins', 'trash-liners'],
                  ['memphis', 'atlanta', 'birmingham']),
    'atlanta': ('Atlanta', 'GA', 'Fulton County', 790, 'I-10 East, I-65 North and I-85 North, about 12 hours',
                ['One of the largest food service markets in the Southeast, with a deep restaurant scene and many national chains based in the metro.',
                 'The world\'s busiest airport and a big convention center drive catering and concessions.'],
                'College football season and major conventions are the peaks.',
                ['black-containers', 'pet-cups', 'disposable-cutlery-kits', 'deli-containers', 'black-nitrile-gloves'],
                ['birmingham', 'nashville', 'charlotte']),
    'birmingham': ('Birmingham', 'AL', 'Jefferson County', 670, 'I-10 East, I-12 and I-59 North, about 10 hours',
                   ['A Southern food city known for barbecue with white sauce and meat-and-three diners.',
                    'Hospital campuses and universities run large cafeteria programs.'],
                   'Football season (fall) is the peak.',
                   ['round-foil-pans', 'school-trays', 'black-containers', 'dinner-napkins', 'trash-liners'],
                   ['atlanta', 'nashville', 'jackson']),
    'jackson': ('Jackson', 'MS', 'Hinds County', 440, 'I-10 East and I-55 North, about six and a half hours',
                ['The Mississippi capital, with soul food, catfish and Southern barbecue.',
                 'State offices, hospitals and schools are steady institutional buyers.'],
                'Back-to-school and holiday catering are the peaks.',
                ['school-trays', 'round-foil-pans', 'dinner-napkins', 'black-containers', 'trash-liners'],
                ['new-orleans', 'memphis', 'baton-rouge']),
    'orlando': ('Orlando', 'FL', 'Orange County', 965, 'I-10 East and I-75 South, about 14 hours',
                ['Theme parks, resorts and one of the largest convention centers in the country make it a hospitality-first market.',
                 'Quick-service restaurants along International Drive move huge volumes of cups and to-go containers.'],
                'Spring break, summer and the winter holidays are all peak tourism seasons.',
                ['pet-cups', 'pet-cup-lids', 'black-containers', 'paper-bags', 'trash-liners'],
                ['tampa', 'jacksonville', 'miami']),
    'tampa': ('Tampa', 'FL', 'Hillsborough County', 1000, 'I-10 East and I-75 South, about 15 hours',
              ['Cuban sandwiches from Ybor City, Gulf seafood and a busy cruise and sports scene.',
               'Beach towns from Clearwater to St. Pete add seasonal restaurant demand.'],
              'Snowbird season (winter) and Gasparilla (January) are the peaks; hurricane season means stocking ahead.',
              ['checker-deli-paper-wrap', 'paper-boat-trays', 'pet-cups', 'black-hinged-containers', 'trash-liners'],
              ['orlando', 'miami', 'jacksonville']),
    'jacksonville': ('Jacksonville', 'FL', 'Duval County', 870, 'I-10 East, about 13 hours',
                     ['The largest city by area in the lower 48, with naval bases, a working port and beach towns.',
                      'Seafood shacks and military dining run on boat trays, foil and liners.'],
                     'Summer beach season and the Florida-Georgia football game (fall) are peaks.',
                     ['paper-boat-trays', 'round-foil-pans', 'black-containers', 'trash-liners', 'black-nitrile-gloves'],
                     ['orlando', 'tampa', 'atlanta']),
    'miami': ('Miami', 'FL', 'Miami-Dade County', 1185, 'I-10 East and I-75 South, about 17 hours',
              ['Cuban and Latin American cooking, cafecito windows and a nightlife and cruise-port economy.',
               'Ventanitas and bakeries go through portion cups, deli paper and bakery tissue.'],
              'Winter season (December to April) and Art Basel (December) are the peaks.',
              ['portion-cups', 'bakery-tissue', 'checker-deli-paper-wrap', 'pet-cups', 'black-containers'],
              ['tampa', 'orlando', 'jacksonville']),
    'charlotte': ('Charlotte', 'NC', 'Mecklenburg County', 1035, 'I-10 East, I-65 and I-85 North, about 15 hours',
                  ['A banking hub with fast-growing suburbs and a big corporate catering market.',
                   'NASCAR heritage and pro sports bring concession demand.'],
                  'Race weeks at Charlotte Motor Speedway (May and October) and football season are peaks.',
                  ['disposable-cutlery-kits', 'black-containers', 'pet-cups', 'paper-boat-trays', 'trash-liners'],
                  ['raleigh', 'atlanta', 'greensboro']),
    'raleigh': ('Raleigh', 'NC', 'Wake County', 1180, 'I-10 East, I-65, I-85 North and I-40, about 17 hours',
                ['The Research Triangle: universities, tech campuses and eastern North Carolina whole-hog barbecue.',
                 'University dining and office catering keep demand steady.'],
                'College basketball and football seasons and graduation are peaks.',
                ['round-foil-pans', 'school-trays', 'black-containers', 'disposable-cutlery-kits', 'dinner-napkins'],
                ['charlotte', 'greensboro', 'atlanta']),
    'greensboro': ('Greensboro', 'NC', 'Guilford County', 1110, 'I-10 East, I-65 and I-85 North, about 16 hours',
                   ['A Piedmont Triad city with Lexington-style barbecue nearby and a large furniture and logistics economy.',
                    'Universities and distribution centers run cafeterias and break rooms.'],
                   'The High Point furniture market (April and October) brings event catering.',
                   ['round-foil-pans', 'black-containers', 'pet-cups', 'trash-liners', 'c-fold-towel'],
                   ['charlotte', 'raleigh', 'atlanta']),
    'phoenix': ('Phoenix', 'AZ', 'Maricopa County', 1175, 'I-10 West across Texas and New Mexico, about 17 hours',
                ['Sonoran-style Mexican food, resorts and spring training baseball in one of the fastest-growing metros.',
                 'Extreme summer heat shifts demand toward cold drinks and delivery packaging.'],
                'Spring training (February to March) and the winter resort season are the peaks.',
                ['pet-cups', 'pet-cup-lids', 'foil-sheets', 'black-hinged-containers', 'paper-bags'],
                ['albuquerque', 'las-vegas', 'el-paso']),
    'albuquerque': ('Albuquerque', 'NM', 'Bernalillo County', 840, 'US-287 and I-40 West, about 13 hours',
                    ['New Mexican cooking built on red and green chile, plus a busy I-40 travel corridor.',
                     'Breakfast burrito shops lean on foil sheets and portion cups.'],
                    'The International Balloon Fiesta (October) is the peak.',
                    ['foil-sheets', 'portion-cups', 'black-hinged-containers', 'pet-cups', 'paper-bags'],
                    ['el-paso', 'phoenix', 'denver']),
    'denver': ('Denver', 'CO', 'Denver County', 1030, 'US-287 and I-25 North, about 15 hours',
               ['A craft brewery and food hall city, plus mountain ski-town restaurants an hour away.',
                'Stadiums and a busy convention center drive concession demand.'],
               'Ski season (winter) and summer festival season are both busy.',
               ['pet-cups', 'paper-boat-trays', 'black-containers', 'trash-liners', 'beverage-napkins'],
               ['albuquerque', 'kansas-city', 'phoenix']),
    'las-vegas': ('Las Vegas', 'NV', 'Clark County', 1465, 'I-10 West and I-40 / US-93, about 21 hours',
                  ['Casino resorts, buffets and one of the largest convention markets in the world.',
                   'Around-the-clock food service burns through gloves, liners and to-go containers.'],
                  'Major conventions (January and spring) and holiday weekends are the peaks.',
                  ['black-nitrile-gloves', 'black-containers', 'pet-cups', 'trash-liners', 'disposable-cutlery-kits'],
                  ['phoenix', 'denver', 'albuquerque']),
    'kansas-city': ('Kansas City', 'MO', 'Jackson County', 745, 'I-45 North and I-35 North, about 11 hours',
                    ['Kansas City barbecue, burnt ends and a huge competition barbecue circuit.',
                     'A central freight hub with large food distribution warehouses.'],
                    'The American Royal World Series of Barbecue (fall) and football season are peaks.',
                    ['round-foil-pans', 'deep-steam-table-pans', 'checker-deli-paper-wrap', 'paper-boat-trays', 'black-nitrile-gloves'],
                    ['st-louis', 'tulsa', 'oklahoma-city']),
    'st-louis': ('St. Louis', 'MO', 'St. Louis City', 820, 'I-30 East and I-55 North, about 12 hours',
                 ['Toasted ravioli, St. Louis-style pizza and barbecue, with a big brewery and ballpark culture.',
                  'Universities and hospitals are major institutional buyers.'],
                 'Baseball season (spring to fall) is the peak.',
                 ['round-foil-pans', 'pet-cups', 'paper-boat-trays', 'black-containers', 'trash-liners'],
                 ['kansas-city', 'memphis', 'chicago']),
    'chicago': ('Chicago', 'IL', 'Cook County', 1085, 'I-45 North, I-30, I-40 and I-55 North, about 16 hours',
                ['One of the largest restaurant markets in the country: deep dish, Italian beef, hot dogs and a dense neighborhood dining scene.',
                 'A national rail and trucking hub, so pallet freight arrives on regular lanes.'],
                'Summer festival season (Taste of Chicago, street fests) and the holiday season are the peaks.',
                ['black-containers', 'deli-containers', 'paper-bags', 'checker-deli-paper-wrap', 'black-nitrile-gloves'],
                ['st-louis', 'kansas-city', 'nashville']),
}


# ------------------------------------------------------------------------------------------------
# P1 (Nov 2026 audit): only the strongest location pages stay in Google, each with its own copy.
# Every other city page is noindex,follow and left out of the sitemap until it gets unique copy.
INDEXED_CITIES = ['houston', 'dallas', 'fort-worth', 'austin', 'san-antonio', 'new-orleans', 'atlanta']
FOOTER_CITIES = list(INDEXED_CITIES)   # the biggest markets, linked from every page's footer

LOCAL = {
    'houston': [
        'Our warehouse sits at 7350 Langfield Rd (77092), inside Beltway 8 just off US-290 in northwest Houston. Houston restaurants, '
        'taquerias, caterers and food trucks can pick up the same day they order, or we deliver across Harris, Fort Bend and Montgomery '
        'counties, typically the next business day.',
        'Because there is no freight leg, Houston buyers can order tighter: a few cases of gloves and to-go containers this week, a pallet of '
        'cups next week. Pick-up orders are staged at the dock, so send your list ahead and drive in when it is ready.',
        'Distributors based in Houston use us as a second warehouse. Mixed pallets go out on your truck or ours, and the same spec sheets '
        'you see on the product pages (case pack, Ti × Hi, cases per pallet) come with every quote.',
    ],
    'dallas': [
        'Dallas orders ride I-45 North, about 240 miles from our Houston dock, so a pallet that leaves on Monday is usually at a Dallas '
        'County receiving door on Tuesday. That makes Houston a practical second source for Dallas distributors when a national supplier '
        'runs short.',
        'Restaurants in Deep Ellum, Bishop Arts and Uptown, and the many restaurant groups headquartered in the metro, tend to order mixed '
        'pallets: black-base to-go containers, PET cups and deli containers on one load. Plan State Fair concessions (late September to '
        'October) two weeks out; that is when cups, gloves and paper bags are tightest across North Texas.',
    ],
    'fort-worth': [
        'Fort Worth is about 265 miles from our warehouse by I-45 North and I-20 West. Most Tarrant County deliveries arrive the business '
        'day after the order ships, and many Fort Worth accounts share a truck with Dallas and Arlington stops.',
        'Stockyards steakhouses, barbecue joints and the food halls downtown and on Magnolia Avenue run through foil pans, red plaid boat '
        'trays and gloves. Rodeo caterers usually book a full pallet of round foil pans and plates ahead of the Fort Worth Stock Show '
        '(January to February) so they are not chasing stock mid-run.',
    ],
    'austin': [
        'Austin is the shortest out-of-town run we make: about 165 miles west on US-290, usually next-day delivery to Travis County. '
        'Food-trailer parks in East Austin and on South Congress buy small and often, so mixed orders by the case suit them better than '
        'full pallets of one item.',
        'The products that move here are hinged containers (black and PFAS-free bagasse), PET cups for coffee and tea, checkered deli paper '
        'for barbecue, and portion cups for salsa and queso. For SXSW in March and Austin City Limits in October, order two weeks ahead.',
    ],
    'san-antonio': [
        'San Antonio is about 200 miles west on I-10, so Bexar County deliveries typically land the business day after the order ships. '
        'Taquerias, tortilla makers and Tex-Mex kitchens are the core of our San Antonio orders: pop-up foil sheets for tacos and '
        'breakfast burritos, checkered deli paper, portion cups and interfold napkins.',
        'Large kitchens that serve the military bases and River Walk hotels order by the pallet. Fiesta in April is the busiest stretch; '
        'restaurants that stock a pallet of foil sheets and portion cups in March avoid rush freight.',
    ],
    'new-orleans': [
        'New Orleans is 350 miles east of our warehouse on I-10. LTL freight usually reaches Orleans and Jefferson parishes in one to two '
        'business days, and Baton Rouge stops share the same route.',
        'Crawfish boils, po-boy shops and caterers drive demand for round foil pans, red plaid boat trays and checkered deli paper, and the '
        'convention and festival calendar adds PET cups and trash liners in volume. Most New Orleans buyers book a pallet ahead of Mardi '
        'Gras (January to February) and another before Jazz Fest in late April.',
    ],
    'atlanta': [
        'Atlanta is our longest regular lane in the Southeast: about 790 miles on I-10, I-65 and I-85, typically two to three business '
        'days by LTL freight from Houston. Because of the transit, Atlanta accounts usually order full or mixed pallets and keep two to '
        'three weeks of their fastest movers on hand.',
        'Restaurant groups, airport concessions and convention caterers in Fulton County order black-base to-go containers, PET cups, '
        'cutlery kits and deli containers. A 6- or 12-pallet order moves into a lower price tier, which offsets most of the extra freight.',
    ],
}

# Unique local copy for the rest of the city pages (Nov 2026): routes, transit and counties from the data
# above; the ordering notes are written for each market so no two pages read alike.
LOCAL.update({
    'katy': [
        'Katy is about 30 miles west of our Langfield Rd warehouse on I-10, so deliveries across the Harris, Fort Bend and Waller county parts of '
        'Katy usually land the next business day. Many Katy restaurants skip freight entirely and pick up on their way into Houston.',
        'Katy Asian Town and the family restaurants along the Grand Parkway and I-10 order PET cups for boba and tea, hinged containers and portion '
        'cups. Schools and youth sports programs in the Katy area buy school trays and dinner napkins in volume before back-to-school in August.',
    ],
    'sugar-land': [
        'Sugar Land sits 20 miles southwest of our warehouse on US-59 / I-69, about half an hour away, and Fort Bend County orders typically '
        'arrive the next business day. Houston pick-up is just as easy for Sugar Land buyers who pass through the city.',
        'The South Asian, Chinese, Vietnamese and Nigerian kitchens along the US-59 corridor run on deli containers, black-base to-go containers '
        'and portion cups for sauces and chutneys. Caterers who cover weddings and Town Square festival weekends add cutlery kits and interfold '
        'napkins to the same order.',
    ],
    'the-woodlands': [
        'The Woodlands is 30 miles north of our warehouse on I-45, roughly 40 minutes, and Montgomery County deliveries are usually next-day. '
        'Restaurants on Market Street, the Waterway and Hughes Landing often combine a delivery with neighboring Conroe or Spring stops.',
        'Coffee shops and fast-casual concepts here order PET cups and matching 98mm lids, black-base containers and beverage napkins. Concert '
        'season at the Cynthia Woods Mitchell Pavilion (spring to fall) is when cups and cutlery kits move fastest.',
    ],
    'pasadena': [
        'Pasadena is 15 miles east of our warehouse on TX-225, one of the shortest delivery runs we make, typically next business day. Plants '
        'along the Houston Ship Channel and the Port of Houston corridor are a big part of the local demand.',
        'Plant cafeterias and crew caterers order blue nitrile gloves, hinged containers, food film, C-fold towels and heavy trash liners. During '
        'plant turnarounds, usually spring and fall, crew meal counts jump overnight; a mixed pallet staged a week ahead keeps the line running.',
    ],
    'pearland': [
        'Pearland is about 18 miles south of our warehouse via TX-288, around 25 minutes, so Brazoria County orders usually arrive the next '
        'business day or can be picked up in Houston the same day.',
        'New restaurant pads along Broadway and Shadow Creek Ranch keep opening, and new openings tend to standardize on one container and cup '
        'program from day one. Pearland caterers and church kitchens buy round plates, dinner napkins, deli containers and trash liners by the case.',
    ],
    'baytown': [
        'Baytown is 30 miles east on I-10, about 35 minutes from our warehouse, covering the Harris and Chambers county sides of the city with '
        'next-day delivery. Refinery and petrochemical sites set the rhythm of local orders.',
        'Industrial cafeterias and contractors order black nitrile gloves, hinged meal containers, kitchen roll towels, stretch film and trash '
        'liners. Turnaround seasons and summer boating traffic on Trinity Bay both lift volumes, so Baytown buyers often keep a reserve pallet.',
    ],
    'conroe': [
        'Conroe, the Montgomery County seat, is about 40 miles north on I-45, under an hour from our dock, with next-business-day delivery. '
        'Lake Conroe marinas and the historic downtown restaurant district are the two main buyer groups.',
        'Summer lake season (May to September) is when PET cups, beverage napkins, paper bags and trash liners move fastest; restaurants along '
        'the I-45 growth corridor add black-base to-go containers. Ordering before Memorial Day avoids the summer rush.',
    ],
    'league-city': [
        'League City is 28 miles south of our warehouse on I-45, about 35 minutes, and Galveston County deliveries are typically next-day. '
        'Kemah Boardwalk, Clear Lake marinas and NASA-area offices are all within the same delivery loop.',
        'Seafood restaurants here use round foil pans, red plaid boat trays, checkered deli paper and food film. Summer boardwalk season is the '
        'peak, and during hurricane season (June to November) many kitchens keep an extra week of disposables on hand.',
    ],
    'galveston': [
        'Galveston is about 50 miles from our warehouse, I-45 South to the causeway, roughly an hour, with next-business-day delivery to the '
        'island. Seawall Boulevard, The Strand and the cruise terminal set the pace.',
        'Beach-season seafood shacks and snack stands go through boat trays, checkered deli paper, portion cups for cocktail and tartar sauce, '
        'PET cups and trash liners. Mardi Gras Galveston in February and the summer beach season are the peaks; storm season means stocking ahead.',
    ],
    'beaumont': [
        'Beaumont is 85 miles east of our warehouse on I-10, about an hour and a half, and Jefferson County orders usually arrive in one '
        'business day. Port Arthur and Orange in the Golden Triangle share the same route.',
        'Cajun and Creole kitchens use round foil pans, deep steam table pans and red plaid boat trays, especially in crawfish season each spring. '
        'Refinery turnarounds add crew catering, black nitrile gloves and trash liners on short notice.',
    ],
    'college-station': [
        'College Station is about 95 miles from our warehouse via US-290 and TX-6, roughly an hour and 45 minutes, and Brazos County orders '
        'typically arrive in one business day.',
        'Texas A&M game weekends can double a restaurant\'s volume overnight. Northgate bars and tailgate caterers order PET cups, boat trays, '
        'round plates, cutlery kits and trash liners. Book football-season stock in August, and again before graduation weekends.',
    ],
    'arlington': [
        'Arlington is about 255 miles north via I-45 and I-20, roughly four hours, and Tarrant County deliveries usually arrive one business day '
        'after the order ships, often on the same truck as Dallas and Fort Worth stops.',
        'The entertainment district around AT&T Stadium, Globe Life Field and Six Flags runs on concessions: PET cups and lids, red plaid boat '
        'trays, beverage napkins and trash liners. Football, baseball and summer park seasons overlap, so most Arlington buyers order year-round.',
    ],
    'plano': [
        'Plano is about 260 miles north of Houston via I-45 and US-75, about four hours, and Collin County orders typically arrive in one '
        'business day.',
        'Corporate campuses around Legacy West drive office catering: cutlery kits, black-base containers, deli containers, interfold napkins and '
        'PET cups. Holiday catering season and the Plano Balloon Festival in September are the busiest times to plan for.',
    ],
    'el-paso': [
        'El Paso is our longest run inside Texas: about 745 miles west on I-10, typically two to three business days by LTL freight. Because of the '
        'distance, El Paso accounts usually order full or mixed pallets on a set schedule.',
        'Mexican restaurants and burrito shops order pop-up foil sheets, hinged containers, portion cups for salsa and paper bags; Fort Bliss '
        'contractors and caterers add black nitrile gloves. Order ahead of the summer heat and the holiday season.',
    ],
    'corpus-christi': [
        'Corpus Christi is about 210 miles southwest via US-59 / I-69 and US-77, three and a half hours, and Nueces County deliveries usually '
        'arrive in one business day.',
        'Gulf seafood restaurants and North Padre Island beach traffic drive orders for boat trays, round foil pans, checkered deli paper, PET cups '
        'and trash liners. Spring break and summer are the peaks; during hurricane season kitchens keep an extra pallet on hand.',
    ],
    'mcallen': [
        'McAllen, in Hidalgo County, is about 350 miles from Houston via US-59 / I-69 and US-77, roughly five and a half hours, with one to two '
        'business days in transit.',
        'Rio Grande Valley kitchens use pop-up foil sheets for tacos and breakfast burritos, black-base to-go containers, portion cups for salsa and '
        'dinner napkins. Winter Texan season (November to March) is the peak, so most McAllen buyers stock up in October.',
    ],
    'laredo': [
        'Laredo is about 315 miles southwest via US-59 / I-69W, roughly five hours, and Webb County orders take one to two business days.',
        'As the busiest inland port in the U.S., Laredo has as many warehouse and trucking buyers as restaurants: stretch film, black nitrile '
        'gloves and paper bags go out alongside hinged containers and foil sheets. February\'s Washington\'s Birthday Celebration is the local peak.',
    ],
    'lubbock': [
        'Lubbock is about 520 miles northwest via US-290 and US-84, roughly eight hours, with one to two business days of transit to Lubbock '
        'County.',
        'Texas Tech game days and the South Plains harvest season shape demand. Restaurants and caterers order PET cups, boat trays, round plates, '
        'trash liners and black nitrile gloves; a mixed pallet before football season covers most of the fall.',
    ],
    'waco': [
        'Waco is about 185 miles northwest of our warehouse via TX-6, roughly three hours, and McLennan County deliveries usually arrive in one '
        'business day.',
        'Baylor game days and visitors to Magnolia Market keep downtown restaurants busy. They order PET cups, black-base containers, paper bags, '
        'cutlery kits and trash liners; spring tourism season is the time to stock up.',
    ],
    'baton-rouge': [
        'Baton Rouge is about 270 miles east on I-10, roughly four hours, and East Baton Rouge Parish orders usually arrive in one business day, '
        'often on the same run as New Orleans deliveries.',
        'LSU tailgates and plant turnarounds are the two big swings. Caterers order red plaid boat trays, round foil pans, PET cups, black nitrile '
        'gloves and trash liners; booking football-season stock in August keeps game weekends covered.',
    ],
    'oklahoma-city': [
        'Oklahoma City is about 440 miles north via I-45 and I-35, roughly six and a half hours, with one to two business days of transit to '
        'Oklahoma County.',
        'Steakhouses, barbecue joints and the Bricktown entertainment district order black-base to-go containers, round foil pans, PET cups and '
        'paper bags, plus black nitrile gloves for the line. Thunder season and the State Fair of Oklahoma in September are the peaks.',
    ],
    'tulsa': [
        'Tulsa is about 490 miles north via US-59 and US-69, roughly seven and a half hours, and Tulsa County orders take one to two business '
        'days.',
        'Route 66 diners, barbecue and the Brady and Blue Dome districts buy hinged containers, PET cups, deli containers, dinner napkins and '
        'trash liners. Summer festivals and holiday catering are the busy stretches.',
    ],
    'little-rock': [
        'Little Rock is about 440 miles northeast via US-59 / I-69 and I-30, roughly six and a half hours, with one to two business days of '
        'transit to Pulaski County.',
        'Catfish and barbecue restaurants, River Market caterers and school cafeterias order black-base containers, round foil pans, dinner '
        'napkins, school trays and trash liners. Razorback football weekends and holiday catering are the peaks.',
    ],
    'memphis': [
        'Memphis is about 560 miles from Houston via I-30 and I-40, roughly eight and a half hours, typically two to three business days by LTL '
        'freight to Shelby County.',
        'Barbecue is the core of Memphis demand: round foil pans, deep steam table pans, red plaid boat trays, checkered deli paper and black '
        'nitrile gloves. Memphis in May, home of the World Championship Barbecue Cooking Contest, is the month to have a full pallet staged.',
    ],
    'nashville': [
        'Nashville is about 780 miles northeast via I-10, I-12, I-59 and I-65, roughly 11 and a half hours, with two to three business days of '
        'transit to Davidson County.',
        'Hot chicken spots and Broadway honky-tonks order hinged containers, boat trays, PET cups, beverage napkins and trash liners. Summer '
        'tourism and CMA Fest in June are the peaks; because of the transit, most Nashville accounts keep two to three weeks of stock.',
    ],
    'birmingham': [
        'Birmingham is about 670 miles east via I-10, I-12 and I-59, roughly 10 hours, typically two to three business days to Jefferson County.',
        'Barbecue with white sauce and meat-and-three diners drive orders for round foil pans, black-base containers and dinner napkins; schools '
        'and church kitchens add school trays and trash liners. Fall football season is the peak.',
    ],
    'jackson': [
        'Jackson is about 440 miles east via I-10 and I-55, roughly six and a half hours, with one to two business days of transit to Hinds County.',
        'Soul food, catfish and barbecue restaurants order round foil pans, black-base containers and dinner napkins; school and institutional '
        'kitchens buy school trays and trash liners. Back-to-school and holiday catering are the busy seasons.',
    ],
    'orlando': [
        'Orlando is about 965 miles from Houston via I-10 and I-75, roughly 14 hours, typically three to four business days by LTL freight to '
        'Orange County. Orlando accounts almost always order full or mixed pallets.',
        'Theme-park-area restaurants, resorts and convention caterers order PET cups and lids, black-base containers, paper bags and trash '
        'liners. Spring break, summer and the winter holidays are all peak seasons, so plan orders two to three weeks out.',
    ],
    'tampa': [
        'Tampa is about 1,000 miles east via I-10 and I-75, roughly 15 hours, with three to four business days of transit to Hillsborough County.',
        'Ybor City sandwich shops wrap Cubans in checkered deli paper; seafood restaurants add boat trays and hinged containers, and stadium and '
        'cruise-season catering adds PET cups and trash liners. Snowbird season and Gasparilla in January are the peaks.',
    ],
    'jacksonville': [
        'Jacksonville is about 870 miles east on I-10, roughly 13 hours, typically two to three business days to Duval County.',
        'Seafood restaurants, naval-base contractors and beach-town kitchens order boat trays, round foil pans, black-base containers, trash liners '
        'and black nitrile gloves. Summer beach season and the Florida-Georgia game in the fall are the peaks.',
    ],
    'miami': [
        'Miami is our longest Southeast lane: about 1,185 miles via I-10 and I-75, roughly 17 hours, three to four business days by LTL freight to '
        'Miami-Dade County.',
        'Cafecito windows and Cuban and Latin American bakeries order portion cups, bakery tissue, checkered deli paper and PET cups; nightlife and '
        'cruise-port kitchens add black-base containers. Winter season (December to April) and Art Basel in December are the peaks.',
    ],
    'charlotte': [
        'Charlotte is about 1,035 miles northeast via I-10, I-65 and I-85, roughly 15 hours, with three to four business days of transit to '
        'Mecklenburg County.',
        'Banking-district office catering runs on cutlery kits, black-base containers and PET cups; race weeks at Charlotte Motor Speedway in May '
        'and October add boat trays and trash liners. Most Charlotte accounts order full pallets on a schedule.',
    ],
    'raleigh': [
        'Raleigh is about 1,180 miles from Houston via I-10, I-65, I-85 and I-40, roughly 17 hours, typically three to four business days to Wake '
        'County.',
        'University dining, tech-campus catering and eastern North Carolina whole-hog barbecue drive orders for round foil pans, school trays, '
        'black-base containers, cutlery kits and dinner napkins. College sports seasons and graduation are the peaks.',
    ],
    'greensboro': [
        'Greensboro is about 1,110 miles northeast via I-10, I-65 and I-85, roughly 16 hours, with three to four business days of transit to '
        'Guilford County.',
        'Lexington-style barbecue nearby and the logistics and furniture economy shape demand: round foil pans, black-base containers, PET cups, '
        'trash liners and C-fold towels. The High Point furniture market in April and October brings event catering.',
    ],
    'phoenix': [
        'Phoenix is about 1,175 miles west on I-10 across Texas and New Mexico, roughly 17 hours, typically three to four business days to '
        'Maricopa County.',
        'Sonoran-style Mexican restaurants use pop-up foil sheets and hinged containers; resorts and spring-training concessions add PET cups and '
        'lids and paper bags. Spring training (February to March) and the winter resort season are the peaks.',
    ],
    'albuquerque': [
        'Albuquerque is about 840 miles northwest via US-287 and I-40, roughly 13 hours, with two to three business days of transit to '
        'Bernalillo County.',
        'New Mexican kitchens built on red and green chile order pop-up foil sheets, portion cups, hinged containers and paper bags; I-40 travel '
        'stops add PET cups. The International Balloon Fiesta in October is the single biggest week of the year.',
    ],
    'denver': [
        'Denver is about 1,030 miles from Houston via US-287 and I-25, roughly 15 hours, typically three to four business days to Denver County.',
        'Food halls, craft breweries and mountain ski-town restaurants order PET cups, boat trays, black-base containers, beverage napkins and '
        'trash liners. Ski season in winter and the summer festival season are both busy, so Denver buyers order on a steady schedule.',
    ],
    'las-vegas': [
        'Las Vegas is our longest regular lane: about 1,465 miles via I-10 and I-40 / US-93, roughly 21 hours, four to five business days by LTL '
        'freight to Clark County. Las Vegas accounts order full pallets and plan a month ahead.',
        'Casino resorts, buffets and convention caterers go through black nitrile gloves, black-base containers, PET cups, cutlery kits and trash '
        'liners in volume. Major conventions in January and spring are the peaks.',
    ],
    'kansas-city': [
        'Kansas City is about 745 miles north via I-45 and I-35, roughly 11 hours, with two to three business days of transit to Jackson County.',
        'Kansas City barbecue and the competition circuit run on round foil pans, deep steam table pans, checkered deli paper, boat trays and black '
        'nitrile gloves. The American Royal World Series of Barbecue in the fall and football season are the peaks.',
    ],
    'st-louis': [
        'St. Louis is about 820 miles northeast via I-30 and I-55, roughly 12 hours, typically two to three business days to St. Louis City.',
        'Barbecue, pizza and ballpark concessions order round foil pans, PET cups, boat trays, black-base containers and trash liners. Baseball '
        'season, spring through fall, is the long peak.',
    ],
    'chicago': [
        'Chicago is about 1,085 miles from Houston via I-45, I-30, I-40 and I-55, roughly 16 hours, with three to four business days of transit '
        'to Cook County. Chicago accounts usually order mixed pallets on a fixed schedule.',
        'Italian beef and hot dog stands wrap in checkered deli paper; neighborhood restaurants order black-base containers, deli containers and '
        'paper bags, plus black nitrile gloves. Summer festival season and the holidays are the peaks.',
    ],
})
INDEXED_CITIES = sorted(set(INDEXED_CITIES) | set(LOCAL))
