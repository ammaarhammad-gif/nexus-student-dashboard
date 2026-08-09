"""
preloaded_syllabi.py — Comprehensive CBSE and ICSE syllabus datastore for Classes 1 to 10.

Automatically populates subjects, chapters, and topics for students so they don't
have to type anything manually — all they need to do is tick off topics as they study.
"""

from models import add_subject, add_chapter, add_topic, get_subject_by_name, get_chapters_for_subject

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
                {"name": "Chapter 1: Knowing Our Numbers", "topics": ["Comparing Numbers", "Large Numbers in Practice", "Indian & International System", "Estimation & Rounding Off"]},
                {"name": "Chapter 2: Whole Numbers & Playing with Numbers", "topics": ["Properties of Whole Numbers", "Factors & Multiples", "Prime & Composite Numbers", "HCF and LCM"]},
                {"name": "Chapter 3: Basic Geometrical Ideas & Integers", "topics": ["Points, Lines & Rays", "Angles, Triangles & Quadrilaterals", "Integers on Number Line", "Addition & Subtraction of Integers"]},
                {"name": "Chapter 4: Fractions, Decimals & Algebra", "topics": ["Types of Fractions", "Decimal Numbers & Conversion", "Introduction to Variables", "Algebraic Equations"]}
            ]
        },
        {
            "name": "Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Components of Food", "topics": ["Carbohydrates, Proteins, Fats", "Vitamins & Minerals", "Balanced Diet", "Deficiency Diseases"]},
                {"name": "Chapter 2: Sorting Materials into Groups", "topics": ["Appearance & Hardness", "Solubility in Water", "Transparency, Translucency & Opacity", "Floatation"]},
                {"name": "Chapter 3: Separation of Substances", "topics": ["Handpicking, Threshing, Winnowing", "Sieving & Magnetic Separation", "Sedimentation, Decantation & Filtration", "Evaporation & Saturation"]},
                {"name": "Chapter 4: Getting to Know Plants & Body Movements", "topics": ["Herbs, Shrubs, Trees", "Root System & Shoot System", "Leaf Structure & Transpiration", "Human Skeleton & Joints"]}
            ]
        },
        {
            "name": "Social Science", "color": "#F59E0B",
            "chapters": [
                {"name": "History: What, Where, How and When?", "topics": ["Finding Out What Happened", "Where Did People Live?", "Names of the Land", "Dates & Manuscripts"]},
                {"name": "Geography: The Earth in the Solar System", "topics": ["Celestial Bodies & Stars", "The Solar System & Planets", "Earth & Moon", "Asteroids & Meteoroids"]},
                {"name": "Civics: Understanding Diversity", "topics": ["Concept of Diversity", "Diversity in India", "Unity in Diversity", "Inequality vs Diversity"]}
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
    Looks up standard syllabus data for (board, class_name) and creates all
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

    # Insert subjects, chapters, and topics
    for sub_data in syllabus_list:
        sub_id = add_subject(user_id, sub_data["name"], sub_data.get("color", "#6366F1"))
        if sub_id is None:
            existing_sub = get_subject_by_name(user_id, sub_data["name"])
            if existing_sub:
                sub_id = existing_sub["id"]

        if sub_id is None:
            continue

        existing_chapters = get_chapters_for_subject(user_id, sub_id)
        if existing_chapters:
            # Chapters already exist for this subject, skip creating duplicates
            continue

        for chap_data in sub_data.get("chapters", []):
            chap_id = add_chapter(user_id, sub_id, chap_data["name"])
            for topic_name in chap_data.get("topics", []):
                add_topic(user_id, chap_id, topic_name)

    return True
