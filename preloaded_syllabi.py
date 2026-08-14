"""
preloaded_syllabi.py — Comprehensive CBSE and ICSE syllabus datastore for Classes 1 to 10.

Automatically populates subjects, chapters, and topics for students so they don't
have to type anything manually — all they need to do is tick off topics as they study.
"""

from models import add_subject, add_chapter, add_topic, get_subject_by_name, get_chapters_for_subject, bulk_create_syllabus

# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE SYLLABUS DATASTORE FOR CBSE AND ICSE (CLASSES 1 TO 10)
# ══════════════════════════════════════════════════════════════════════════════

SYLLABUS_DATA = {
    # ──────────────────────────────────────────────────────────────────────────
    # ICSE SYLLABUS DATA (CLASSES 1 TO 10)
    # ──────────────────────────────────────────────────────────────────────────
    ("ICSE", "Class 1"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Pre-Number Concepts & Numbers 1-100", "topics": ["Big/Small & Tall/Short", "Top/Bottom & Above/Below", "Counting & Number Names 1-100", "Place Value (Tens and Ones)", "Before, After and Between"]},
                {"name": "Chapter 2: Addition & Subtraction", "topics": ["Single Digit Addition", "Single Digit Subtraction", "Addition on Number Line", "Word Problems on Addition & Subtraction"]},
                {"name": "Chapter 3: Shapes, Patterns & Measurement", "topics": ["Basic 2D Shapes (Circle, Square, Triangle, Rectangle)", "Repeating Patterns", "Measuring Length & Weight (Non-standard units)"]},
                {"name": "Chapter 4: Money & Time", "topics": ["Indian Coins and Currency Notes", "Reading Clock (O'Clock)", "Days of the Week & Months of the Year"]}
            ]
        },
        {
            "name": "General Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Living and Non-Living Things", "topics": ["Features of Living Things", "Natural vs Man-made Things", "Plants & Animals Around Us"]},
                {"name": "Chapter 2: My Body & Healthy Habits", "topics": ["Parts of My Body", "Sense Organs & Their Uses", "Cleanliness & Good Habits", "Safe Habits at Home and School"]},
                {"name": "Chapter 3: Plant & Animal Life", "topics": ["Types of Plants (Trees, Shrubs, Herbs)", "Domestic and Wild Animals", "Animals Homes and Food"]},
                {"name": "Chapter 4: Air, Water and Weather", "topics": ["Importance of Clean Air", "Uses and Conservation of Water", "Sun, Moon and Stars", "Different Seasons"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Phonics & Naming Words", "topics": ["Vowels and Consonants", "Naming Words (Nouns)", "Singular and Plural (One and Many)", "Use of A and An"]},
                {"name": "Unit 2: Pronouns & Action Words", "topics": ["Pronouns (He, She, It, They)", "Doing Words (Verbs)", "Describing Words (Adjectives)", "Simple Sentence Construction", "Picture Comprehension"]}
            ]
        }
    ],

    ("ICSE", "Class 2"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: 3-Digit Numbers & Place Value", "topics": ["Numbers up to 999", "Place Value and Face Value", "Expanded Form", "Comparing and Ordering Numbers", "Even and Odd Numbers"]},
                {"name": "Chapter 2: Addition & Subtraction (2 & 3 Digits)", "topics": ["Addition with Regrouping (Carrying)", "Subtraction with Borrowing", "Checking Subtraction with Addition", "Word Problems"]},
                {"name": "Chapter 3: Multiplication & Division Basics", "topics": ["Multiplication as Repeated Addition", "Multiplication Tables (1 to 10)", "Multiplication of 2-digit numbers", "Division as Equal Sharing"]},
                {"name": "Chapter 4: Geometry, Measurement & Data", "topics": ["Straight and Curved Lines", "Solid Shapes (Cube, Cuboid, Sphere, Cone, Cylinder)", "Measurement of Length (m, cm), Mass (kg, g), Capacity (l, ml)", "Reading Pictographs"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Plant Kingdom", "topics": ["Types of Plants (Climbers, Creepers)", "Parts of a Plant", "Uses of Plants (Food, Fibres, Medicine)", "Care of Plants"]},
                {"name": "Chapter 2: Animal Kingdom", "topics": ["Wild Animals & Pet Animals", "Food Habits of Animals (Herbivores, Carnivores, Omnivores)", "Animal Shelters & Young Ones"]},
                {"name": "Chapter 3: Human Body & Health", "topics": ["Internal and External Organs", "Bones and Muscles", "Healthy Food Habits & Posture", "Safety Rules & First Aid Basics"]},
                {"name": "Chapter 4: Natural Phenomena", "topics": ["Air has Weight & Occupies Space", "Forms of Water (Ice, Water, Vapour)", "Water Cycle Basic Concept", "Rocks and Minerals"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Grammar & Vocabulary", "topics": ["Common & Proper Nouns", "Use of This/That/These/Those", "Articles (A, An, The)", "Prepositions (In, On, Under, Behind)", "Conjunctions (and, but)"]},
                {"name": "Unit 2: Creative Writing & Reading", "topics": ["Short Story Reading Comprehension", "Paragraph Writing on My Family / Pet", "Punctuation (Capital letters, Full stop, Question mark)"]}
            ]
        }
    ],

    ("ICSE", "Class 3"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: 4-Digit Numbers", "topics": ["Numbers up to 9,999", "Place Value & Face Value", "Successor and Predecessor", "Roman Numerals (I to XX)", "Rounding Off to Nearest 10"]},
                {"name": "Chapter 2: Operations on Numbers", "topics": ["Addition of 4-Digit Numbers", "Subtraction of 4-Digit Numbers", "Multiplication by 1-Digit and 2-Digit Numbers", "Division by 1-Digit Numbers (Quotient & Remainder)"]},
                {"name": "Chapter 3: Fractions", "topics": ["Concept of Fraction as Part of Whole", "Numerator and Denominator", "Like and Unlike Fractions", "Addition and Subtraction of Like Fractions"]},
                {"name": "Chapter 4: Geometry & Measurement", "topics": ["Line, Line Segment & Ray", "Perimeter of Simple Shapes", "Conversion of Length, Mass & Capacity", "Time (Quarter past, Half past, Quarter to)", "Money Operations & Making Bills"]}
            ]
        },
        {
            "name": "General Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Plants & Food Production", "topics": ["Parts of a Plant and Their Functions", "Leaves: The Food Factory (Photosynthesis)", "Modifications of Root, Stem, Leaf"]},
                {"name": "Chapter 2: Animals: Feeding & Birds", "topics": ["Feeding Habits & Mouthparts of Animals", "Food Chain", "Beaks, Claws and Feathers of Birds", "Nests and Flight Mechanism"]},
                {"name": "Chapter 3: Human Organ Systems", "topics": ["Digestive System Overview", "Respiratory System Overview", "Circulatory & Nervous System Introduction", "Sense Organs & Hygiene"]},
                {"name": "Chapter 4: Matter & Materials", "topics": ["Solids, Liquids and Gases", "Changes in States of Matter", "Soil: Formation, Types & Conservation", "Light, Sound and Force"]}
            ]
        },
        {
            "name": "Social Studies", "color": "#F59E0B",
            "chapters": [
                {"name": "Chapter 1: Earth and Solar System", "topics": ["The Solar System & Planets", "The Unique Planet: Earth", "Continents and Oceans", "Globes and Maps"]},
                {"name": "Chapter 2: India: Our Country", "topics": ["Physical Features of India", "States and Union Territories", "Our Capital: New Delhi", "Major Metropolitan Cities (Mumbai, Kolkata, Chennai)"]},
                {"name": "Chapter 3: Community & Governance", "topics": ["Our National Symbols", "Occupations of People", "Means of Transport & Communication", "Local Civic Bodies (Gram Panchayat, Municipality)"]}
            ]
        }
    ],

    ("ICSE", "Class 4"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Large Numbers & Roman Numerals", "topics": ["5-Digit & 6-Digit Numbers (Indian & International System)", "Place Value Chart & Periods", "Roman Numerals up to C (100)", "Estimation and Rounding Off"]},
                {"name": "Chapter 2: Arithmetic Operations", "topics": ["Addition & Subtraction of Large Numbers", "Multiplication by 2 & 3-Digit Numbers", "Long Division with 2-Digit Divisors", "Unitary Method Basics", "BODMAS / Order of Operations"]},
                {"name": "Chapter 3: Factors, Multiples & Fractions", "topics": ["Factors and Multiples", "Prime and Composite Numbers", "Tests of Divisibility (2, 3, 5, 9, 10)", "HCF and LCM", "Types of Fractions (Proper, Improper, Mixed, Equivalent)", "Decimals Introduction"]},
                {"name": "Chapter 4: Geometry & Mensuration", "topics": ["Angles and Types of Angles", "Triangles and Quadrilaterals", "Circles: Radius, Diameter, Chord, Circumference", "Perimeter and Area of Square & Rectangle", "Volume Concept"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Plant Adaptation & Reproduction", "topics": ["Terrestrial & Aquatic Plants", "Insectivorous & Non-green Plants", "Reproduction in Plants (Seeds, Spores, Vegetative)"]},
                {"name": "Chapter 2: Animal Habitats & Life Cycles", "topics": ["Adaptations in Terrestrial, Aquatic, Amphibians & Aerial Animals", "Life Cycle of Butterfly, Frog, Cockroach", "Care and Protection of Animals"]},
                {"name": "Chapter 3: Food, Digestion & Teeth", "topics": ["Nutrients & Balanced Diet", "Human Teeth (Structure & Types: Incisors, Canines, Premolars, Molars)", "Digestive System & Digestive Juices", "Food Preservation Methods"]},
                {"name": "Chapter 4: Matter, Energy & Environment", "topics": ["Arrangement of Molecules in Matter", "Solute, Solvent & Solution", "Forces (Gravitational, Frictional, Magnetic)", "Simple Machines (Lever, Pulley, Inclined plane)", "Pollution (Air, Water, Land, Noise) & Conservation"]}
            ]
        },
        {
            "name": "Social Studies", "color": "#F59E0B",
            "chapters": [
                {"name": "Chapter 1: Physical Divisions of India", "topics": ["The Northern Mountains (Himalayas)", "The Northern Fertile Plains", "The Great Indian Desert (Thar)", "The Southern Peninsular Plateau", "The Coastal Plains & Islands"]},
                {"name": "Chapter 2: Climate, Natural Resources & Agriculture", "topics": ["Seasons of India", "Soils and Forests of India", "Water Resources and Multi-purpose River Valley Projects", "Mineral Wealth & Industries", "Agriculture and Livestock"]},
                {"name": "Chapter 3: History & Heritage of India", "topics": ["Indus Valley Civilization Overview", "Emperor Ashoka and the Mauryan Empire", "Our Rich Culture: Monuments, Festivals, Dances", "Our Rights and Duties as Citizens"]}
            ]
        }
    ],

    ("ICSE", "Class 5"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Numbers, Operations & Roman Numerals", "topics": ["7 & 8-Digit Numbers (Lakhs, Crores, Millions)", "Indian vs International Place Value System", "Roman Numerals up to M (1000)", "Four Fundamental Operations on Large Numbers"]},
                {"name": "Chapter 2: Number Theory, Fractions & Decimals", "topics": ["Divisibility Rules (2 to 11)", "Prime Factorization (Factor Tree & Division Method)", "HCF and LCM by Division Method", "Operations on Fractions (+, -, ×, ÷)", "Decimal Operations and Conversion", "Percentage Concept"]},
                {"name": "Chapter 3: Commercial Mathematics", "topics": ["Unitary Method & Direct Variation", "Profit and Loss Basics", "Simple Interest (P, R, T Formula)", "Average Calculations", "Speed, Distance and Time"]},
                {"name": "Chapter 4: Geometry, Perimeter, Area & Volume", "topics": ["Lines, Angles & Measuring with Protractor", "Parallel and Perpendicular Lines", "Triangles Classification & Angle Sum Property", "Perimeter and Area of Composite Shapes", "Volume of Cube and Cuboid"]}
            ]
        },
        {
            "name": "General Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Plant Reproduction & Agriculture", "topics": ["Structure of a Seed & Germination", "Seed Dispersal by Wind, Water, Animals & Explosion", "Vegetative Propagation", "Crops: Kharif & Rabi, Agricultural Steps"]},
                {"name": "Chapter 2: Animal World & Human Skeletal System", "topics": ["Breathing and Movement in Animals", "Human Skeletal System (Skull, Spine, Ribcage, Limbs)", "Joints: Ball & Socket, Hinge, Pivot, Gliding", "Muscular System & Reflex Actions"]},
                {"name": "Chapter 3: Nervous System, Diseases & First Aid", "topics": ["Brain (Cerebrum, Cerebellum, Medulla), Spinal Cord & Nerves", "Sense Organs Structure & Care", "Communicable vs Non-Communicable Diseases", "Vaccination, Hygiene & First Aid"]},
                {"name": "Chapter 4: Physical Sciences & Environment", "topics": ["States of Matter & Molecular Theory", "Air Composition & Atmospheric Pressure", "Water Purification & Distillation", "Simple Machines", "Space Exploration & Moon"]}
            ]
        },
        {
            "name": "Social Studies", "color": "#F59E0B",
            "chapters": [
                {"name": "Chapter 1: Globe, Maps & Climatic Zones", "topics": ["Latitudes (Equator, Tropics, Arctic/Antarctic) & Longitudes (Prime Meridian)", "Grid System & Time Zones", "Major Climate Zones (Torrid, Temperate, Frigid)", "Equatorial Region (DR Congo), Deserts (Saudi Arabia), Polar Region (Greenland)"]},
                {"name": "Chapter 2: The Freedom Struggle of India", "topics": ["Arrival of Europeans & East India Company", "The Revolt of 1857", "Rise of Indian National Congress", "Role of Mahatma Gandhi, Subhas Chandra Bose, Bhagat Singh", "Independence and Partition"]},
                {"name": "Chapter 3: Government and United Nations", "topics": ["Democratic Government of India (Parliament, President, PM, Judiciary)", "The Indian Constitution & Fundamental Rights", "The United Nations: Origin, Organs & Agencies (UNESCO, UNICEF, WHO)"]}
            ]
        }
    ],

    ("ICSE", "Class 6"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Number System & Integers", "topics": ["Natural & Whole Numbers, Properties", "Integers: Representation, Addition & Subtraction on Number Line", "HCF and LCM by Division & Factorization", "Playing with Numbers & Divisibility Rules"]},
                {"name": "Chapter 2: Fractions & Decimals", "topics": ["Fractions: Types, Equivalent, Comparison", "Operations on Fractions", "Decimals: Place Value, Addition, Subtraction, Multiplication, Division", "Terminating & Repeating Decimals"]},
                {"name": "Chapter 3: Commercial Arithmetic", "topics": ["Ratio and Proportion", "Unitary Method", "Percentage Concept & Applications", "Speed, Distance and Time Calculations"]},
                {"name": "Chapter 4: Algebra", "topics": ["Fundamental Concepts & Variables", "Algebraic Expressions & Terms (Monomial, Binomial, Trinomial)", "Addition and Subtraction of Algebraic Expressions", "Linear Equations in One Variable"]},
                {"name": "Chapter 5: Geometry & Mensuration", "topics": ["Basic Geometrical Ideas (Points, Lines, Planes, Rays)", "Angles and Their Types", "Parallel Lines and Transversals", "Triangles, Quadrilaterals & Circles", "Perimeter and Area of Plane Figures", "Data Handling & Bar Graphs"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Matter & Measurement", "topics": ["States of Matter & Molecular Properties", "Measurement of Length, Mass & Time", "Units & SI System", "Measurement of Area & Volume"]},
                {"name": "Chapter 2: Force and Friction", "topics": ["Concept of Force & Effects", "Types of Forces (Contact & Non-Contact)", "Friction: Types, Advantages, Disadvantages & Methods of Reduction"]},
                {"name": "Chapter 3: Simple Machines & Energy", "topics": ["Concept of Simple Machine & Mechanical Advantage", "Levers (Class I, II, III)", "Pulley, Inclined Plane, Wheel and Axle, Wedge, Screw", "Forms of Energy & Conservation of Energy"]},
                {"name": "Chapter 4: Light & Magnetism", "topics": ["Luminous & Non-Luminous Objects", "Rectilinear Propagation of Light & Pin-hole Camera", "Shadows & Eclipses (Solar & Lunar)", "Magnetic Properties, Poles & Magnetic Compass"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Introduction to Chemistry", "topics": ["Scope and Importance of Chemistry", "Chemistry Laboratory Apparatus & Safety Rules", "Famous Chemists & Discoveries"]},
                {"name": "Chapter 2: Elements, Compounds & Mixtures", "topics": ["Pure Substances vs Mixtures", "Elements: Metals, Non-metals, Metalloids, Noble Gases", "Symbols of Common Elements", "Compounds & Chemical Formulae", "Methods of Separation (Filtration, Evaporation, Distillation, Magnetic)"]},
                {"name": "Chapter 3: Matter & Physical/Chemical Changes", "topics": ["Classification of Matter", "Characteristics of Solids, Liquids, Gases", "Physical vs Chemical Changes with Examples", "Law of Conservation of Mass Overview"]},
                {"name": "Chapter 4: Air and Atmosphere & Water", "topics": ["Composition of Air", "Importance of Oxygen, Nitrogen, Carbon Dioxide", "Rusting of Iron and Prevention", "Water: Universal Solvent & Water Cycle", "Water Pollution & Conservation"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Plant Life", "topics": ["The Leaf: Structure, Venation & Modifications", "Photosynthesis: Process & Significance", "Transpiration in Plants", "The Flower: Parts, Functions & Pollination", "Fertilization and Seed Formation"]},
                {"name": "Chapter 2: Cell - The Unit of Life", "topics": ["Discovery of Cell & Cell Theory", "Structure of Plant Cell vs Animal Cell", "Cell Organelles: Nucleus, Mitochondria, Chloroplast, Vacuole", "Prokaryotic vs Eukaryotic Cells"]},
                {"name": "Chapter 3: Human Body: Organ Systems", "topics": ["Digestive System: Organs, Digestion Process & Enzymes", "Respiratory System: Mechanism of Breathing & Cellular Respiration", "Circulatory System Overview"]},
                {"name": "Chapter 4: Health and Hygiene & Habitat", "topics": ["Types of Diseases: Infectious & Non-infectious", "Modes of Transmission of Diseases", "Personal & Community Hygiene", "Adaptations in Plants and Animals (Desert, Aquatic, Mountain)"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "History: Ancient Civilizations", "topics": ["Mesopotamian, Egyptian & Chinese Civilizations", "Indus Valley Civilization: Town Planning, Social Life, Trade & Decline", "The Vedic Period: Early & Later Vedic Life"]},
                {"name": "History: Empires & Rise of Religions", "topics": ["Rise of Jainism and Buddhism", "The Mauryan Empire: Chandragupta & Ashoka", "The Golden Age of Guptas"]},
                {"name": "Civics: Rural & Urban Governance", "topics": ["Rural Local Self-Government: Panchayati Raj (Gram Panchayat, Panchayat Samiti, Zila Parishad)", "Urban Local Self-Government: Municipal Corporations & Municipalities"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Maps and Globes & Major Landforms", "topics": ["Types of Maps, Scale, Legend & Cardinal Directions", "Mountains, Plateaus, Plains, Valleys - Formation & Importance", "Major Water Bodies (Oceans, Seas, Lakes, Rivers)"]},
                {"name": "Chapter 2: Study of Continents: North & South America", "topics": ["North America: Location, Physical Features, Great Lakes, Climate & Vegetation", "South America: Physical Features, Amazon Basin, Andes Mountains, Pampas"]}
            ]
        }
    ],

    ("ICSE", "Class 7"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Integers & Rational Numbers", "topics": ["Operations on Integers & Properties", "Rational Numbers: Representation, Operations & Comparison", "Decimals & Recurring Decimals", "Exponents and Powers (Laws of Indices)"]},
                {"name": "Chapter 2: Commercial Arithmetic", "topics": ["Ratio, Proportion & Unitary Method", "Percentage & Its Applications", "Profit, Loss and Discount", "Simple Interest Calculation", "Speed, Distance, Time & Trains"]},
                {"name": "Chapter 3: Algebra", "topics": ["Algebraic Expressions: Degree, Terms, Coefficients", "Addition, Subtraction & Multiplication of Polynomials", "Linear Equations in One Variable (Word Problems)", "Inequalities Basic Introduction"]},
                {"name": "Chapter 4: Geometry & Mensuration", "topics": ["Lines and Angles: Complementary, Supplementary, Transversal", "Properties of Triangles: Angle Sum, Exterior Angle, Congruence (SSS, SAS, ASA, RHS)", "Perimeter and Area of Triangle, Parallelogram, Rhombus, Circle", "Data Handling: Mean, Median, Mode, Bar Graphs"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Physical Quantities & Measurement", "topics": ["Measurement of Volume, Density & Relative Density", "Density Bottle Method", "Floatation and Sinking", "Speed and Velocity"]},
                {"name": "Chapter 2: Motion & Force", "topics": ["Types of Motion (Translatory, Rotatory, Oscillatory, Periodic)", "Distance vs Displacement", "Uniform and Non-uniform Motion", "Weight and Mass Comparison"]},
                {"name": "Chapter 3: Energy & Light", "topics": ["Energy: Kinetic and Potential Energy Formulas", "Law of Conservation of Energy", "Reflection of Light: Laws of Reflection", "Plane Mirrors: Image Formation & Characteristics", "Spherical Mirrors: Concave & Convex Mirrors Basics"]},
                {"name": "Chapter 4: Heat & Sound", "topics": ["Heat vs Temperature & Thermometers", "Modes of Heat Transfer: Conduction, Convection, Radiation", "Thermal Expansion of Solids, Liquids, Gases", "Sound: Production, Propagation, Amplitude, Pitch, Loudness"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Matter and Its Composition", "topics": ["Kinetic Molecular Theory of Matter", "Changes of State in terms of Kinetic Theory", "Law of Conservation of Mass"]},
                {"name": "Chapter 2: Elements, Compounds and Chemical Reactions", "topics": ["Valency and Chemical Formulae of Radicals", "Balancing Chemical Equations", "Types of Chemical Reactions (Combination, Decomposition, Displacement, Double Displacement)"]},
                {"name": "Chapter 3: Atomic Structure", "topics": ["Structure of an Atom: Protons, Neutrons, Electrons", "Atomic Number and Mass Number", "Electronic Configuration (up to Z=20)", "Isotopes Concept"]},
                {"name": "Chapter 4: Metals and Non-Metals & Air", "topics": ["Physical Properties of Metals vs Non-Metals", "Chemical Properties & Reactivity Series", "Uses of Common Metals (Fe, Cu, Al, Au)", "Air & Composition, Greenhouse Effect & Acid Rain"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Plant and Animal Tissues", "topics": ["Plant Tissues: Meristematic & Permanent (Parenchyma, Collenchyma, Sclerenchyma, Xylem, Phloem)", "Animal Tissues: Epithelial, Connective, Muscular, Nervous", "Tissue Functions & Differences"]},
                {"name": "Chapter 2: Kingdom Classification", "topics": ["Five Kingdom Classification (Monera, Protista, Fungi, Plantae, Animalia)", "Invertebrates: Porifera to Echinodermata", "Vertebrates: Pisces, Amphibia, Reptilia, Aves, Mammalia"]},
                {"name": "Chapter 3: Plant Life & Human Body", "topics": ["Photosynthesis & Respiration in Plants", "Human Excretory System: Kidneys, Nephron Structure, Urine Formation", "Human Nervous System: Brain, Spinal Cord, Reflex Action"]},
                {"name": "Chapter 4: Health, Hygiene & Allergy", "topics": ["Types of Allergies & Allergens", "Symptoms and Prevention of Allergies", "First Aid and Safety Measures"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "History: Medieval India", "topics": ["Rise of Christianity and Islam", "The Turkish Invasions: Mahmud of Ghazni & Muhammad Ghori", "The Delhi Sultanate: Slave, Khilji, Tughlaq dynasties", "The Mughal Empire: Babur, Akbar, Shah Jahan, Aurangzeb", "The Bhakti and Sufi Movements"]},
                {"name": "Civics: The Constitution & Democracy", "topics": ["Making of the Indian Constitution & Preamble", "Directive Principles of State Policy", "Fundamental Rights and Fundamental Duties"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Topographical Sheets & Weather", "topics": ["Contour Lines, Symbols and Colours on Topo Sheets", "Weather vs Climate & Weather Instruments (Thermometer, Barometer, Hygrometer, Rain Gauge, Anemometer)"]},
                {"name": "Chapter 2: Study of Continents: Europe & Africa", "topics": ["Europe: Location, Physical Divisions, Rhine & Danube Rivers, Climate & Industries", "Africa: Rift Valley, Sahara Desert, Nile River, Congo Basin, Wildlife & Resources"]}
            ]
        }
    ],

    ("ICSE", "Class 8"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Number System & Sets", "topics": ["Rational Numbers Operations & Representation", "Exponents and Radicals", "Squares, Square Roots, Cubes & Cube Roots", "Set Theory: Representation, Types, Union, Intersection, Venn Diagrams"]},
                {"name": "Chapter 2: Commercial Mathematics", "topics": ["Compound Interest (Formula and Without Formula)", "Inverse Variation & Time and Work", "Percentage, Profit, Loss & Discount", "GST (Goods and Services Tax) Basics"]},
                {"name": "Chapter 3: Algebra", "topics": ["Algebraic Identities & Expansions: (a+b)², (a-b)², (a+b)³", "Factorisation of Algebraic Expressions (Grouping, Difference of Squares, Middle Term Splitting)", "Linear Equations & Word Problems", "Simultaneous Linear Equations in Two Variables"]},
                {"name": "Chapter 4: Geometry & Mensuration", "topics": ["Polygons & Angle Sum Property", "Quadrilaterals: Parallelogram, Rectangle, Rhombus, Square, Trapezium", "Constructions of Quadrilaterals", "Circles: Theorems and Chords", "Surface Area and Volume of Cube, Cuboid, Cylinder", "Statistics: Frequency Distribution, Histograms"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Matter & Pressure", "topics": ["Kinetic Theory of Matter Explanation", "Pressure in Fluids: Hydrostatic Pressure & Pascal's Law", "Atmospheric Pressure & Barometers", "Buoyancy & Archimedes' Principle", "Principle of Floatation & Submarines"]},
                {"name": "Chapter 2: Force and Motion", "topics": ["Newton's First, Second and Third Laws of Motion", "Linear Momentum and Conservation", "Circular Motion & Centripetal/Centrifugal Force Basics"]},
                {"name": "Chapter 3: Heat Transfer & Energy", "topics": ["Thermal Energy & Phase Changes (Boiling, Melting, Latent Heat)", "Conduction, Convection & Radiation Deep Dive", "Applications: Vacuum Flask, Ventilation, Sea/Land Breeze"]},
                {"name": "Chapter 4: Light, Sound & Electricity", "topics": ["Refraction of Light & Refractive Index", "Total Internal Reflection & Mirage", "Lenses: Convex and Concave Ray Diagrams & Formula", "Sound: Resonance, Echo, SONAR", "Static Electricity: Electroscope, Lightning & Conductors"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Matter & Chemical Reactions", "topics": ["States of Matter & Phase Transitions", "Chemical Reactions: Reactants, Products & Balancing", "Combustion & Types of Flame"]},
                {"name": "Chapter 2: Atomic Structure & Chemical Bonding", "topics": ["Dalton's Atomic Theory & Modern Atomic Structure", "Rutherford's & Bohr's Models", "Valency & Octet Rule", "Electrovalent (Ionic) and Covalent Bonding"]},
                {"name": "Chapter 3: Periodic Table & Language of Chemistry", "topics": ["Mendeleev's vs Modern Periodic Table", "Groups and Periods Overview", "Writing Chemical Formulae & Radical Valencies", "Relative Atomic Mass and Molecular Mass"]},
                {"name": "Chapter 4: Hydrogen, Carbon and Its Compounds", "topics": ["Preparation and Properties of Hydrogen Gas", "Oxidation and Reduction Concept", "Allotropes of Carbon: Diamond, Graphite, Fullerenes", "Oxides of Carbon (CO, CO2) & Greenhouse Effect"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Transport in Plants & Reproduction", "topics": ["Diffusion, Osmosis, Active Transport", "Xylem & Phloem: Mechanism of Conduction", "Transpiration Pull & Factors Affecting Transpiration", "Asexual vs Sexual Reproduction in Plants", "Pollination & Fertilization in Detail"]},
                {"name": "Chapter 2: Human Body: Endocrine & Circulatory System", "topics": ["Endocrine Glands & Hormones (Pituitary, Thyroid, Pancreas, Adrenal)", "Adolescence, Puberty & Stress Management", "Human Heart: Structure, Double Circulation, Blood Vessels & Blood Groups"]},
                {"name": "Chapter 3: Human Nervous System & Diseases", "topics": ["Structure of a Neuron", "Central, Peripheral & Autonomous Nervous System", "Reflex Arc and Reflex Action", "Communicable Diseases, Pathogens, Immunity & Vaccination"]},
                {"name": "Chapter 4: Ecology and Ecosystem", "topics": ["Abiotic and Biotic Components", "Food Chains, Food Webs & Ecological Pyramids", "Forest, Desert & Aquatic Ecosystems", "Carbon Cycle, Nitrogen Cycle & Conservation"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "History: The Modern World & British Rule in India", "topics": ["The Industrial Revolution & Age of Revolutions (American & French)", "Decline of Mughals & Rise of Independent Kingdoms", "Expansion of British Power: Battle of Plassey & Buxar", "Subsidiary Alliance & Doctrine of Lapse", "Social and Religious Reform Movements (Raja Ram Mohan Roy, Swami Vivekananda)"]},
                {"name": "Civics: The Union Legislature & Judiciary", "topics": ["The Union Parliament: Lok Sabha, Rajya Sabha, Law-making Process", "The Union Judiciary: Supreme Court, High Courts, Subordinate Courts"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Topographical Maps & Climate", "topics": ["Grid References (4-figure & 6-figure)", "Topographical Features & Drainage Patterns", "Atmospheric Pressure Belts and Planetary Winds", "Cyclones and Anticyclones"]},
                {"name": "Chapter 2: Study of Continents: Asia & India", "topics": ["Asia: Location, Physical Divisions, River Systems, Climate & Natural Vegetation", "India: Geographical Location, Physical Divisions, Major Rivers & Drainage Systems"]}
            ]
        }
    ],

    ("ICSE", "Class 9"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Pure & Commercial Mathematics", "topics": ["Rational and Irrational Numbers & Surds", "Compound Interest without Formula", "Compound Interest using Formula", "Expansions: Algebraic Formulas & Identities"]},
                {"name": "Chapter 2: Algebra", "topics": ["Factorisation of Polynomials", "Simultaneous Linear Equations in Two Variables (Elimination, Substitution, Cross-Multiplication)", "Indices and Logarithms (Laws of Logarithms)"]},
                {"name": "Chapter 3: Geometry & Coordinate Geometry", "topics": ["Triangles: Congruency & Inequalities", "Mid-Point Theorem and Intercept Theorem", "Pythagoras Theorem & Proof", "Rectilinear Figures (Quadrilaterals)", "Coordinate Geometry: Cartesian Plane, Distance Formula"]},
                {"name": "Chapter 4: Trigonometry, Mensuration & Statistics", "topics": ["Trigonometric Ratios of Standard Angles (0, 30, 45, 60, 90)", "Simple 2D Trigonometric Problems", "Area and Perimeter of Triangle and Quadrilateral", "Surface Area and Volume of 3D Solids", "Statistics: Mean, Median, Frequency Distribution Tables"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Measurements and Experimentation", "topics": ["Least Count & Vernier Calipers", "Micrometer Screw Gauge", "Simple Pendulum & Factors Affecting Time Period"]},
                {"name": "Chapter 2: Motion in One Dimension & Laws of Motion", "topics": ["Rest, Motion, Scalar & Vector Quantities", "Speed, Velocity & Acceleration (Equations of Motion)", "Graphical Representation of Motion (s-t, v-t graphs)", "Newton's Laws of Motion & Gravitation (Universal Law, g vs G)"]},
                {"name": "Chapter 3: Fluids, Pressure & Heat", "topics": ["Pressure in Fluids & Atmospheric Pressure", "Archimedes' Principle & Relative Density", "Thermal Expansion of Solids, Liquids, Gases", "Calorimetry: Heat Capacity, Specific Heat Capacity & Latent Heat"]},
                {"name": "Chapter 4: Light, Sound & Electricity", "topics": ["Reflection of Light: Plane & Spherical Mirrors (Ray Diagrams)", "Propagation of Sound Waves, Range of Hearing (Infrasonic, Ultrasonic)", "Current Electricity: Simple Circuit, Potential Difference, Conductors & Insulators", "Magnetism: Magnetic Field of Earth & Electromagnets"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: The Language of Chemistry & Chemical Changes", "topics": ["Symbols, Valency & Chemical Formulae", "Writing and Balancing Chemical Equations", "Relative Molecular Mass & Percentage Composition", "Energy Changes in Reactions (Exothermic & Endothermic)"]},
                {"name": "Chapter 2: Water & Atomic Structure", "topics": ["Water as Universal Solvent, Solutions, Suspensions", "Hard and Soft Water & Removal of Hardness", "Rutherford's Model & Bohr's Model of Atom", "Atomic Number, Mass Number, Electronic Configuration"]},
                {"name": "Chapter 3: The Periodic Table & Chemical Bonding", "topics": ["Modern Periodic Table & Periodic Trends (Valency, Metallic character)", "Electrovalent (Ionic) Bonding & Properties", "Covalent Bonding & Electron Dot Diagrams"]},
                {"name": "Chapter 4: Study of Gas Laws & Atmospheric Pollution", "topics": ["Boyle's Law and Charles's Law (P1V1=P2V2, V1/T1=V2/T2)", "Standard Temperature and Pressure (STP)", "Acid Rain, Global Warming, Ozone Depletion"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Basic Biology & Plant Physiology", "topics": ["Cell: The Unit of Life & Organelles", "Plant and Animal Tissues Structure & Function", "The Flower: Structure, Pollination & Fertilization", "Structure and Germination of Seeds", "Respiration in Plants"]},
                {"name": "Chapter 2: Human Anatomy & Physiology", "topics": ["Human Digestive System & Teeth", "Human Skeletal System: Bones, Joints & Axial/Appendicular Skeleton", "Human Respiratory System: Inhalation, Exhalation & Capacity", "Skin: Structure, Functions & Temperature Regulation"]},
                {"name": "Chapter 3: Health, Hygiene & Waste Management", "topics": ["Bacterial & Viral Diseases (Modes of transmission, symptoms, prevention)", "Hygiene, Sanitation & First Aid", "Waste Generation, Segregation & Safe Disposal"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "Civics: Our Constitution & Elections", "topics": ["The Indian Constitution: Features & Preamble", "Fundamental Rights, Fundamental Duties & Directive Principles", "Elections and the Election Commission of India", "Local Self-Government: Rural and Urban"]},
                {"name": "History: Ancient & Medieval India", "topics": ["The Harappan Civilization & Vedic Period", "Jainism and Buddhism", "The Mauryan Empire & The Sangam Age", "The Gupta Empire & The Chola Empire", "The Delhi Sultanate & The Mughal Empire", "The Renaissance and The Reformation in Europe"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Principles of Geography", "topics": ["Earth as a Planet & Shape of Earth", "Latitudes, Longitudes & International Date Line", "Rotation and Revolution of Earth & Seasons", "Structure of Earth: Crust, Mantle, Core", "Landforms of the Earth: Mountains, Plateaus, Plains", "Rocks: Igneous, Sedimentary, Metamorphic"]},
                {"name": "Chapter 2: Atmosphere, Hydrosphere & Pollution", "topics": ["Composition and Structure of Atmosphere", "Insolation and Heat Budget", "Atmospheric Pressure and Winds", "Humidity, Condensation & Precipitation", "Tides and Ocean Currents", "Pollution: Causes, Effects & Prevention"]}
            ]
        }
    ],

    ("ICSE", "Class 10"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Commercial Mathematics", "topics": ["Goods and Services Tax (GST) - CGST, SGST, IGST calculations", "Banking: Recurring Deposit (RD) Accounts & Maturity Value", "Shares and Dividends: Face Value, Market Value, Dividend, Yield Rate"]},
                {"name": "Chapter 2: Algebra", "topics": ["Linear Inequations on Number Line", "Quadratic Equations in One Variable (Factorisation & Formula Method)", "Remainder and Factor Theorems (Factorising cubic polynomials)", "Matrices: Order, Addition, Subtraction, Multiplication & Identity Matrix", "Arithmetic Progression (AP): nth term & Sum of n terms", "Geometric Progression (GP): nth term & Sum of n terms"]},
                {"name": "Chapter 3: Geometry & Coordinate Geometry", "topics": ["Similarity of Triangles: Axioms, Basic Proportionality Theorem, Area Theorem", "Loci: Definition and Theorems", "Circles: Angle Properties, Cyclic Properties, Tangent & Secant Properties", "Constructions: Tangents to Circles, Circumcircle, Incircle", "Reflection: Line & Origin Reflection", "Section and Mid-Point Formula", "Equation of a Line: Slope, Intercept, Point-Slope Form"]},
                {"name": "Chapter 4: Trigonometry, Mensuration & Statistics", "topics": ["Trigonometric Identities: Proof and Applications", "Heights and Distances: Angles of Elevation & Depression", "Surface Area and Volume: Cylinder, Cone, Sphere, Hemisphere & Combinations", "Statistics: Mean (Direct, Short-cut, Step-deviation), Median, Mode", "Graphical Representation: Ogive (Cumulative Frequency Curve) & Interquartile Range", "Probability: Classical Definition & Simple Events"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Force, Work, Power and Energy", "topics": ["Turning Effect of Force: Moment of Force & Couple", "Equilibrium of Bodies & Center of Gravity", "Work, Energy, Power: Definitions, Formulas & Units", "Machines as Force Multipliers: Levers, Pulleys, Mechanical Advantage, Velocity Ratio, Efficiency", "Principle of Conservation of Energy"]},
                {"name": "Chapter 2: Light", "topics": ["Refraction through Plane Surface: Snell's Law & Refractive Index", "Refraction through Prism: Deviation, Dispersion & Spectrum", "Total Internal Reflection & Critical Angle", "Refraction through Convex & Concave Lenses: Ray Diagrams, Lens Formula, Power of Lens", "Electromagnetic Spectrum & Uses of Various Radiations"]},
                {"name": "Chapter 3: Sound", "topics": ["Reflection of Sound: Echoes, Conditions for Echo & Numerical Problems", "Applications of Echo: SONAR, Medical Imaging", "Natural, Damped & Forced Vibrations", "Resonance: Definition, Examples & Differentiating Characteristics", "Loudness, Pitch and Quality (Timbre) of Sound"]},
                {"name": "Chapter 4: Electricity and Magnetism", "topics": ["Ohm's Law, Resistance, Factors Affecting Resistance & Resistivity", "Resistors in Series and Parallel Combinations", "Electromotive Force (EMF), Terminal Voltage & Internal Resistance", "Electrical Energy and Electrical Power (kWh calculation)", "Household Wiring: Ring System, Switches, Fuses, Earthing, Three-pin Plugs", "Magnetic Effect of Current: Right Hand Thumb Rule, Solenoid, Electromagnet", "Force on a Conductor in a Magnetic Field: Fleming's Left Hand Rule & DC Motor", "Electromagnetic Induction: Fleming's Right Hand Rule & AC Generator, Transformer"]},
                {"name": "Chapter 5: Heat & Modern Physics", "topics": ["Heat Capacity and Specific Heat Capacity (Principle of Calorimetry: Q = mcΔT)", "Latent Heat and Specific Latent Heat of Fusion/Vaporization", "Radioactivity: Nuclear Structure, Alpha, Beta and Gamma Emissions & Properties", "Nuclear Fission and Nuclear Fusion Basics", "Safety Precautions and Background Radiation"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Periodic Table & Chemical Bonding", "topics": ["Periodic Properties: Atomic Size, Ionization Potential, Electron Affinity, Electronegativity, Metallic Character", "Periodic Trends across Periods and down Groups", "Electrovalent (Ionic) Bonding: Electron dot diagrams (NaCl, MgCl2, CaO)", "Covalent Bonding: Non-polar and Polar (H2, Cl2, O2, N2, H2O, NH3, CH4, CCl4)", "Coordinate Bonding: Formation of Ammonium ion (NH4+) and Hydronium ion (H3O+)"]},
                {"name": "Chapter 2: Acids, Bases, Salts & Analytical Chemistry", "topics": ["Definitions of Acids and Bases according to Arrhenius Theory", "Classification and Properties of Acids and Bases", "pH Scale & Indicators", "Salts: Normal, Acid, Basic Salts & Methods of Preparation", "Action of Sodium Hydroxide and Ammonium Hydroxide on Salt Solutions (Fe2+, Fe3+, Cu2+, Zn2+, Pb2+)"]},
                {"name": "Chapter 3: Mole Concept and Stoichiometry", "topics": ["Gay-Lussac's Law of Combining Volumes", "Avogadro's Law: Definition, Application & Mole Concept", "Relative Atomic Mass, Relative Molecular Mass & Gram Molecular Mass", "Vapour Density and Molecular Weight Relationship (VD = MW / 2)", "Empirical and Molecular Formula Calculations", "Chemical Stoichiometry & Mass-Volume Calculations"]},
                {"name": "Chapter 4: Electrolysis & Metallurgy", "topics": ["Electrolytes vs Non-electrolytes, Strong and Weak Electrolytes", "Electrolysis of Molten Lead Bromide, Acidulated Water, Aqueous Copper Sulphate", "Applications: Electroplating (with Silver and Nickel) and Electro-refining of Copper", "Extraction of Aluminium: Hall-Héroult Process, Baeyer's Process, Hoop's Process", "Alloys: Composition and Uses of Brass, Bronze, Duralumin, Solder, Stainless Steel"]},
                {"name": "Chapter 5: Study of Compounds", "topics": ["Hydrogen Chloride (HCl): Laboratory Preparation, Fountain Experiment, Chemical Properties", "Ammonia (NH3): Laboratory Preparation, Haber's Process, Fountain Experiment, Chemical Reactions", "Nitric Acid (HNO3): Laboratory Preparation, Ostwald's Process, Oxidizing Properties", "Sulphuric Acid (H2SO4): Contact Process, Dehydrating Property, Oxidizing Property"]},
                {"name": "Chapter 6: Organic Chemistry", "topics": ["Introduction to Organic Compounds, Tetravalency of Carbon & Catenation", "Homologous Series, Functional Groups & IUPAC Nomenclature", "Alkanes (Methane, Ethane): Preparation and Reactions", "Alkenes (Ethene): Preparation and Addition Reactions", "Alkynes (Ethyne): Preparation and Reactions", "Alcohols (Methanol, Ethanol) & Carboxylic Acids (Ethanoic Acid)"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Basic Biology & Genetics", "topics": ["Structure of Chromosomes: DNA, Histones & Genes", "Cell Division: Mitosis (Stages & Significance) vs Meiosis Overview", "Genetics: Mendel's Laws of Inheritance (Monohybrid & Dihybrid Cross)", "Sex Determination in Humans & Genetic Disorders (Haemophilia, Colour Blindness)"]},
                {"name": "Chapter 2: Plant Physiology", "topics": ["Absorption by Roots: Imbibition, Diffusion, Osmosis, Turgidity, Plasmolysis, Root Pressure", "Transpiration: Mechanism, Stomatal Transpiration, Experiments & Significance", "Photosynthesis: Light Reaction & Dark Reaction, Experiments on Sunlight, Chlorophyll, CO2", "Chemical Coordination in Plants: Auxins, Gibberellins, Cytokinins, Abscisic Acid, Ethylene", "Tropic Movements: Phototropism, Geotropism, Hydrotropism, Thigmotropism"]},
                {"name": "Chapter 3: Human Anatomy & Physiology", "topics": ["Circulatory System: Blood Composition, Blood Vessels, Structure of Heart, Double Circulation, Pulse, BP", "Excretory System: Internal Structure of Kidney, Structure of Nephron, Ultrafiltration, Selective Reabsorption", "Nervous System: Structure of Neuron, Central Nervous System (Brain & Spinal Cord), Reflex Action", "Sense Organs: Eye (Structure, Working, Defects: Myopia, Hypermetropia, Astigmatism) & Ear (Hearing and Balance)", "Endocrine System: Adrenal, Thyroid, Pancreas, Pituitary Glands & Hormonal Disorders", "Reproductive System: Male & Female Reproductive Organs, Menstrual Cycle, Fertilization, Implantation"]},
                {"name": "Chapter 4: Population & Human Health", "topics": ["Population Explosion: Causes, Consequences & Control Methods (Contraception)", "Human Health: Cleanliness, Safe Drinking Water, First Aid, Red Cross, WHO"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "Civics: The Union Legislature", "topics": ["The Union Parliament: Composition of Lok Sabha and Rajya Sabha", "Qualifications, Term, Presiding Officers (Speaker & Chairman)", "Powers and Functions of Parliament: Legislative, Financial, Executive Control, Judicial"]},
                {"name": "Civics: The Union Executive", "topics": ["The President: Qualifications, Election, Executive, Legislative, Financial, Judicial, Emergency Powers", "The Vice-President: Election and Functions", "The Prime Minister & Council of Ministers: Appointment, Collective Responsibility, Powers and Position"]},
                {"name": "Civics: The Judiciary", "topics": ["The Supreme Court: Composition, Qualifications, Jurisdiction (Original, Appellate, Advisory, Revisory)", "Writ Jurisdiction: Habeas Corpus, Mandamus, Prohibition, Quo Warranto, Certiorari", "The High Courts: Composition, Jurisdiction & Powers", "Subordinate Courts and Lok Adalats: Structure, Functions and Advantages"]},
                {"name": "History: The Indian National Movement (1857-1917)", "topics": ["The First War of Independence (1857): Causes (Political, Socio-religious, Economic, Military) & Consequences", "Factors Leading to Growth of Nationalism & Foundation of Indian National Congress", "First Phase of INC (Early Nationalists): Objectives, Methods, Contributions of Dadabhai Naoroji, Surendranath Banerjea, Gopal Krishna Gokhale", "Second Phase of INC (Assertive Nationalists): Causes, Methods, Contributions of Bal Gangadhar Tilak, Bipin Chandra Pal, Lala Lajpat Rai", "Partition of Bengal (1905): Causes, Swadeshi & Boycott Movements", "Formation of Muslim League (1906) & Lucknow Pact (1916)"]},
                {"name": "History: Mass Movement & Independence (1915-1947)", "topics": ["Mahatma Gandhi: Non-Cooperation Movement (Causes, Programme, Suspensions, Impact)", "Civil Disobedience Movement: Dandi March, Gandhi-Irwin Pact, Round Table Conferences", "Quit India Movement: Causes (Cripps Mission failure, Japanese threat), Resolution & Significance", "Forward Bloc and the INA: Subhas Chandra Bose's Contributions", "Independence and Partition of India: Cabinet Mission Plan, Mountbatten Plan, Indian Independence Act 1947"]},
                {"name": "History: Contemporary World (World Wars & UN)", "topics": ["First World War (1914-1918): Causes (Nationalism, Imperialism, Alliances, Sarajevo Crisis) & Treaty of Versailles", "Rise of Dictatorships: Fascism in Italy (Mussolini) & Nazism in Germany (Hitler)", "Second World War (1939-1945): Causes (Treaty of Versailles failure, Rise of Fascism, Failure of League of Nations, Hitler's Invasion of Poland) & Consequences", "United Nations: Origin, Objectives, Principal Organs (General Assembly, Security Council, ICJ)", "Major UN Agencies: UNESCO, UNICEF, WHO (Objectives and Functions)", "Non-Aligned Movement (NAM): Origin, Panchsheel, Role of Jawaharlal Nehru, Josip Broz Tito, Gamal Abdel Nasser"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Interpretation of Topographical Maps", "topics": ["Grid References: 4-Figure and 6-Figure Coordinates", "Scale and Distance Measurements", "Contour Lines and Landforms: Gentle/Steep Slopes, Conical Hill, Plateau, Ridge, Cliff", "Conventional Signs and Symbols", "Drainage Patterns: Dendritic, Trellis, Radial", "Settlement Patterns: Nucleated, Dispersed, Linear", "Identification of Land Use, Occupations and Means of Transport"]},
                {"name": "Chapter 2: Map of India", "topics": ["Mountains, Peaks and Plateaus (Himalayas, Karakoram, Aravali, Vindhya, Satpura, Western/Eastern Ghats, Nilgiri, Mount Godwin Austen, Kanchenjunga, Deccan Plateau, Chota Nagpur Plateau)", "Plains and Desert: Gangetic Plains, Coastal Plains, Thar Desert", "Rivers: Indus, Jhelum, Chenab, Ravi, Beas, Sutlej, Ganga, Yamuna, Brahmaputra, Narmada, Tapi, Mahanadi, Godavari, Krishna, Cauvery", "Water Bodies and Coastlines: Gulf of Kutch, Gulf of Khambhat, Gulf of Mannar, Palk Strait, Arabian Sea, Bay of Bengal, Andaman Sea", "Cities and Lines: Delhi, Mumbai, Kolkata, Chennai, Hyderabad, Bengaluru, Tropic of Cancer, Standard Meridian (82°30'E)"]},
                {"name": "Chapter 3: Climate of India", "topics": ["Factors Affecting the Climate of India (Latitude, Altitude, Distance from Sea, Relief, Jet Streams)", "South-West Monsoon: Arabian Sea Branch and Bay of Bengal Branch", "North-East (Retreating) Monsoon and Western Disturbances", "Seasons of India: Hot Dry Summer, Rainy Season, Retreating Monsoon, Cold Winter", "Rainfall Distribution in India & Climatic Data Interpretation"]},
                {"name": "Chapter 4: Soils of India", "topics": ["Alluvial Soil: Formation, Characteristics, Types (Khadar and Bhangar), Crops Grown, Distribution", "Black (Regur) Soil: Formation from Lava, Moisture Retention, Cotton Cultivation, Distribution", "Red Soil: Formation, Characteristics, Suitability for Agriculture, Distribution", "Laterite Soil: Formation by Leaching, Acidity, Crops (Tea, Coffee, Cashew), Distribution", "Soil Erosion: Causes (Deforestation, Overgrazing, Faulty Farming) & Conservation Methods (Terracing, Afforestation, Shelterbelts)"]},
                {"name": "Chapter 5: Natural Vegetation & Water Resources", "topics": ["Tropical Evergreen Rainforests, Tropical Deciduous (Monsoon) Forests, Tropical Thorn & Scrub Forests, Mountain Forests, Mangrove (Tidal) Forests", "Forest Conservation and Social Forestry", "Water Resources: Need for Conservation, Traditional Rainwater Harvesting", "Modern Rainwater Harvesting: Rooftop Harvesting, Percolation Pits", "Irrigation: Canals, Wells, Tube-wells, Tanks, Drip & Sprinkler Irrigation (Advantages and Disadvantages)"]},
                {"name": "Chapter 6: Mineral and Energy Resources", "topics": ["Iron Ore, Bauxite, Manganese: Uses and Major Mining Centers in India", "Conventional Energy: Coal, Petroleum, Natural Gas (Distribution, Advantages and Disadvantages)", "Hydel Power: Bhakra Nangal Dam, Hirakud Dam", "Non-Conventional Energy: Solar Energy, Wind Energy, Biogas, Nuclear Energy, Geo-thermal Energy"]},
                {"name": "Chapter 7: Agriculture in India", "topics": ["Agricultural Seasons: Kharif, Rabi, Zaid", "Food Crops: Rice, Wheat, Millets, Pulses (Soil, Climate, Methods of Cultivation, Distribution)", "Cash Crops: Sugarcane, Oilseeds (Groundnut, Mustard), Cotton, Jute", "Beverage Crops: Tea and Coffee (Climatic Requirements, Pruning, Processing, Distribution)"]},
                {"name": "Chapter 8: Manufacturing Industries & Transport", "topics": ["Agro-based Industries: Sugar Industry, Textile Industry (Cotton and Silk)", "Mineral-based Industries: Iron and Steel Industry (Tata Steel, Rourkela, Bhilai, Visakhapatnam), Electronics Industry (Bengaluru)", "Roadways: Expressways, Golden Quadrilateral, National Highways (Advantages and Disadvantages)", "Railways, Waterways (Inland and Oceanic), Airways (Significance and Challenges)", "Waste Management: Need for Waste Management, Methods of Safe Disposal (Segregation, Dumping, Composting, Incineration, 3 R's - Reduce, Reuse, Recycle)"]}
            ]
        },
        {
            "name": "English Language & Literature", "color": "#0284C7",
            "chapters": [
                {"name": "English Language: Composition & Grammar", "topics": ["Descriptive & Narrative Essay Writing", "Argumentative & Story Writing", "Formal & Informal Letter Writing", "Notice Writing and Email Writing Formats", "Unseen Comprehension Passage & Précis Writing", "Functional Grammar: Transformation of Sentences, Prepositions, Tenses, Phrasal Verbs, Synthesis of Sentences"]},
                {"name": "Literature: Drama - Julius Caesar", "topics": ["Act III Scene 1: The Assassination of Caesar", "Act III Scene 2: Antony's Funeral Oration", "Act III Scene 3: Death of Cinna the Poet", "Act IV Scene 1 to 3: The Triumvirs and Quarrel between Brutus and Cassius", "Act V Scene 1 to 5: The Battle of Philippi and Death of Brutus"]},
                {"name": "Literature: Treasure Chest (Poems)", "topics": ["Haunted Houses - H.W. Longfellow", "The Glove and the Lions - Leigh Hunt", "When Great Trees Fall - Maya Angelou", "A Considerable Speck - Robert Frost", "The Power of Music - Sukumar Ray"]},
                {"name": "Literature: Treasure Chest (Short Stories)", "topics": ["With the Photographer - Stephen Leacock", "The Elevator - William Sleator", "The Girl Who Can - Ama Ata Aidoo", "The Last Lesson - Alphonse Daudet", "A Face in the Dark - Ruskin Bond"]}
            ]
        },
        {
            "name": "Computer Applications (Java)", "color": "#14B8A6",
            "chapters": [
                {"name": "Unit 1: Object-Oriented Concepts & Java Basics", "topics": ["Principles of OOP: Abstraction, Encapsulation, Inheritance, Polymorphism", "Classes as Basis of Computation & Objects as Instances", "Java Data Types: Primitive vs Non-primitive, Type Casting & Operators", "Control Statements: Conditional (if-else, switch-case) & Loops (for, while, do-while)"]},
                {"name": "Unit 2: User-Defined Methods & Constructors", "topics": ["Method Definition, Syntax, Return Types & Parameters", "Call by Value vs Call by Reference", "Method Overloading: Rules and Implementation", "Constructors: Default vs Parameterized, Constructor Overloading, 'this' Keyword"]},
                {"name": "Unit 3: Library Classes & String Handling", "topics": ["Wrapper Classes: Character, Integer, Double and Methods (isLetter, isDigit, toUpperCase)", "String Class Methods: length(), charAt(), indexOf(), substring(), toUpperCase(), equals(), compareTo(), replace(), trim()", "String Buffer & String Tokenizer Basics", "String Manipulation Algorithms (Reversing, Palindrome, Pig Latin, Word Frequency)"]},
                {"name": "Unit 4: Arrays & Data Structures", "topics": ["Single Dimensional Arrays (1D): Declaration, Initialization, Input", "Searching Algorithms: Linear Search and Binary Search", "Sorting Algorithms: Bubble Sort and Selection Sort", "Double Dimensional Arrays (2D): Declaration, Row-wise/Column-wise Traversal, Sum of Diagonals"]}
            ]
        },
        {
            "name": "Hindi (हिन्दी)", "color": "#E11D48",
            "chapters": [
                {
                    "name": "Chapter 1: हिन्दी भाषा एवं व्याकरण (Hindi Grammar & Writing)",
                    "topics": [
                        "निबन्ध लेखन (प्रस्ताव / Essay Writing - वर्णनात्मक, विचारात्मक, विवरणात्मक)",
                        "पत्र लेखन (औपचारिक एवं अनौपचारिक पत्र / Formal & Informal Letter)",
                        "अपठित गद्यांश बोध एवं प्रश्नोत्तर (Unseen Comprehension)",
                        "व्यावहारिक व्याकरण: विलोम शब्द, पर्यायवाची शब्द, भाववाचक संज्ञा निर्माण",
                        "विशेषण निर्माण, अनेक शब्दों के लिए एक शब्द, समरूपी भिन्नार्थक शब्द",
                        "मुहावरे एवं लोकोक्तियाँ: अर्थ एवं वाक्य प्रयोग",
                        "वाक्य रूपान्तरण (सरल, संयुक्त, मिश्रित), वाच्य परिवर्तन, काल परिवर्तन",
                        "वाक्य शुद्धिकरण एवं वर्तनी शुद्धि"
                    ]
                },
                {
                    "name": "Chapter 2: साहित्य सागर (गद्य भाग - कहानियाँ)",
                    "topics": [
                        "बात अठन्नी की - सुदर्शन (कथासार, चरित्र-चित्रण व प्रश्नोत्तर)",
                        "काकी - सियारामशरण गुप्त (कथासार, चरित्र-चित्रण व प्रश्नोत्तर)",
                        "महायज्ञ का पुरस्कार - यशपाल (कथासार, चरित्र-चित्रण व प्रश्नोत्तर)",
                        "नेताजी का चश्मा - स्वयं प्रकाश (कथासार, देशप्रेम भाव व प्रश्नोत्तर)",
                        "अपना-अपना भाग्य - जैनेन्द्र कुमार (कथासार, सामाजिक विषमता व प्रश्नोत्तर)",
                        "बड़े घर की बेटी - प्रेमचंद (कथासार, संयुक्त परिवार मूल्य व प्रश्नोत्तर)",
                        "संदेह - जयशंकर प्रसाद (कथासार, मनोविज्ञान व प्रश्नोत्तर)",
                        "भीड़ में खोया आदमी - लीलाधर शर्मा पर्वतीय (जनसंख्या समस्या व प्रश्नोत्तर)",
                        "भेड़ें और भेड़िए - हरिशंकर परसाई (व्यंग्य कथासार व राजनीति बोध)",
                        "दो कलाकार - मन्नू भंडारी (कथासार, चित्रा व अरुणा का चरित्र-चित्रण)"
                    ]
                },
                {
                    "name": "Chapter 3: साहित्य सागर (पद्य भाग - कविताएँ)",
                    "topics": [
                        "साखी - कबीरदास (दोहे, अर्थ, व्याख्या व सन्देश)",
                        "गिरधर की कुंडलियाँ - गिरधर कविराय (नीतिपरक कुंडलियाँ व व्याख्या)",
                        "स्वर्ग बना सकते हैं - रामधारी सिंह 'दिनकर' (काव्य भावार्थ व सामाजिक चेतना)",
                        "वह जन्मभूमि मेरी - सोहनलाल द्विवेदी (देशप्रेम, प्राकृतिक सौंदर्य व व्याख्या)",
                        "मेघ आए - सर्वेश्वर दयाल सक्सेना (मानवीकरण अलंकार, प्रकृति चित्रण व भावार्थ)",
                        "सूर के पद - सूरदास (वात्सल्य रस, बाल-लीला व व्याख्या)",
                        "विनय के पद - तुलसीदास (भक्ति भाव, दीनता व व्याख्या)",
                        "भिक्षुक - सूर्यकांत त्रिपाठी 'निराला' (करुण रस, यथार्थ चित्रण व व्याख्या)",
                        "चलना हमारा काम है - शिवमंगल सिंह 'सुमन' (कर्मशीलता, प्रेरणा व व्याख्या)",
                        "मातृ मंदिर की ओर - सुभद्रा कुमारी चौहान (बलिदान, राष्ट्रप्रेम व व्याख्या)"
                    ]
                },
                {
                    "name": "Chapter 4: नया रास्ता / एकांकी संचय",
                    "topics": [
                        "नया रास्ता - सुषमा अग्रवाल (अध्याय 1 से 12: मीनू का संघर्ष, आत्मनिर्भरता)",
                        "नया रास्ता - सुषमा अग्रवाल (अध्याय 13 से 26: अमित, दयाराम व सफलता)",
                        "एकांकी संचय: संस्कार और भावना - विष्णु प्रभाकर",
                        "एकांकी संचय: बहू की विदा - विनोद रस्तोगी (दहेज प्रथा पर प्रहार)",
                        "एकांकी संचय: मातृभूमि का मान - पं. हरिकृष्ण 'प्रेमी'",
                        "एकांकी संचय: सूखी डाली - उपेन्द्रनाथ 'अश्क'",
                        "एकांकी संचय: महाभारत की एक साँझ - भारतभूषण अग्रवाल",
                        "एकांकी संचय: दीपदान - डॉ. रामकुमार वर्मा (पन्ना धाय का त्याग)"
                    ]
                }
            ]
        }
    ],

    # ──────────────────────────────────────────────────────────────────────────
    # CBSE SYLLABUS DATA (CLASSES 1 TO 10)
    # ──────────────────────────────────────────────────────────────────────────
    ("CBSE", "Class 1"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Shapes and Space", "topics": ["Inside-Outside & Bigger-Smaller", "Top-Bottom & Near-Far", "Shapes Around Us", "Rolling-Sliding"]},
                {"name": "Chapter 2: Numbers from One to Nine", "topics": ["As Many As", "Counting 1 to 9", "More or Less", "Making Groups & Zero"]},
                {"name": "Chapter 3: Addition & Subtraction", "topics": ["One More", "Adding 1 to 9", "Subtracting 1 to 9", "Missing Numbers"]},
                {"name": "Chapter 4: Numbers 10 to 20 & Time", "topics": ["Grouping Tens & Ones", "Counting 10 to 20", "Order & Comparison", "Daily Routines & Time"]}
            ]
        },
        {
            "name": "Environmental Studies (EVS)", "color": "#22C55E",
            "chapters": [
                {"name": "Chapter 1: All About Me", "topics": ["My Body Parts", "My Sense Organs", "My Likes and Dislikes", "Cleanliness & Health"]},
                {"name": "Chapter 2: My Family & Home", "topics": ["Types of Families", "Rooms in My House", "Helping Each Other", "Our Neighborhood"]},
                {"name": "Chapter 3: Plant & Animal World", "topics": ["Trees, Plants & Flowers", "Domestic & Wild Animals", "Animal Babies & Sounds", "Food for Animals"]},
                {"name": "Chapter 4: Air, Water & Weather", "topics": ["Uses of Air & Water", "Keeping Water Clean", "Summer, Winter & Rainy Seasons", "Day and Night"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Alphabet & Nouns", "topics": ["Capital & Small Letters", "Naming Words (Nouns)", "A and An Articles", "One and Many (Singular/Plural)"]},
                {"name": "Unit 2: Action Words & Sentences", "topics": ["Doing Words (Verbs)", "He, She, It & They", "Simple Sentences", "Rhyming Words & Poems"]}
            ]
        }
    ],

    ("CBSE", "Class 2"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: What is Long, What is Round?", "topics": ["Long vs Round Objects", "What Rolls, What Slides?", "Building Towers"]},
                {"name": "Chapter 2: Counting in Groups & 3-Digit Numbers", "topics": ["Counting in Pairs & Tens", "Place Value & Expanded Form", "Greater Than & Less Than", "Even and Odd Numbers"]},
                {"name": "Chapter 3: Addition & Subtraction", "topics": ["Addition with Regrouping", "Subtracting 2-Digit Numbers", "Word Problems", "Patterns in Addition"]}
            ]
        },
        {
            "name": "Environmental Studies (EVS)", "color": "#22C55E",
            "chapters": [
                {"name": "Chapter 1: My Family & Neighborhood", "topics": ["Family Relations", "Community Helpers", "Places in Our Neighborhood", "Safety at Home & Road"]},
                {"name": "Chapter 2: Food & Health", "topics": ["Food Groups & Balanced Diet", "Good Food Habits", "Clean Habits", "Good Touch & Bad Touch"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Phonics & Sentences", "topics": ["Sight Words and Simple Sentences", "Punctuation Basics", "Short Stories and Rhymes"]}
            ]
        }
    ],

    ("CBSE", "Class 3"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Where to Look From & 4-Digit Numbers", "topics": ["Top, Side & Front Views", "Symmetry & Patterns", "4-Digit Numbers & Place Value", "Face Value & Place Value"]},
                {"name": "Chapter 2: Fun with Numbers & Addition", "topics": ["Counting in 10s, 50s, 100s", "Addition of 3-Digit Numbers", "Word Problems", "Mental Arithmetic"]},
                {"name": "Chapter 3: Multiplication & Division", "topics": ["Repeated Addition", "Multiplication Tables (1-10)", "Equal Sharing & Division", "Fractions Introduction"]}
            ]
        },
        {
            "name": "Environmental Studies (EVS)", "color": "#22C55E",
            "chapters": [
                {"name": "Chapter 1: Poonam's Day Out (Animals)", "topics": ["Movement of Animals", "Habitats of Animals", "Birds & Beaks", "Insects around us"]},
                {"name": "Chapter 2: The Plant Fairy", "topics": ["Types of Leaves & Trees", "Photosynthesis Basic Idea", "Uses of Plants", "Medicinal Plants"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Grammar & Vocabulary", "topics": ["Nouns and Pronouns", "Verbs and Tenses", "Reading Comprehension and Writing"]}
            ]
        }
    ],

    ("CBSE", "Class 4"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Building with Bricks & Long and Short", "topics": ["Brick Patterns & 3D Shapes", "Measuring Length (cm, m, km)", "Conversion of Units", "Perimeter Basic Idea"]},
                {"name": "Chapter 2: Multiplication, Division & Fractions", "topics": ["Multiplying Large Numbers", "Long Division", "Equivalent Fractions", "Adding & Subtracting Fractions"]}
            ]
        },
        {
            "name": "Environmental Studies (EVS)", "color": "#22C55E",
            "chapters": [
                {"name": "Chapter 1: Going to School (Transport)", "topics": ["Bridges & Trolleys", "Bicycles & Boats", "Different Paths to School", "Modes of Transport"]},
                {"name": "Chapter 2: Ear to Ear (Animal Kingdom)", "topics": ["Ears of Animals", "Skin Patterns & Camouflage", "Oviparous & Viviparous Animals", "Extinct Animals"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Grammar & Creative Writing", "topics": ["Adjectives & Adverbs", "Prepositions & Conjunctions", "Paragraph & Story Writing"]}
            ]
        }
    ],

    ("CBSE", "Class 5"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: The Fish Tale (Large Numbers)", "topics": ["Lakhs & Crores", "Speed, Distance & Time", "Loans & Interest Basic Idea", "Shapes & Angles"]},
                {"name": "Chapter 2: How Many Squares? & Fractions", "topics": ["Perimeter & Area on Grid", "Half, Quarter & Thirds", "Equivalent Fractions", "Decimals Introduction"]},
                {"name": "Chapter 3: Factors & Multiples", "topics": ["Multiples and Factors", "Prime & Composite Numbers", "LCM and HCF", "Factor Trees"]}
            ]
        },
        {
            "name": "Environmental Studies (EVS)", "color": "#22C55E",
            "chapters": [
                {"name": "Chapter 1: Super Senses", "topics": ["Amazing Senses of Animals", "Tiger & Endangered Species", "Poaching & Conservation", "Sleeping Patterns"]},
                {"name": "Chapter 2: Seeds and Seeds", "topics": ["Sprouting & Germination", "Pitcher Plant (Insectivorous)", "Dispersal of Seeds", "Seeds from Foreign Countries"]}
            ]
        },
        {
            "name": "English", "color": "#3B82F6",
            "chapters": [
                {"name": "Unit 1: Language & Literature", "topics": ["Sentence Structure & Punctuation", "Formal Letters & Notice", "Reading Comprehension"]}
            ]
        }
    ],

    ("CBSE", "Class 6"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Knowing Our Numbers", "topics": ["Comparing Numbers (Greatest and Smallest)", "Making Large Numbers & Shift Digits", "Indian & International System of Numeration", "Large Numbers in Practice (Units of length, mass, capacity)", "Estimation & Rounding Off to nearest 10, 100, 1000", "Roman Numerals up to 1000"]},
                {"name": "Chapter 2: Whole Numbers", "topics": ["Predecessor and Successor", "Representation of Whole Numbers on Number Line", "Addition, Subtraction & Multiplication on Number Line", "Properties of Whole Numbers (Closure, Commutative, Associative, Distributive)", "Identity for Addition and Multiplication", "Patterns in Whole Numbers"]},
                {"name": "Chapter 3: Playing with Numbers", "topics": ["Factors and Multiples & Perfect Numbers", "Prime and Composite Numbers (Sieve of Eratosthenes)", "Tests for Divisibility of Numbers (2, 3, 4, 5, 6, 8, 9, 10, 11)", "Common Factors and Common Multiples & Co-prime Numbers", "Prime Factorisation & Factor Tree Method", "Highest Common Factor (HCF) by Prime Factorisation & Division", "Lowest Common Multiple (LCM) & Real Life Word Problems"]},
                {"name": "Chapter 4: Basic Geometrical Ideas", "topics": ["Points, Line Segment, Line and Ray", "Intersecting Lines and Parallel Lines", "Curves: Open and Closed Curves, Polygons", "Angles: Vertex, Arms, Interior and Exterior", "Triangles: Vertices, Sides, Angles", "Quadrilaterals: Adjacent and Opposite Sides/Angles", "Circles: Radius, Diameter, Chord, Arc, Sector, Segment, Circumference"]},
                {"name": "Chapter 5: Understanding Elementary Shapes", "topics": ["Measuring Line Segments (Comparison by Ruler and Divider)", "Angles: Right, Straight, Complete, Acute, Obtuse and Reflex", "Measuring Angles with Protractor & Perpendicular Lines", "Classification of Triangles (by Sides and by Angles)", "Quadrilaterals: Trapezium, Parallelogram, Rectangle, Rhombus, Square", "Polygons (Pentagon, Hexagon, Octagon)", "Three Dimensional 3D Shapes (Cube, Cuboid, Cylinder, Cone, Sphere, Prism, Pyramid)"]},
                {"name": "Chapter 6: Integers", "topics": ["Concept of Positive and Negative Numbers in Daily Life", "Representation of Integers on the Number Line", "Ordering and Comparison of Integers", "Addition of Integers using Number Line and Rules", "Subtraction of Integers with Number Line and Additive Inverse"]},
                {"name": "Chapter 7: Fractions", "topics": ["Fraction as Part of a Whole & Part of a Collection", "Representation of Fractions on Number Line", "Proper Fractions, Improper Fractions & Mixed Fractions", "Equivalent Fractions (Simplest Form / Lowest Terms)", "Like and Unlike Fractions & Comparing Fractions", "Addition and Subtraction of Like and Unlike Fractions"]},
                {"name": "Chapter 8: Decimals", "topics": ["Tenths and Hundredths Concept", "Decimals on Number Line & Place Value Chart", "Converting Fractions to Decimals and Decimals to Fractions", "Comparing Decimals", "Using Decimals in Money, Length and Weight", "Addition and Subtraction of Numbers with Decimals"]},
                {"name": "Chapter 9: Data Handling", "topics": ["Recording and Organizing Data using Tally Marks", "Pictograph: Reading and Interpretation", "Drawing Pictographs using Suitable Scale", "Bar Graph: Reading and Interpreting Horizontal/Vertical Bar Graphs", "Drawing Bar Graphs from Given Data"]},
                {"name": "Chapter 10: Mensuration", "topics": ["Perimeter of Closed Figures", "Perimeter of Rectangle and Square (Formulas)", "Perimeter of Regular Polygons (Equilateral Triangle, Regular Hexagon)", "Area Concept & Counting Squares on Grid Paper", "Area of Rectangle and Area of Square"]},
                {"name": "Chapter 11: Algebra", "topics": ["Introduction to Variables using Matchstick Patterns", "Idea of Variable and Algebraic Expressions", "Forming Expressions with Operations (+, -, ×, ÷)", "Translating Word Statements into Algebraic Expressions", "Concept of an Equation (LHS = RHS)", "Solving Equations by Trial and Error Method"]},
                {"name": "Chapter 12: Ratio and Proportion", "topics": ["Concept of Ratio & Simplest Form", "Equivalent Ratios and Comparison", "Concept of Proportion and Extreme/Middle Terms", "Unitary Method: Direct Variation and Word Problems"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Components of Food", "topics": ["Major Nutrients: Carbohydrates, Proteins, Fats, Vitamins, Minerals", "Testing for Starch, Protein and Fat in Food Samples", "Dietary Fibres (Roughage) and Water in Digestion", "Balanced Diet across Different Age Groups", "Deficiency Diseases (Scurvy, Beriberi, Rickets, Anaemia, Goitre, Marasmus, Kwashiorkor)"]},
                {"name": "Chapter 2: Sorting Materials into Groups", "topics": ["Objects Around Us and Materials Used", "Properties of Materials: Lustre / Appearance", "Hardness: Hard vs Soft Materials", "Solubility: Soluble and Insoluble Substances in Water", "Floatation: Objects that Float or Sink in Water", "Transparency: Transparent, Opaque and Translucent Objects"]},
                {"name": "Chapter 3: Separation of Substances", "topics": ["Need for Separation of Substances", "Handpicking, Threshing and Winnowing", "Sieving and Magnetic Separation", "Sedimentation, Decantation and Filtration", "Evaporation and Condensation (Obtaining Common Salt)", "Saturated Solutions and Effect of Temperature on Solubility"]},
                {"name": "Chapter 4: Getting to Know Plants", "topics": ["Classification of Plants: Herbs, Shrubs, Trees, Climbers, Creepers", "Stem: Functions and Conduction of Water/Minerals", "Leaf: Petiole, Lamina, Venation (Reticulate vs Parallel)", "Transpiration and Photosynthesis in Leaves", "Roots: Tap Root vs Fibrous Root, Functions of Roots", "Flower: Sepals, Petals, Stamens (Anther, Filament), Pistil (Stigma, Style, Ovary, Ovules)"]},
                {"name": "Chapter 5: Body Movements", "topics": ["Human Skeleton: Functions, Skull, Backbone, Ribcage, Shoulder and Pelvic Bones", "Cartilage and Muscles (Contraction and Relaxation)", "Types of Joints: Ball and Socket, Hinge, Pivotal, Fixed Joints", "Gait of Animals: Earthworm (Bristles & Muscular Contraction)", "Gait of Animals: Snail, Cockroach, Birds (Streamlined Body & Hollow Bones)", "Gait of Animals: Fish (Fins & Streamlined Shape) and Snakes (Slithering Loops)"]},
                {"name": "Chapter 6: The Living Organisms — Characteristics & Habitats", "topics": ["Organisms and Their Surroundings", "Biotic and Abiotic Components of Environment", "Adaptations in Terrestrial Habitats (Deserts - Camel & Cactus, Mountains - Yak & Pine, Grasslands - Lion & Deer)", "Adaptations in Aquatic Habitats (Oceans, Ponds and Lakes - Water Lily)", "Characteristics of Living Organisms (Nutrition, Respiration, Growth, Excretion, Stimuli Response, Reproduction, Movement)"]},
                {"name": "Chapter 7: Motion and Measurement of Distances", "topics": ["Story of Transport (Ancient to Modern)", "Standard Units of Measurement and SI Unit (Metre)", "Correct Measurement of Length using Ruler & Avoiding Parallax Error", "Measuring the Length of a Curved Line using Thread", "Types of Motion: Rectilinear Motion, Circular Motion, Periodic Motion, Rotational Motion"]},
                {"name": "Chapter 8: Light, Shadows and Reflections", "topics": ["Luminous and Non-luminous Objects", "Opaque, Transparent and Translucent Objects in Light", "Formation and Characteristics of Shadows", "Pinhole Camera: Construction, Working and Image Formation", "Mirrors and Reflection of Light (Periscope Application)"]},
                {"name": "Chapter 9: Electricity and Circuits", "topics": ["Electric Cell: Terminals (+ and -) and Chemical Energy", "Electric Bulb: Filament and Terminals", "Electric Circuit: Closed Circuit vs Open Circuit, Direction of Current Flow", "Electric Switch: Making and Working in Circuit", "Electric Conductors and Insulators (Safety Precautions)"]},
                {"name": "Chapter 10: Fun with Magnets", "topics": ["Discovery of Magnets (Magnes the Shepherd)", "Magnetic and Non-Magnetic Materials", "Poles of a Magnet (North Pole and South Pole)", "Finding Directions with a Freely Suspended Magnetic Needle / Compass", "Making Your Own Magnet (Single Touch Method)", "Attraction and Repulsion Between Magnetic Poles", "Care and Storage of Magnets (Keepers)"]},
                {"name": "Chapter 11: Air Around Us", "topics": ["Presence of Air Everywhere & Wind", "Composition of Air: Nitrogen, Oxygen, Carbon Dioxide, Water Vapour, Dust and Smoke", "Availability of Oxygen to Animals and Plants in Water and Soil", "How Oxygen in Atmosphere is Replaced (Balance by Photosynthesis and Respiration)", "Importance of Atmosphere and Uses of Windmill"]}
            ]
        },
        {
            "name": "Social Science - History (Our Pasts - I)", "color": "#F59E0B",
            "chapters": [
                {"name": "Chapter 1: What, Where, How and When?", "topics": ["Finding Out What Happened in the Past", "Where Did Early People Live (Narmada, Sulaiman, Kirthar, Garo Hills)?", "Names of the Land: Bharat and India", "Finding Out About the Past: Manuscripts and Inscriptions", "Archaeology and Dating: BC, AD, BCE, CE"]},
                {"name": "Chapter 2: From Hunting-Gathering to Growing Food", "topics": ["Hunter-Gatherers: Stone Tools (Palaeolithic, Mesolithic, Neolithic)", "Discovery and Uses of Fire (Kurnool Caves)", "Changing Environment & Beginning of Farming and Herding", "A New Way of Life: Domestication, Storing Animals & Grain", "Finding Out About the First Farmers and Herders (Mehrgarh, Burzahom, Daojali Hading)"]},
                {"name": "Chapter 3: In the Earliest Cities (Harappan Civilisation)", "topics": ["The Story of Harappa & Architecture of Cities (Citadel and Lower Town)", "Special Buildings: The Great Bath at Mohenjo-daro", "Houses, Drains and Planned Streets", "Life in the City: Rulers, Scribes, Crafts Persons", "New Crafts in Harappa: Seal Making, Terracotta Toys, Beads, Copper, Bronze, Gold", "Search for Raw Materials & Agriculture (The Plough)", "Harappan Towns in Gujarat: Dholavira and Lothal & The Mystery of the End"]},
                {"name": "Chapter 4: What Books and Burials Tell Us", "topics": ["One of the Oldest Books in the World: The Vedas (Rigveda, Samaveda, Yajurveda, Atharvaveda)", "Silent Sentinels: The Story of Megaliths (Burials at Inamgaon)", "Social Differences in Burials & Occupations at Inamgaon"]},
                {"name": "Chapter 5: Kingdoms, Kings and an Early Republic", "topics": ["How Some Men Became Rulers: Ashvamedha Sacrifice", "The Varna System (Brahmins, Kshatriyas, Vaishyas, Shudras)", "Janapadas to Mahajanapadas (Fortification & Armies)", "Taxes: Taxes on Crops (Bhaga), Crafts, Trade, Herders", "Changes in Agriculture: Iron Ploughshares & Paddy Transplantation", "Magadha: A Powerful Mahajanapada & Vajji: A Gana/Sangha Republic"]},
                {"name": "Chapter 6: New Questions and Ideas (Buddhism & Jainism)", "topics": ["The Story of the Buddha (Gautama): Enlightenment, Teachings, Kisagotami Story", "Upanishads: Soul (Atman) and Universal Soul (Brahman), Gargi and Satyakama Jabala", "Jainism: Vardhamana Mahavira, Teachings, Ahimsa, Followers", "The Sangha & Monasteries (Viharas)"]},
                {"name": "Chapter 7: Ashoka, The Emperor Who Gave Up War", "topics": ["A Very Big Kingdom: An Empire (Empires vs Kingdoms)", "Ruling the Empire: Pataliputra, Taxila, Ujjain, Tribute vs Taxes", "Ashoka: A Unique Ruler & The Kalinga War Transformation", "Ashoka's Dhamma: Messages, Officials (Dhamma Mahamatta), Edicts and Inscriptions"]},
                {"name": "Chapter 8: Vital Villages, Thriving Towns", "topics": ["Iron Tools and Agriculture: Increased Production & Irrigation Works", "Who Lived in the Villages (Vellalar, Uzhavar, Kadaisiyar in Tamil Nadu; Gramabhojaka in North)", "Finding Out About Cities: Jatakas, Sculpture, Archaeological Ring Wells", "Coins: Punch-Marked Coins & Mathura as an Important Center", "Crafts and Crafts Persons: Shrenis (Guilds) & Arikamedu Port Town"]},
                {"name": "Chapter 9: Traders, Kings and Pilgrims", "topics": ["How to Find Out About Trade and Traders (Black Pottery, South Indian Spices, Silk Route)", "The Story of the Silk Route & The Kushanas (Kanishka)", "The Spread of Buddhism: Mahayana Buddhism & Bodhisattvas", "Pilgrims from China: Fa Xian, Xuan Zang, I-Qing", "The Beginning of Bhakti: Meaning, Deities (Shiva, Vishnu, Durga) & Bhagavad Gita"]},
                {"name": "Chapter 10: New Empires and Kingdoms & Cultural Heritage", "topics": ["Prashastis: Samudragupta's Prashasti (Allahabad Pillar / Prayag Prashasti)", "Genealogies: The Guptas & Chandragupta II (Vikramaditya)", "Harshavardhana and the Harshacharita (Banabhatta)", "The Pallavas, Chalukyas and Pulakeshin II", "Administration of Kingdoms & New Kinds of Armies", "Buildings, Paintings and Books: Iron Pillar at Mehrauli, Stupas, Cave Paintings at Ajanta, Epics (Silappadikaram, Manimekalai), Aryabhata"]}
            ]
        },
        {
            "name": "Social Science - Geography (The Earth Our Habitat)", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: The Earth in the Solar System", "topics": ["Full Moon (Poornima) & New Moon (Amavasya)", "Celestial Bodies, Stars and Constellations (Ursa Major, Saptarishi, Pole Star)", "The Solar System: Sun, Planets, Order of Planets, Terrestrial vs Gas Giants", "The Earth: The Blue Planet and Unique Features Supporting Life", "The Moon: Phases, Conditions on Moon & Satellites (Natural and Artificial)", "Asteroids and Meteoroids & The Milky Way Galaxy"]},
                {"name": "Chapter 2: Globe: Latitudes and Longitudes", "topics": ["Globe as a True Model of Earth & Axis and Poles", "Equator and Parallels of Latitudes", "Important Parallels: Tropic of Cancer, Tropic of Capricorn, Arctic Circle, Antarctic Circle", "Heat Zones of the Earth: Torrid Zone, Temperate Zones, Frigid Zones", "Meridians of Longitude & Prime Meridian (Greenwich)", "Longitude and Time Calculation & Indian Standard Time (IST - 82°30'E)"]},
                {"name": "Chapter 3: Motions of the Earth", "topics": ["Rotation of Earth: Orbital Plane, Circle of Illumination, Day and Night", "Revolution of Earth: Leap Year & Orbit (365 ¼ Days)", "Inclination of Earth's Axis & Changes of Seasons", "Summer Solstice (June 21) & Winter Solstice (December 22)", "Equinox (March 21 & September 23)"]},
                {"name": "Chapter 4: Maps", "topics": ["Types of Maps: Physical Maps, Political Maps, Thematic Maps", "Components of Maps: Distance and Scale (Small Scale vs Large Scale Maps)", "Direction: Cardinal Points (N, S, E, W) & Intermediate Directions, The Compass", "Symbols and Conventional Colours used in Maps", "Sketch and Plan: Differences and Uses"]},
                {"name": "Chapter 5: Major Domains of the Earth", "topics": ["Lithosphere: Continents (Asia, Europe, Africa, North America, South America, Australia, Antarctica)", "Hydrosphere: Oceans (Pacific, Atlantic, Indian, Southern, Arctic Ocean)", "Atmosphere: Layers of Atmosphere (Troposphere, Stratosphere, Mesosphere, Thermosphere, Exosphere)", "Composition of Atmosphere: Nitrogen, Oxygen and other gases", "Biosphere: The Domain of Life & Global Warming Effects"]},
                {"name": "Chapter 6: Our Country — India", "topics": ["Geographical Location, Latitudinal and Longitudinal Extent of India", "India's Neighbours (Land and Sea Boundaries)", "Political and Administrative Divisions (States and Union Territories)", "Physical Divisions: The Great Himalayas (Himadri, Himachal, Shiwalik)", "Northern Indian Plains, Great Indian Desert (Thar), Peninsular Plateau (Western & Eastern Ghats)", "Coastal Plains (Western vs Eastern) and Island Groups (Lakshadweep and Andaman & Nicobar)"]}
            ]
        },
        {
            "name": "Social Science - Civics (Social & Political Life - I)", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Understanding Diversity", "topics": ["Concept of Diversity in Languages, Food, Festivals, Religions", "Diversity in Daily Life: Samir Ek and Samir Do Story", "Historical and Geographical Factors Influencing Diversity", "Case Study: Ladakh (Cold Desert, Pashmina Wool, Caravans)", "Case Study: Kerala (Spices, St. Thomas, Ibn Battuta, Chinese Fishing Nets)", "Unity in Diversity: Freedom Struggle and National Anthem"]},
                {"name": "Chapter 2: Diversity and Discrimination", "topics": ["Difference and Prejudice", "Creating Stereotypes (Gender Stereotypes & societal expectations)", "Inequality and Discrimination: Dr. B.R. Ambedkar's Experience at Koregaon", "Caste-based Discrimination & Dalits (Untouchability)", "Striving for Equality: Preamble & Constitutional Safeguards for Minorities"]},
                {"name": "Chapter 3: What is Government?", "topics": ["Definition and Need for a Government", "Levels of Government: Local Level, State Level, National Level", "Laws and the Government: Power to Make and Enforce Decisions", "Types of Government: Democratic Government vs Monarchy", "Democratic Governments: Representative Democracy, Universal Adult Franchise, Women's Suffrage Movement"]},
                {"name": "Chapter 4: Key Elements of a Democratic Government", "topics": ["Apartheid System in South Africa: Hector Pieterson Story & Nelson Mandela's Victory", "Participation of People: Elections and Voting", "Other Ways of Participating: Rallies, Strikes, Signature Campaigns, Media", "Need to Resolve Conflict: Rivers as source of conflict (Cauvery Water Dispute)", "Equality and Justice: Untouchability ban & Affirmative action"]},
                {"name": "Chapter 5: Panchayati Raj", "topics": ["Gram Sabha: Composition, Meeting, Role in Checking Gram Panchayat", "The Gram Panchayat: Ward Members (Panchs), Sarpanch, Secretary", "Functions and Sources of Funds of Gram Panchayat", "Three Levels of Panchayats: Gram Panchayat, Panchayat Samiti (Block Level), Zilla Parishad (District Level)"]},
                {"name": "Chapter 6: Rural Administration", "topics": ["Maintaining Law and Order in Villages: Police Station and SHO", "Maintenance of Land Records: The Patwari (Lekhpal/Karnam) & Khasra Record", "Revenue Department: Tehsildar and District Collector", "A New Law: Hindu Succession Amendment Act (2005) - Equal rights for women in agricultural land"]},
                {"name": "Chapter 7: Urban Administration", "topics": ["City Life vs Village Life & Need for Municipal Administration", "The Municipal Corporation (Mahanagarpalika) & Municipal Council", "The Ward Councillor and Administrative Staff (Commissioner)", "How Municipal Corporations Get Money (Property Tax, Water Tax, Entertainment Tax)", "Community Protest: Gangabai's Story on Garbage Collection"]},
                {"name": "Chapter 8: Rural and Urban Livelihoods", "topics": ["Livelihoods in Kalpattu Village: Farming, Agricultural Labourers (Thulasi), Small Farmers (Sekar), Big Farmers (Ramalingam)", "Debt Cycle of Farmers and Fisherman Life in Pudupet", "Livelihoods in the City: Street Workers, Vendors and Hawkers", "In the Market: Permanent Shops, Showrooms, Businesspersons", "In the Factory-Workshop Area: Casual Labourers and Labour Chowk", "In the Office: Regular and Permanent Workers (Call Centers, Government Offices)"]}
            ]
        },
        {
            "name": "English", "color": "#0284C7",
            "chapters": [
                {
                    "name": "Unit 1: Honeysuckle (Prose & Poetry)",
                    "topics": [
                        "Who Did Patrick's Homework? (Prose) & A House, A Home (Poem)",
                        "How the Dog Found Himself a New Master! (Prose) & The Kite (Poem)",
                        "Taro's Reward (Prose) & The Quarrel (Poem)",
                        "An Indian - American Woman in Space: Kalpana Chawla (Prose) & Beauty (Poem)",
                        "A Different Kind of School (Prose) & Where Do All the Teachers Go? (Poem)",
                        "Who I Am (Prose) & The Wonderful Words (Poem)",
                        "Fair Play (Prose by Premchand)",
                        "The Banyan Tree (Prose by Ruskin Bond) & Vocation (Poem)"
                    ]
                },
                {
                    "name": "Unit 2: A Pact with the Sun (Supplementary Reader)",
                    "topics": [
                        "A Tale of Two Birds (Story & Moral)",
                        "The Friendly Mongoose (Panchatantra Story)",
                        "The Shepherd's Treasure (Iranian Folktale)",
                        "Tansen (Life and Musical Mastery of Tansen)",
                        "The Monkey and the Crocodile (Panchatantra Story)",
                        "The Wonder Called Sleep (Biological Benefits of Sleep)",
                        "A Pact with the Sun (Saeeda's Story & Sunshine)",
                        "What Happened to the Reptiles (Pambupatti Tale of Harmony)"
                    ]
                },
                {
                    "name": "Unit 3: English Grammar & Composition",
                    "topics": [
                        "Nouns: Common, Proper, Collective, Abstract Nouns & Gender/Number",
                        "Pronouns: Personal, Possessive, Demonstrative, Relative Pronouns",
                        "Verbs: Main Verbs, Helping Verbs, Transitive and Intransitive Verbs",
                        "Tenses: Simple Present, Present Continuous, Simple Past, Past Continuous, Simple Future",
                        "Adjectives: Degrees of Comparison (Positive, Comparative, Superlative)",
                        "Adverbs: Adverbs of Manner, Time, Place and Frequency",
                        "Prepositions of Time and Place (in, on, at, under, behind)",
                        "Conjunctions: Coordinating (and, but, or, so) & Subordinating (because, although)",
                        "Punctuation & Capitalization Rules",
                        "Reading Comprehension: Unseen Prose and Poetry Passages",
                        "Writing Skills: Paragraph Writing, Story Writing with Outlines",
                        "Writing Skills: Notice Writing and Formal/Informal Letter Writing"
                    ]
                }
            ]
        },
        {
            "name": "Hindi (हिन्दी)", "color": "#E11D48",
            "chapters": [
                {
                    "name": "Chapter 1: वसंत भाग-1 (गद्य एवं पद्य भाग)",
                    "topics": [
                        "वह चिड़िया जो (कविता - केदारनाथ अग्रवाल)",
                        "बचपन (संस्मरण - कृष्णा सोबती)",
                        "नादान दोस्त (कहानी - मुंशी प्रेमचंद)",
                        "चाँद से थोड़ी सी गप्पें (कविता - शमशेर बहादुर सिंह)",
                        "साथी हाथ बढ़ाना (गीत - साहिर लुधियानवी)",
                        "ऐसे-ऐसे (एकांकी - विष्णु प्रभाकर)",
                        "टिकट अलबम (कहानी - सुंदरा रामस्वामी)",
                        "झाँसी की रानी (कविता - सुभद्रा कुमारी चौहान)",
                        "जो देखकर भी नहीं देखते (निबंध - हेलेन केलर)",
                        "संसार पुस्तक है (पत्र - पं. जवाहरलाल नेहरू)",
                        "मैं सबसे छोटी होऊँ (कविता - सुमित्रानंदन पंत)",
                        "लोकगीत (निबंध - भगवतशरण उपाध्याय)",
                        "नौकर (निबंध - अनुबंधोपाध्याय)",
                        "वन के मार्ग में (सवैया - तुलसीदास)",
                        "साँस-साँस में बाँस (निबंध - एलेक्स एम जॉर्ज)"
                    ]
                },
                {
                    "name": "Chapter 2: बाल रामकथा (पूरक पाठ्यपुस्तक)",
                    "topics": [
                        "अवधपुरी में राम (दशरथ, ऋषि विश्वामित्र व बालकांड)",
                        "जंगल और जनकपुर (ताड़का वध व धनुष भंग)",
                        "दो वरदान (मंथरा की कुटिलता व कैकेयी के वरदान)",
                        "राम का वन गमन (राम, सीता और लक्ष्मण का प्रस्थान)",
                        "चित्रकूट में भरत (भरत मिलाप व पादुका स्थापना)",
                        "दंडक वन में दस वर्ष व शूर्पणखा प्रसंग",
                        "सोने का हिरण (मारीच वध व सीता हरण)",
                        "सीता की खोज (जटायु व शबरी से भेंट)",
                        "राम और सुग्रीव (किष्किंधा कांड व बालि वध)",
                        "लंका में हनुमान (समुद्र लंघन व अशोक वाटिका)",
                        "लंका विजय (सेतु निर्माण व रावण वध)",
                        "राम का राज्याभिषेक (अयोध्या वापसी)"
                    ]
                },
                {
                    "name": "Chapter 3: हिन्दी व्याकरण एवं रचना (Grammar & Writing)",
                    "topics": [
                        "भाषा, लिपि और व्याकरण परिचय",
                        "वर्ण विचार: स्वर, व्यंजन, अनुस्वार व अनुनासिक",
                        "संज्ञा एवं संज्ञा के भेद (व्यक्तिवाचक, जातिवाचक, भाववाचक)",
                        "लिंग (पुल्लिंग, स्त्रीलिंग) एवं वचन (एकवचन, बहुवचन)",
                        "कारक एवं कारक के भेद (परसर्ग / विभक्ति चिन्ह)",
                        "सर्वनाम एवं सर्वनाम के छह भेद",
                        "विशेषण एवं विशेषण के चार भेद",
                        "क्रिया (सकर्मक, अकर्मक) एवं काल (वर्तमान, भूत, भविष्य)",
                        "विलोम शब्द एवं पर्यायवाची शब्द (समानार्थी)",
                        "अनेक शब्दों के लिए एक शब्द एवं समरूपी भिन्नार्थक शब्द",
                        "मुहावरे: अर्थ एवं वाक्य प्रयोग",
                        "अपठित गद्यांश बोध एवं प्रश्नोत्तर",
                        "पत्र लेखन (औपचारिक - अवकाश/प्रार्थना पत्र, अनौपचारिक पत्र)",
                        "अनुच्छेद / निबंध लेखन एवं संवाद लेखन"
                    ]
                }
            ]
        },
        {
            "name": "Computer Science & IT Basics", "color": "#14B8A6",
            "chapters": [
                {"name": "Chapter 1: Computer Fundamentals & Architecture", "topics": ["What is a Computer: IPO Cycle (Input - Process - Output)", "Hardware vs Software: System Software and Application Software", "Input Devices: Keyboard, Mouse, Scanner, Web Camera, Barcode Reader", "Output Devices: Monitor (LED/LCD), Printers (Laser, Inkjet), Speakers", "Storage Devices: Primary Memory (RAM, ROM) & Secondary Memory (HDD, SSD, Pen Drive, Cloud)"]},
                {"name": "Chapter 2: Operating Systems & GUI", "topics": ["Role of Operating System (Windows / Linux / macOS / Android)", "Windows GUI Interface: Desktop, Taskbar, Start Menu, File Explorer", "Managing Files and Folders (Create, Rename, Copy, Move, Delete)", "Recycle Bin and Storage Management"]},
                {"name": "Chapter 3: Word Processing Skills (MS Word / Docs)", "topics": ["Creating, Opening, Saving and Exporting Documents (PDF)", "Text Formatting: Font, Size, Color, Bold, Italic, Underline, Highlighting", "Paragraph Formatting: Alignment, Line Spacing, Bullets and Numbering", "Inserting Images, Shapes, SmartArt and Tables", "Page Setup: Margins, Orientation, Headers, Footers, Page Numbers, Print Preview"]},
                {"name": "Chapter 4: Presentation & Digital Storytelling (MS PowerPoint / Slides)", "topics": ["Introduction to Presentation Software & Slide Layouts", "Adding Text, Bullet Points and Formatting Slide Content", "Inserting Images, Audio, Video and Diagrams", "Applying Slide Themes, Background Styles and Color Palettes", "Slide Transitions and Custom Animations", "Running a Slide Show (F5, Presenter View)"]},
                {"name": "Chapter 5: Visual Coding & Computational Thinking (Scratch / Blockly)", "topics": ["Introduction to Algorithms & Step-by-Step Problem Solving", "Scratch Interface: Stage, Sprite, Blocks Palette, Scripts Area", "Motion Blocks: Moving and Turning Sprites", "Looks and Sound Blocks: Costumes, Speech Bubbles, Sound Effects", "Events and Control Blocks: When Green Flag Clicked, Repeat Loops, If-Then Conditions", "Creating an Interactive Animation and Mini-Game in Scratch"]},
                {"name": "Chapter 6: Internet, Cyber Safety & Ethics", "topics": ["What is the Internet: WWW, Web Browser, Search Engines", "Effective Web Searching Techniques and Keywords", "Email Basics: Composing, Sending, Attachments and Netiquette", "Cyber Safety: Strong Passwords, Protecting Personal Information", "Recognizing Scams: Phishing, Viruses, Fake Links & Safe Downloading", "Digital Footprint and Responsible Social Behavior"]}
            ]
        }
    ],

    ("CBSE", "Class 7"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Integers", "topics": ["Properties of Addition & Subtraction", "Multiplication of Integers", "Division of Integers", "Word Problems"]},
                {"name": "Chapter 2: Fractions and Decimals", "topics": ["Multiplication of Fractions", "Division of Fractions", "Multiplication of Decimals", "Division of Decimals"]},
                {"name": "Chapter 3: Simple Equations & Lines and Angles", "topics": ["Setting Up Equations", "Solving Equations", "Complementary & Supplementary Angles", "Parallel Lines & Transversal"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Nutrition in Plants & Animals", "topics": ["Mode of Nutrition & Photosynthesis", "Other Modes of Plant Nutrition", "Human Digestive System", "Digestion in Grass-eating Animals"]},
                {"name": "Chapter 2: Heat & Acids, Bases and Salts", "topics": ["Measuring Temperature & Thermometer", "Conduction, Convection, Radiation", "Indicators & Neutralisation", "Salts in Daily Life"]}
            ]
        },
        {
            "name": "Social Science", "color": "#F59E0B",
            "chapters": [
                {"name": "History: Tracing Changes Through a Thousand Years", "topics": ["New and Old Terminologies", "Historians and Their Sources", "New Social and Political Groups", "Regions and Empires"]},
                {"name": "Geography: Our Environment", "topics": ["Components of Environment", "Natural Environment: Lithosphere, Hydrosphere, Atmosphere, Biosphere", "Ecosystem & Human Environment"]},
                {"name": "Civics: On Equality", "topics": ["Equal Right to Vote", "Other Kinds of Equality", "Equality in Indian Democracy", "Midday Meal Scheme"]}
            ]
        }
    ],

    ("CBSE", "Class 8"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Rational Numbers", "topics": ["Closure & Commutative Property", "Associative & Distributive Property", "Representation on Number Line", "Rational Numbers Between Two Rational Numbers"]},
                {"name": "Chapter 2: Linear Equations in One Variable", "topics": ["Solving Equations with Variables on One Side", "Variables on Both Sides", "Reducing Equations to Simpler Form", "Word Problems"]},
                {"name": "Chapter 3: Squares, Square Roots, Cubes & Cube Roots", "topics": ["Properties of Square Numbers", "Prime Factorisation & Long Division", "Cube Numbers & Prime Factorisation", "Estimation of Roots"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Crop Production and Management", "topics": ["Agricultural Practices", "Basic Practices of Crop Production", "Irrigation & Protection from Weeds", "Harvesting & Storage"]},
                {"name": "Chapter 2: Microorganisms: Friend and Foe", "topics": ["Types of Microorganisms", "Commercial & Medicinal Use", "Harmful Microorganisms & Pathogens", "Food Preservation & Nitrogen Cycle"]}
            ]
        },
        {
            "name": "Social Science", "color": "#F59E0B",
            "chapters": [
                {"name": "History: How, When and Where", "topics": ["How Important are Dates?", "Which Dates?", "How Do We Periodise?", "What is Colonial?"]},
                {"name": "Geography: Resources", "topics": ["Types of Resources: Natural, Human Made, Human", "Conserving Resources & Sustainable Development"]},
                {"name": "Civics: The Indian Constitution", "topics": ["Why Does a Country Need a Constitution?", "Key Features of the Indian Constitution", "Secularism in India"]}
            ]
        }
    ],

    ("CBSE", "Class 9"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Number Systems", "topics": ["Irrational Numbers & Real Numbers", "Real Numbers and Their Decimal Expansions", "Representing Real Numbers on Number Line", "Operations on Real Numbers & Laws of Exponents"]},
                {"name": "Chapter 2: Polynomials", "topics": ["Polynomials in One Variable", "Zeros of a Polynomial", "Remainder Theorem & Factor Theorem", "Algebraic Identities"]},
                {"name": "Chapter 3: Coordinate Geometry & Linear Equations", "topics": ["Cartesian System & Plotting Points", "Linear Equations in Two Variables", "Graph of Linear Equation in Two Variables", "Equations of Lines Parallel to X/Y Axes"]},
                {"name": "Chapter 4: Lines, Angles & Triangles", "topics": ["Basic Terms & Definitions", "Intersecting Lines & Parallel Lines", "Angle Sum Property of Triangle", "Congruence of Triangles & Criteria (SAS, ASA, SSS, RHS)"]},
                {"name": "Chapter 5: Surface Areas, Volumes & Statistics", "topics": ["Surface Area of Cone & Sphere", "Volume of Cone & Sphere", "Graphical Representation of Data (Bar Graphs, Histograms)", "Mean, Median & Mode"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Physics: Motion & Force", "topics": ["Distance & Displacement", "Speed, Velocity & Acceleration", "Equations of Motion", "Newton's Laws of Motion & Momentum"]},
                {"name": "Physics: Gravitation & Work-Energy", "topics": ["Universal Law of Gravitation", "Free Fall & Acceleration due to Gravity", "Work Done by a Force", "Kinetic Energy & Potential Energy"]},
                {"name": "Chemistry: Matter & Atoms", "topics": ["Physical Nature of Matter", "States of Matter & Change of State", "Law of Chemical Combination", "Dalton's Atomic Theory & Mole Concept"]},
                {"name": "Biology: Cell & Tissues", "topics": ["Cell Structure & Plasma Membrane", "Nucleus & Cell Organelles", "Plant Tissues (Meristematic & Permanent)", "Animal Tissues (Epithelial, Connective, Muscular, Nervous)"]}
            ]
        },
        {
            "name": "Social Science", "color": "#F59E0B",
            "chapters": [
                {"name": "History: The French Revolution", "topics": ["French Society During Late 18th Century", "Outbreak of the Revolution", "France Abolishes Monarchy", "Women's Revolution & Abolition of Slavery"]},
                {"name": "Geography: India - Size and Location", "topics": ["Location and Size", "India and the World", "India's Neighbors", "Physiographic Divisions of India"]},
                {"name": "Pol Science: What is Democracy?", "topics": ["Features of Democracy", "Why Democracy?", "Broader Meanings of Democracy", "Constitutional Design"]}
            ]
        }
    ],

    ("CBSE", "Class 10"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Real Numbers & Polynomials", "topics": ["Euclid's Division Lemma & Fundamental Theorem of Arithmetic", "Revisiting Irrational Numbers & Decimals", "Zeros of Polynomial & Coefficient Relationship", "Division Algorithm for Polynomials"]},
                {"name": "Chapter 2: Pair of Linear Equations in Two Variables", "topics": ["Graphical Method of Solution", "Algebraic Methods (Substitution, Elimination)", "Cross-Multiplication Method", "Equations Reducible to Linear Form"]},
                {"name": "Chapter 3: Quadratic Equations & Arithmetic Progressions", "topics": ["Standard Form & Solution by Factoring", "Completing the Square & Quadratic Formula", "Nature of Roots", "nth Term & Sum of First n Terms of AP"]},
                {"name": "Chapter 4: Triangles & Coordinate Geometry", "topics": ["Similar Figures & Basic Proportionality Theorem (Thales)", "Criteria for Similarity of Triangles (AAA, SAS, SSS)", "Distance Formula & Section Formula", "Area of a Triangle"]},
                {"name": "Chapter 5: Introduction to Trigonometry & Applications", "topics": ["Trigonometric Ratios & Specific Angles (0, 30, 45, 60, 90)", "Trigonometric Identities", "Heights and Distances", "Angle of Elevation & Depression"]},
                {"name": "Chapter 6: Circles, Surface Areas & Statistics", "topics": ["Tangent to a Circle & Theorems", "Surface Area & Volume of Combination of Solids", "Frustum of a Cone", "Mean, Median, Mode & Ogive Graphs"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Light - Reflection and Refraction", "topics": ["Spherical Mirrors & Mirror Formula", "Refraction & Snell's Law", "Refraction through Lenses & Lens Formula", "Power of a Lens"]},
                {"name": "Chapter 2: Human Eye and Colorful World", "topics": ["Structure of Human Eye & Defects of Vision", "Refraction through a Prism", "Dispersion of White Light", "Atmospheric Refraction & Scattering of Light"]},
                {"name": "Chapter 3: Electricity & Magnetic Effects", "topics": ["Electric Current, Potential Difference & Ohm's Law", "Resistance & Factors Affecting Resistance", "Heating Effect of Electric Current & Joule's Law", "Magnetic Field, Field Lines & Solenoid", "Fleming's Left Hand Rule & Electric Motor", "Electromagnetic Induction & Generator"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Chemical Reactions and Equations", "topics": ["Chemical Equations & Balancing", "Types of Chemical Reactions", "Corrosion and Rancidity"]},
                {"name": "Chapter 2: Acids, Bases and Salts", "topics": ["Chemical Properties of Acids & Bases", "pH Scale & Importance in Daily Life", "Preparation & Uses of Salts (Bleaching Powder, Baking Soda, Plaster of Paris)"]},
                {"name": "Chapter 3: Carbon and Its Compounds", "topics": ["Covalent Bonding in Carbon", "Versatile Nature of Carbon & Homologous Series", "Nomenclature & Chemical Properties of Carbon Compounds", "Ethanol, Ethanoic Acid, Soaps & Detergents"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Life Processes", "topics": ["Autotrophic & Heterotrophic Nutrition", "Respiration in Plants & Humans", "Transportation in Humans & Plants", "Excretion in Humans & Plants"]},
                {"name": "Chapter 2: Control and Coordination & Reproduction", "topics": ["Nervous System & Reflex Action", "Hormones in Plants & Animals", "Asexual & Sexual Reproduction", "Human Reproductive System & Reproductive Health"]}
            ]
        },
        {
            "name": "Social Science", "color": "#F59E0B",
            "chapters": [
                {"name": "History: Nationalism in India & Europe", "topics": ["Rise of Nationalism in Europe", "First World War, Khilafat & Non-Cooperation", "Differing Strands within Movement", "Towards Civil Disobedience", "Sense of Collective Belonging"]},
                {"name": "Geography: Resources, Agriculture & Minerals", "topics": ["Types of Resources & Development", "Forest and Wildlife Resources", "Water Resources & Dams", "Types of Farming & Major Crops", "Minerals and Energy Resources", "Manufacturing Industries & Lifelines of National Economy"]},
                {"name": "Pol Science: Democracy & Governance", "topics": ["Power Sharing (Belgium and Sri Lanka Models)", "Federalism in India", "Gender, Religion and Caste", "Political Parties & Outcomes of Democracy"]}
            ]
        },
        {
            "name": "English", "color": "#0284C7",
            "chapters": [
                {"name": "First Flight: Prose & Poetry", "topics": ["A Letter to God & Dust of Snow", "Nelson Mandela: Long Walk to Freedom", "Two Stories About Flying", "From the Diary of Anne Frank", "Glimpses of India & The Trees", "Madam Rides the Bus & Fog", "The Sermon at Benares & For Anne Gregory", "The Proposal (Play)"]},
                {"name": "Footprints Without Feet: Supplementary", "topics": ["A Triumph of Surgery", "The Thief's Story", "The Midnight Visitor", "A Question of Trust", "Footprints Without Feet", "The Making of a Scientist", "The Necklace & Bholi"]},
                {"name": "Grammar & Creative Writing", "topics": ["Tenses, Modals & Subject-Verb Concord", "Reported Speech (Commands, Statements, Questions)", "Formal Letter Writing (Editor, Complaint, Inquiry)", "Analytical Paragraph Writing based on charts/data"]}
            ]
        }
    ]
}


def normalize_class_name(raw_class: str) -> str:
    """Normalize class string to matching key format like 'Class 10'."""
    s = str(raw_class).strip().lower()
    # Check 10 first to avoid matching '1'
    if "10" in s or "class 10" in s or "class10" in s or s == "x":
        return "Class 10"
    for num in range(9, 0, -1):
        if f"class {num}" in s or f"class{num}" in s or s == str(num):
            return f"Class {num}"
    if "ix" in s or "9" in s:
        return "Class 9"
    if "viii" in s or "8" in s:
        return "Class 8"
    if "vii" in s or "7" in s:
        return "Class 7"
    if "vi" in s or "6" in s:
        return "Class 6"
    if "v" in s or "5" in s:
        return "Class 5"
    if "iv" in s or "4" in s:
        return "Class 4"
    if "iii" in s or "3" in s:
        return "Class 3"
    if "ii" in s or "2" in s:
        return "Class 2"
    if "i" in s or "1" in s:
        return "Class 1"
    return "Class 10"


def preload_standard_syllabus(user_id: int, board: str, class_name: str) -> bool:
    """
    Looks up standard syllabus data for (board, class_name) and bulk-creates all
    subjects, chapters, and topics in the database for the given user_id.

    Returns True if data was successfully loaded, False otherwise.
    """
    board_clean = "ICSE" if "ICSE" in str(board).upper() else "CBSE"
    norm_class = normalize_class_name(class_name)
    
    # Try exact match first
    syllabus_list = SYLLABUS_DATA.get((board_clean, norm_class))

    # Fallback to Class 10 if specific class key isn't explicitly defined
    if not syllabus_list:
        syllabus_list = SYLLABUS_DATA.get((board_clean, "Class 10"))

    if not syllabus_list:
        return False

    success = bulk_create_syllabus(user_id, syllabus_list)
    if success:
        try:
            from preloaded_formulas import seed_user_canonical_formulas
            seed_user_canonical_formulas(user_id)
        except Exception:
            pass
    return success


def reload_and_replace_syllabus(user_id: int, board: str, class_name: str) -> bool:
    """
    Completely replaces a student's syllabus with the official curriculum for (board, class_name).
    Clears all existing subjects/chapters/topics for this user first, then bulk loads the new syllabus.
    """
    from models import clear_user_syllabus
    clear_user_syllabus(user_id)
    return preload_standard_syllabus(user_id, board, class_name)



