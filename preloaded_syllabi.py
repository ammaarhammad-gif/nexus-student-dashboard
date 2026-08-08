"""
preloaded_syllabi.py — Standard CBSE and ICSE syllabus data loader for Classes 1 to 10.

Automatically populates subjects, chapters, and topics for students so they don't
have to type their syllabus manually.
"""

# ══════════════════════════════════════════════════════════════════════════════
# SYLLABUS DATASTORE FOR CBSE AND ICSE (CLASSES 1 to 10)
# ══════════════════════════════════════════════════════════════════════════════

SYLLABUS_DATA = {
    # ──────────────────────────────────────────────────────────────────────────
    # CBSE SYLLABUS DATA (CLASSES 1 to 10)
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
                {"name": "History: Nationalism in India", "topics": ["First World War, Khilafat & Non-Cooperation", "Differing Strands within Movement", "Towards Civil Disobedience", "Sense of Collective Belonging"]},
                {"name": "Geography: Resources & Agriculture", "topics": ["Types of Resources & Development", "Forest and Wildlife Resources", "Water Resources & Dams", "Types of Farming & Major Crops"]},
                {"name": "Pol Science: Power Sharing & Federalism", "topics": ["Belgium and Sri Lanka Models", "Why Power Sharing is Desirable", "What is Federalism?", "Decentralisation in India"]}
            ]
        }
    ],

    # ──────────────────────────────────────────────────────────────────────────
    # ICSE SYLLABUS DATA (CLASSES 1 to 10)
    # ──────────────────────────────────────────────────────────────────────────
    ("ICSE", "Class 1"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Pre-Number Concepts & Numbers 1-100", "topics": ["Big/Small & Tall/Short", "Top/Bottom & Above/Below", "Counting & Number Names 1-100", "Place Value (Tens and Ones)"]},
                {"name": "Chapter 2: Addition & Subtraction", "topics": ["Simple Addition", "Simple Subtraction", "Word Problems", "Money & Coins"]}
            ]
        },
        {
            "name": "General Science", "color": "#06B6D4",
            "chapters": [
                {"name": "Chapter 1: Living and Non-Living Things", "topics": ["Features of Living Things", "Natural vs Man-made Things", "Plants & Animals Around Us"]},
                {"name": "Chapter 2: My Body & Healthy Habits", "topics": ["Parts of My Body", "Sense Organs", "Good Habits & Exercise"]}
            ]
        }
    ],

    ("ICSE", "Class 6"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Number System & Speed Distance Time", "topics": ["Natural Numbers & Whole Numbers", "Integers & Operations", "HCF and LCM", "Speed, Distance and Time Calculations"]},
                {"name": "Chapter 2: Algebra & Geometry", "topics": ["Fundamental Concepts of Algebra", "Linear Equations in One Variable", "Angles, Triangles and Polygons", "Perimeter and Area of Plane Figures"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Matter & Physical Quantities", "topics": ["States of Matter & Molecular Properties", "Measurement of Length, Mass & Time", "Units and Systems of Measurement"]},
                {"name": "Chapter 2: Force, Light & Magnetism", "topics": ["Types of Forces & Effects", "Light, Shadows & Images", "Magnetic Properties & Poles"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Introduction to Chemistry & Matter", "topics": ["Importance of Chemistry", "Elements, Compounds & Mixtures", "Methods of Separation"]},
                {"name": "Chapter 2: Water & Air", "topics": ["Importance & Uses of Water", "Composition of Air", "Properties of Oxygen & Nitrogen"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Plant Life & Cell Structure", "topics": ["Structure of Leaf & Flower", "Photosynthesis Basic Idea", "Cell - Structure and Function"]},
                {"name": "Chapter 2: Human Body & Health", "topics": ["Digestive System", "Circulatory System", "Health & Hygiene"]}
            ]
        }
    ],

    ("ICSE", "Class 9"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Pure & Commercial Mathematics", "topics": ["Rational & Irrational Numbers", "Compound Interest without Formula", "Compound Interest using Formula"]},
                {"name": "Chapter 2: Algebra & Geometry", "topics": ["Expansions & Factorisation", "Simultaneous Linear Equations", "Indices & Logarithms", "Triangles, Mid-Point Theorem & Circles"]},
                {"name": "Chapter 3: Trigonometry & Mensuration", "topics": ["Trigonometric Ratios", "Simple 30-60-90 Trigonometric Ratios", "Area and Perimeter of Triangles & Quadrilaterals", "Statistics & Mean"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Measurements & Motion", "topics": ["Least Count & Vernier Calipers", "Simple Pendulum", "Rest, Motion & Scalar/Vector", "Equations of Motion & Graphs"]},
                {"name": "Chapter 2: Laws of Motion, Fluids & Heat", "topics": ["Newton's First, Second & Third Law", "Gravitation & Mass vs Weight", "Pressure in Fluids & Atmospheric Pressure", "Thermal Expansion & Calorimetry"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Language of Chemistry & Periodic Table", "topics": ["Symbols, Valency & Chemical Formulae", "Balancing Chemical Equations", "Modern Periodic Table & Trends"]},
                {"name": "Chapter 2: Chemical Bonding & Gas Laws", "topics": ["Electrovalent and Covalent Bonding", "Boyle's Law and Charles's Law", "Study of Hydrogen & Water"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Basic Biology & Plant Physiology", "topics": ["Cell - The Unit of Life", "Tissues - Plant & Animal", "Photosynthesis & Respiration in Plants"]},
                {"name": "Chapter 2: Human Anatomy & Health", "topics": ["Skeletal & Muscular System", "Respiratory System", "Hygiene & Diseases"]}
            ]
        }
    ],

    ("ICSE", "Class 10"): [
        {
            "name": "Mathematics", "color": "#6366F1",
            "chapters": [
                {"name": "Chapter 1: Commercial Mathematics", "topics": ["Goods and Services Tax (GST)", "Banking (Recurring Deposit Accounts)", "Shares and Dividends"]},
                {"name": "Chapter 2: Algebra", "topics": ["Linear Inequations", "Quadratic Equations in One Variable", "Remainder and Factor Theorems", "Matrices & Arithmetic/Geometric Progressions"]},
                {"name": "Chapter 3: Geometry & Coordinate Geometry", "topics": ["Similarity of Triangles", "Loci & Circles (Angle & Cyclic Properties)", "Reflection & Section/Midpoint Formula", "Equation of a Line"]},
                {"name": "Chapter 4: Trigonometry, Mensuration & Probability", "topics": ["Trigonometric Identities & Tables", "Heights and Distances", "Cylinder, Cone and Sphere Surface Area & Volume", "Histogram, Ogive & Probability"]}
            ]
        },
        {
            "name": "Physics", "color": "#3B82F6",
            "chapters": [
                {"name": "Chapter 1: Force, Work, Energy & Power", "topics": ["Turning Effect of Force & Equilibrium", "Center of Gravity", "Work, Energy, Power & Machines", "Principle of Conservation of Energy"]},
                {"name": "Chapter 2: Light & Sound", "topics": ["Refraction through Plane Surface & Prism", "Refraction through Convex/Concave Lens", "Spectrum & Electromagnetic Waves", "Reflection of Sound & Echoes", "Vibrations & Resonance"]},
                {"name": "Chapter 3: Electricity, Magnetism & Modern Physics", "topics": ["Ohm's Law, Resistance & Combination", "Electrical Energy & Power", "Household Circuits & Safety (Fuse, Earthing)", "Magnetic Effect of Current & Transformer", "Radioactivity & Alpha, Beta, Gamma Radiations"]}
            ]
        },
        {
            "name": "Chemistry", "color": "#EC4899",
            "chapters": [
                {"name": "Chapter 1: Periodic Table & Chemical Bonding", "topics": ["Periodic Properties & Periodic Trends", "Electrovalent, Covalent & Coordinate Bonding", "Electron Dot Structures"]},
                {"name": "Chapter 2: Acids, Bases, Salts & Analytical Chemistry", "topics": ["Definitions & Properties of Acids/Bases", "Types of Salts & Preparation", "Action of Ammonium Hydroxide & Sodium Hydroxide on Salts"]},
                {"name": "Chapter 3: Mole Concept & Electrolysis", "topics": ["Gay-Lussac's Law & Avogadro's Law", "Vapour Density & Molecular Weight", "Electrolysis of Molten Lead Bromide, Acidulated Water & Electroplating"]},
                {"name": "Chapter 4: Metallurgy & Organic Chemistry", "topics": ["Extraction of Aluminium", "Hydrocarbons - Alkanes, Alkenes, Alkynes", "Alcohols and Carboxylic Acids"]}
            ]
        },
        {
            "name": "Biology", "color": "#10B981",
            "chapters": [
                {"name": "Chapter 1: Basic Biology & Plant Physiology", "topics": ["Structure of Chromosomes & Cell Division", "Genetics & Mendel's Laws", "Absorption by Roots & Osmosis", "Transpiration & Photosynthesis"]},
                {"name": "Chapter 2: Human Anatomy & Physiology", "topics": ["Circulatory System & Heart", "Excretory System & Kidney", "Nervous System & Sense Organs", "Endocrine System & Hormones"]},
                {"name": "Chapter 3: Reproductive System & Population", "topics": ["Male & Female Reproductive System", "Population Explosion & Control Methods"]}
            ]
        },
        {
            "name": "History & Civics", "color": "#F59E0B",
            "chapters": [
                {"name": "Civics: Union Judiciary & Parliament", "topics": ["Union Parliament (Lok Sabha & Rajya Sabha)", "The President & Vice President", "Prime Minister & Council of Ministers", "Supreme Court & High Court"]},
                {"name": "History: Indian National Movement", "topics": ["First War of Independence (1857)", "Factors Leading to Growth of Nationalism", "First Phase of Indian National Congress", "Mass Movement under Mahatma Gandhi", "Partition of India & Independence"]}
            ]
        },
        {
            "name": "Geography", "color": "#8B5CF6",
            "chapters": [
                {"name": "Chapter 1: Map Work & Climate of India", "topics": ["Interpretation of Topographical Maps", "Map of India (Mountains, Rivers, Cities)", "Factors Affecting Climate of India", "Seasons of India & Monsoons"]},
                {"name": "Chapter 2: Natural Resources of India", "topics": ["Types of Soil in India", "Forest Conservation & Vegetation", "Water Resources & Rainwater Harvesting", "Mineral and Energy Resources"]},
                {"name": "Chapter 3: Agriculture & Industries in India", "topics": ["Types of Agriculture & Food Crops", "Cash Crops & Commercial Farming", "Agro-based & Mineral-based Industries", "Transport & Waste Management"]}
            ]
        }
    ]
}


from models import add_subject, add_chapter, add_topic, get_subject_by_name, get_chapters_for_subject

def normalize_class_name(raw_class: str) -> str:
    """Normalize class string to matching key format like 'Class 10'."""
    s = str(raw_class).strip().lower()
    for num in range(1, 11):
        if str(num) in s or f"class {num}" in s or f"class{num}" in s:
            return f"Class {num}"
    if "ix" in s or "9" in s:
        return "Class 9"
    if "x" in s or "10" in s:
        return "Class 10"
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
