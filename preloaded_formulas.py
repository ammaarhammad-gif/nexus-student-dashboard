"""
preloaded_formulas.py — Canonical Chapter-Wise Academic Formula Datastore & Auto-Seeder.

Provides high-rigor, official curriculum formulas for CBSE and ICSE (Class 9, 10 & General STEM)
organized into academic categories:
- Core Formulas
- Derived / Useful Relations
- Definitions & Relations
- Constants / Values

Includes automated fuzzy syllabus chapter-matching and transactional seeding.
"""

import logging
from models import (
    get_all_subjects,
    get_chapters_for_subject,
    get_all_formulas,
    bulk_seed_canonical_formulas
)

logger = logging.getLogger("NexusFormulaDatastore")

# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE CANONICAL FORMULA CATALOG
# Mapped by canonical subject keyword and chapter keyword
# ══════════════════════════════════════════════════════════════════════════════

CANONICAL_FORMULAS_CATALOG = [
    # ──────────────────────────────────────────────────────────────────────────
    # PHYSICS: LIGHT - REFLECTION AND REFRACTION
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["physics", "science", "general science"],
        "chapter_match": ["light", "reflection", "refraction", "optics"],
        "formulas": [
            {
                "title": "Mirror Formula",
                "latex": r"\frac{1}{f} = \frac{1}{v} + \frac{1}{u}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Relates object distance (u), image distance (v), and focal length (f) for all spherical mirrors.",
                "variables": {
                    "f": "Focal length of mirror (meters or cm)",
                    "v": "Image distance from pole (meters or cm)",
                    "u": "Object distance from pole (meters or cm)"
                },
                "units": "f, v, u in meters (m) or cm",
                "conditions": "Follows Cartesian sign convention. For concave mirror f is negative; for convex mirror f is positive. u is always negative for real objects.",
                "common_mistake": "Confusing the plus (+) sign with the lens formula minus (-) sign, or failing to assign negative sign to u.",
                "example_application": "A concave mirror of focal length 15 cm forms an image of an object placed 30 cm in front. Using 1/f = 1/v + 1/u gives v = -30 cm (real, inverted)."
            },
            {
                "title": "Spherical Mirror Magnification",
                "latex": r"m = \frac{h'}{h} = -\frac{v}{u}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Linear magnification produced by a spherical mirror representing the ratio of image height to object height.",
                "variables": {
                    "m": "Linear magnification (dimensionless)",
                    "h'": "Height of the image",
                    "h": "Height of the object",
                    "v": "Image distance",
                    "u": "Object distance"
                },
                "units": "Dimensionless ratio",
                "conditions": "m is negative for real and inverted images; m is positive for virtual and erect images.",
                "common_mistake": "Omitting the negative sign in m = -v/u for mirrors.",
                "example_application": "If u = -30 cm and v = -30 cm, m = -(-30)/(-30) = -1, meaning the image is real, inverted, and same size."
            },
            {
                "title": "Focal Length and Radius of Curvature",
                "latex": r"f = \frac{R}{2}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "For spherical mirrors of small aperture, the focal length is half the radius of curvature.",
                "variables": {
                    "f": "Focal length",
                    "R": "Radius of curvature of the spherical surface"
                },
                "units": "meters (m) or cm",
                "conditions": "Valid for paraxial rays and spherical mirrors with small apertures.",
                "common_mistake": "Using R instead of f directly in the mirror formula.",
                "example_application": "A convex rear-view mirror has R = 3.00 m, so f = +3.00/2 = +1.50 m."
            },
            {
                "title": "Snell's Law of Refraction",
                "latex": r"n_{21} = \frac{\sin i}{\sin r} = \frac{n_2}{n_1} = \frac{v_1}{v_2}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "The ratio of sine of angle of incidence to sine of angle of refraction is constant for a given pair of media.",
                "variables": {
                    "i": "Angle of incidence in medium 1",
                    "r": "Angle of refraction in medium 2",
                    "n_{21}": "Refractive index of medium 2 with respect to medium 1",
                    "v_1": "Speed of light in medium 1",
                    "v_2": "Speed of light in medium 2"
                },
                "units": "Dimensionless ratio",
                "conditions": "Valid for angles 0° < i < 90°. Rays bend towards normal when entering denser medium (v2 < v1).",
                "common_mistake": "Swapping i and r, or inverting n1 and n2.",
                "example_application": "Light travels from air (n1=1) into water (n2=1.33) at i = 45°. sin(r) = sin(45°)/1.33 = 0.5316 => r ≈ 32.1°."
            },
            {
                "title": "Absolute Refractive Index",
                "latex": r"n = \frac{c}{v}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Ratio of speed of light in vacuum (c) to the speed of light in the given medium (v).",
                "variables": {
                    "n": "Absolute refractive index (always >= 1)",
                    "c": "Speed of light in vacuum (3.0 x 10^8 m/s)",
                    "v": "Speed of light in the medium"
                },
                "units": "Dimensionless",
                "conditions": "Optical density is directly proportional to n, but physical density is not necessarily so.",
                "common_mistake": "Believing a higher physical density always means higher optical refractive index (e.g. kerosene vs water).",
                "example_application": "In glass with n = 1.5, light speed v = 3.0 x 10^8 / 1.5 = 2.0 x 10^8 m/s."
            },
            {
                "title": "Lens Formula",
                "latex": r"\frac{1}{f} = \frac{1}{v} - \frac{1}{u}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Fundamental relationship between object distance (u), image distance (v), and focal length (f) for thin spherical lenses.",
                "variables": {
                    "f": "Focal length of lens",
                    "v": "Image distance from optical centre",
                    "u": "Object distance from optical centre"
                },
                "units": "meters (m) or cm",
                "conditions": "Cartesian sign convention: Convex lens f is positive (+); Concave lens f is negative (-). u is negative for real objects.",
                "common_mistake": "Confusing the minus sign with the mirror formula's plus sign.",
                "example_application": "For a convex lens with f = +10 cm and u = -30 cm: 1/v = 1/f + 1/u = 1/10 - 1/30 = 2/30 => v = +15 cm."
            },
            {
                "title": "Lens Magnification",
                "latex": r"m = \frac{h'}{h} = \frac{v}{u}",
                "category": "Derived / Useful Relations",
                "is_core": 0,
                "description": "Linear magnification for thin lenses (positive sign compared to mirror formula).",
                "variables": {
                    "m": "Linear magnification",
                    "h'": "Image height",
                    "h": "Object height",
                    "v": "Image distance",
                    "u": "Object distance"
                },
                "units": "Dimensionless",
                "conditions": "Positive m indicates virtual and erect image; negative m indicates real and inverted image.",
                "common_mistake": "Inserting an unwanted negative sign (which belongs to mirrors, not lenses).",
                "example_application": "With v = +15 cm and u = -30 cm, m = +15 / (-30) = -0.5 (real, inverted, half size)."
            },
            {
                "title": "Power of a Lens",
                "latex": r"P = \frac{1}{f\text{ (in meters)}}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Degree of convergence or divergence of light rays achieved by a lens, defined as reciprocal of focal length in meters.",
                "variables": {
                    "P": "Power of lens in Dioptres (D or m^-1)",
                    "f": "Focal length in meters"
                },
                "units": "Dioptre (D)",
                "conditions": "f must be converted to meters before calculating. Convex lens power is positive (+); concave lens power is negative (-).",
                "common_mistake": "Using focal length in cm directly without dividing by 100 (e.g. 1/50 instead of 100/50).",
                "example_application": "A lens of focal length f = -50 cm = -0.5 m has power P = 1/(-0.5) = -2.0 D."
            },
            {
                "title": "Combination of Thin Lenses",
                "latex": r"P_{\text{net}} = P_1 + P_2 + P_3 + \dots",
                "category": "Derived / Useful Relations",
                "is_core": 0,
                "description": "Net optical power of multiple thin lenses placed in close contact.",
                "variables": {
                    "P_{net}": "Net optical power",
                    "P_1, P_2": "Powers of individual constituent lenses"
                },
                "units": "Dioptre (D)",
                "conditions": "Lenses must be thin and in physical contact.",
                "common_mistake": "Multiplying powers instead of adding them algebraically.",
                "example_application": "Combining a +2.0 D lens and a -1.5 D lens yields P = +2.0 - 1.5 = +0.5 D (net focal length +2 m)."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # PHYSICS: ELECTRICITY & CIRCUITS
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["physics", "science", "general science"],
        "chapter_match": ["electricity", "current", "circuit", "magnetic effects"],
        "formulas": [
            {
                "title": "Electric Current",
                "latex": r"I = \frac{Q}{t}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Rate of flow of electric charge through any cross-section of a conductor.",
                "variables": {
                    "I": "Electric current in Amperes (A)",
                    "Q": "Net electric charge in Coulombs (C)",
                    "t": "Time interval in seconds (s)"
                },
                "units": "Ampere (A) = C/s",
                "conditions": "1 Ampere = 1 Coulomb per second. 1 Coulomb ≈ 6.25 x 10^18 electrons.",
                "common_mistake": "Using minutes instead of converting to seconds.",
                "example_application": "A current of 0.5 A drawn by a filament for 10 minutes (600 s) corresponds to Q = 0.5 x 600 = 300 C."
            },
            {
                "title": "Electric Potential Difference",
                "latex": r"V = \frac{W}{Q}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Work done in moving a unit positive charge from one point to another in an electric circuit.",
                "variables": {
                    "V": "Potential difference in Volts (V)",
                    "W": "Work done in Joules (J)",
                    "Q": "Charge moved in Coulombs (C)"
                },
                "units": "Volt (V) = J/C",
                "conditions": "1 Volt = 1 Joule per 1 Coulomb.",
                "common_mistake": "Confusing potential difference with current or electromotive force.",
                "example_application": "Moving 2 C of charge across two points at 12 V requires W = V x Q = 12 x 2 = 24 J."
            },
            {
                "title": "Ohm's Law",
                "latex": r"V = I \cdot R",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Potential difference across ends of a metallic conductor is directly proportional to current flowing through it, at constant temperature.",
                "variables": {
                    "V": "Potential difference in Volts (V)",
                    "I": "Current in Amperes (A)",
                    "R": "Resistance of conductor in Ohms (Ω)"
                },
                "units": "Ohm (Ω) = V/A",
                "conditions": "Valid for ohmic conductors maintained at constant physical conditions (temperature, strain).",
                "common_mistake": "Assuming resistance changes with voltage for ohmic conductors; R is a constant property of the conductor.",
                "example_application": "A toaster connected to a 220 V line draws 4 A. Resistance R = 220 / 4 = 55 Ω."
            },
            {
                "title": "Resistance and Resistivity",
                "latex": r"R = \rho \frac{l}{A}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Resistance of a uniform conductor is proportional to length (l) and inversely proportional to cross-sectional area (A).",
                "variables": {
                    "R": "Resistance in Ohms (Ω)",
                    r"\rho": "Specific resistance / Resistivity in Ohm-meters (Ω·m)",
                    "l": "Length of wire in meters (m)",
                    "A": "Cross-sectional area in m^2 (A = πr^2 for circular wire)"
                },
                "units": r"Resistivity \rho in Ω·m",
                "conditions": "Resistivity is an intrinsic material property that varies with temperature, independent of dimensions.",
                "common_mistake": "If wire is stretched to double length, area halves, so resistance increases 4 times (R' = 4R).",
                "example_application": "A copper wire (ρ = 1.6 x 10^-8 Ω·m) of length 10 m and radius 1 mm (A = 3.14 x 10^-6 m^2) has R = 0.051 Ω."
            },
            {
                "title": "Resistors in Series",
                "latex": r"R_s = R_1 + R_2 + R_3 + \dots + R_n",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Equivalent resistance of conductors connected end-to-end in a single electrical branch.",
                "variables": {
                    "R_s": "Equivalent series resistance (Ω)",
                    "R_1, R_2, R_3": "Individual component resistances"
                },
                "units": "Ohms (Ω)",
                "conditions": "Current (I) is identical through each resistor; total voltage is sum of individual voltage drops (V = V1 + V2 + ...).",
                "common_mistake": "Confusing series current equality with parallel voltage equality.",
                "example_application": "Series connection of 5 Ω, 10 Ω, and 15 Ω gives Rs = 5 + 10 + 15 = 30 Ω."
            },
            {
                "title": "Resistors in Parallel",
                "latex": r"\frac{1}{R_p} = \frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_3} + \dots",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Equivalent resistance of conductors connected between two common electrical nodes.",
                "variables": {
                    "R_p": "Equivalent parallel resistance (always less than smallest resistor)",
                    "R_1, R_2, R_3": "Individual component resistances"
                },
                "units": "Ohms (Ω)",
                "conditions": "Voltage drop (V) is identical across all parallel branches; total current is sum of branch currents (I = I1 + I2 + ...).",
                "common_mistake": "Adding fractions and forgetting to invert the result to get Rp.",
                "example_application": "Two resistors of 6 Ω and 3 Ω in parallel: 1/Rp = 1/6 + 1/3 = 3/6 = 1/2 => Rp = 2 Ω."
            },
            {
                "title": "Joule's Law of Heating",
                "latex": r"H = I^2 R t = V I t = \frac{V^2}{R} t",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Heat energy generated in a resistor is proportional to the square of current, resistance, and time.",
                "variables": {
                    "H": "Heat energy in Joules (J)",
                    "I": "Current in Amperes (A)",
                    "R": "Resistance in Ohms (Ω)",
                    "t": "Time in seconds (s)",
                    "V": "Voltage across resistor in Volts (V)"
                },
                "units": "Joule (J)",
                "conditions": "Assumes all electrical work is converted into thermal energy.",
                "common_mistake": "Using minutes instead of seconds for time t.",
                "example_application": "A heater of 100 Ω carrying 2 A for 2 hours (7200 s) produces H = (2)^2 x 100 x 7200 = 2,880,000 J (2.88 MJ)."
            },
            {
                "title": "Electric Power Relations",
                "latex": r"P = V I = I^2 R = \frac{V^2}{R}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Rate at which electric energy is dissipated or consumed in an electric circuit.",
                "variables": {
                    "P": "Electric power in Watts (W = J/s)",
                    "V": "Voltage (V)",
                    "I": "Current (A)",
                    "R": "Resistance (Ω)"
                },
                "units": "Watt (W), Kilowatt (kW = 1000 W)",
                "conditions": "Use P = V^2/R for parallel appliances (common voltage); use P = I^2*R for series components (common current).",
                "common_mistake": "Using P = I^2*R when voltage is fixed across varying parallel devices.",
                "example_application": "An electric bulb rated 220 V, 100 W has resistance R = V^2/P = 220^2 / 100 = 484 Ω."
            },
            {
                "title": "Commercial Unit of Electrical Energy",
                "latex": r"1\text{ kWh} = 3.6 \times 10^6\text{ J} = 1\text{ Unit}",
                "category": "Constants / Values",
                "is_core": 0,
                "description": "Commercial electricity billing unit representing 1 kilowatt of power consumed continuously for 1 hour.",
                "variables": {
                    "\text{kWh}": "Kilowatt-hour",
                    "\text{J}": "Joules"
                },
                "units": "Kilowatt-hour (kWh)",
                "conditions": "Energy (kWh) = [Power in Watts x Time in Hours] / 1000.",
                "common_mistake": "Confusing power (kW) with energy (kWh).",
                "example_application": "A 1000 W geyser running for 2 hours daily consumes (1000 x 2)/1000 = 2 kWh (2 units) per day."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # PHYSICS: MOTION, FORCE & GRAVITATION
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["physics", "science", "general science"],
        "chapter_match": ["motion", "force", "gravitation", "work", "energy"],
        "formulas": [
            {
                "title": "First Equation of Motion",
                "latex": r"v = u + a t",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Relates final velocity (v), initial velocity (u), uniform acceleration (a), and time (t).",
                "variables": {
                    "v": "Final velocity in m/s",
                    "u": "Initial velocity in m/s",
                    "a": "Uniform acceleration in m/s^2",
                    "t": "Time interval in seconds (s)"
                },
                "units": "m/s",
                "conditions": "Valid only for motion under constant uniform acceleration along a straight line.",
                "common_mistake": "Applying this equation when acceleration is varying with time.",
                "example_application": "A car accelerates from rest (u=0) at 2 m/s^2 for 5 s: v = 0 + 2(5) = 10 m/s."
            },
            {
                "title": "Second Equation of Motion",
                "latex": r"s = u t + \frac{1}{2} a t^2",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Calculates displacement (s) covered during time (t) under uniform acceleration (a).",
                "variables": {
                    "s": "Displacement in meters (m)",
                    "u": "Initial velocity in m/s",
                    "a": "Acceleration in m/s^2",
                    "t": "Time in seconds (s)"
                },
                "units": "meters (m)",
                "conditions": "Uniform acceleration along a straight path.",
                "common_mistake": "Squaring both u and t instead of only t in the second term.",
                "example_application": "Displacement of a stone dropped (u=0) for 3 s with g=9.8 m/s^2 is s = 0.5(9.8)(3^2) = 44.1 m."
            },
            {
                "title": "Third Equation of Motion",
                "latex": r"v^2 = u^2 + 2 a s",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Time-independent relation between initial velocity, final velocity, acceleration, and displacement.",
                "variables": {
                    "v": "Final velocity (m/s)",
                    "u": "Initial velocity (m/s)",
                    "a": "Acceleration (m/s^2)",
                    "s": "Displacement (m)"
                },
                "units": "m^2/s^2",
                "conditions": "Uniform acceleration.",
                "common_mistake": "Forgetting negative acceleration when braking or throwing upwards.",
                "example_application": "A ball thrown upward with u = 20 m/s reaches peak (v=0) at height s = (0 - 400)/(-2 * 9.8) ≈ 20.4 m."
            },
            {
                "title": "Newton's Second Law of Motion",
                "latex": r"F = m a = \frac{\Delta p}{\Delta t}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Net force acting on an object equals rate of change of momentum (or mass times acceleration for constant mass).",
                "variables": {
                    "F": "Net external force in Newtons (N = kg·m/s^2)",
                    "m": "Mass of body in kg",
                    "a": "Acceleration in m/s^2",
                    r"\Delta p": "Change in linear momentum (p = mv)"
                },
                "units": "Newton (N)",
                "conditions": "Valid in inertial reference frames for constant mass.",
                "common_mistake": "Using grams instead of kilograms for mass.",
                "example_application": "Force required to accelerate a 1500 kg vehicle at 3 m/s^2 is F = 1500 x 3 = 4500 N."
            },
            {
                "title": "Universal Law of Gravitation",
                "latex": r"F = G \frac{m_1 m_2}{r^2}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Every mass attracts every other mass with a force proportional to product of masses and inversely proportional to square of separation.",
                "variables": {
                    "F": "Gravitational attraction force in Newtons (N)",
                    "G": "Universal gravitational constant (6.674 x 10^-11 N·m^2/kg^2)",
                    "m_1, m_2": "Masses of interacting bodies in kg",
                    "r": "Distance between centers of mass in meters (m)"
                },
                "units": "Newton (N)",
                "conditions": "Valid for point masses and spherically symmetric bodies.",
                "common_mistake": "Forgetting to square the distance r in the denominator.",
                "example_application": "Gravitational force between two 1 kg spheres separated by 1 m is F = 6.67 x 10^-11 N."
            },
            {
                "title": "Kinetic Energy",
                "latex": r"E_k = \frac{1}{2} m v^2",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Energy possessed by an object by virtue of its motion.",
                "variables": {
                    "E_k": "Kinetic energy in Joules (J)",
                    "m": "Mass in kg",
                    "v": "Velocity in m/s"
                },
                "units": "Joule (J) = kg·m^2/s^2",
                "conditions": "Scalar quantity. Always non-negative.",
                "common_mistake": "If speed doubles, kinetic energy quadruples (factor of 4), not doubles.",
                "example_application": "A 2 kg brick moving at 4 m/s has Ek = 0.5 x 2 x (4)^2 = 16 J."
            },
            {
                "title": "Gravitational Potential Energy",
                "latex": r"E_p = m g h",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Energy stored in an object due to its position relative to ground in a uniform gravitational field.",
                "variables": {
                    "E_p": "Potential energy in Joules (J)",
                    "m": "Mass in kg",
                    "g": "Acceleration due to gravity (≈ 9.8 m/s^2 on Earth)",
                    "h": "Height above reference plane in meters"
                },
                "units": "Joule (J)",
                "conditions": "Valid for heights h much smaller than Earth radius where g remains constant.",
                "common_mistake": "Measuring height from an inconsistent reference datum.",
                "example_application": "Lifting a 10 kg box to a shelf 2 m high requires Ep = 10 x 9.8 x 2 = 196 J."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # MATHEMATICS: ALGEBRA & POLYNOMIALS
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["math", "mathematics"],
        "chapter_match": ["polynomial", "real number", "quadratic", "linear equation", "arithmetic progression"],
        "formulas": [
            {
                "title": "Quadratic Formula (Sridharacharya Formula)",
                "latex": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Standard analytic solution for roots of quadratic equation ax^2 + bx + c = 0.",
                "variables": {
                    "a": "Coefficient of x^2 (a ≠ 0)",
                    "b": "Coefficient of x",
                    "c": "Constant term",
                    "x": "Roots / Solutions of equation"
                },
                "units": "Pure algebraic number",
                "conditions": "Real roots exist only when discriminant D = b^2 - 4ac >= 0.",
                "common_mistake": "Forgetting the denominator spans the entire numerator (including -b), not just the square root.",
                "example_application": "For 2x^2 - 7x + 3 = 0: x = [7 ± sqrt(49 - 24)] / 4 = [7 ± 5] / 4 => x = 3 or x = 1/2."
            },
            {
                "title": "Discriminant & Nature of Roots",
                "latex": r"D = b^2 - 4ac",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Discriminant classifies roots into distinct real, equal real, or non-real roots.",
                "variables": {
                    "D": "Discriminant value",
                    "D > 0": "Two distinct real roots",
                    "D = 0": "Two equal real roots (x = -b/2a)",
                    "D < 0": "No real roots (imaginary conjugate pair)"
                },
                "units": "Dimensionless",
                "conditions": "Coefficients a, b, c are real numbers with a ≠ 0.",
                "common_mistake": "Checking D > 0 when the question asks for 'real roots' (which is D >= 0).",
                "example_application": "Equation x^2 - 6x + 9 = 0 has D = (-6)^2 - 4(1)(9) = 0, so roots are real and equal (x = 3, 3)."
            },
            {
                "title": "Relationship Between Zeros and Coefficients",
                "latex": r"\alpha + \beta = -\frac{b}{a}, \quad \alpha \cdot \beta = \frac{c}{a}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Vieta's formulas relating sum and product of quadratic zeros to polynomial coefficients.",
                "variables": {
                    "\alpha, \beta": "Zeros of quadratic polynomial ax^2 + bx + c",
                    "a, b, c": "Coefficients of polynomial"
                },
                "units": "Algebraic relation",
                "conditions": "Quadratic polynomial with a ≠ 0.",
                "common_mistake": "Missing the negative sign in the sum of zeros (-b/a).",
                "example_application": "Polynomial x^2 - 5x + 6 has zeros 2 and 3. Sum = 2+3 = 5 = -(-5)/1; Product = 2*3 = 6 = 6/1."
            },
            {
                "title": "nth Term of an Arithmetic Progression",
                "latex": r"a_n = a + (n - 1) d",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Calculates the general n-th term of an AP with first term (a) and common difference (d).",
                "variables": {
                    "a_n": "n-th term value",
                    "a": "First term of the AP",
                    "n": "Term index (positive integer >= 1)",
                    "d": "Common difference (d = a_{k+1} - a_k)"
                },
                "units": "Sequence element",
                "conditions": "n must be a positive integer.",
                "common_mistake": "Writing (n) instead of (n - 1) in the formula.",
                "example_application": "For AP 3, 7, 11, 15... (a=3, d=4), the 10th term is a10 = 3 + (10-1)*4 = 3 + 36 = 39."
            },
            {
                "title": "Sum of First n Terms of an AP",
                "latex": r"S_n = \frac{n}{2} \left[ 2a + (n - 1) d \right] = \frac{n}{2} (a + l)",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Calculates the total summation of first n consecutive terms of an Arithmetic Progression.",
                "variables": {
                    "S_n": "Sum of first n terms",
                    "n": "Number of terms to sum",
                    "a": "First term",
                    "d": "Common difference",
                    "l": "Last term (l = a_n)"
                },
                "units": "Sum value",
                "conditions": "Requires arithmetic progression sequence.",
                "common_mistake": "Using 'a' instead of '2a' when writing the first expansion form.",
                "example_application": "Sum of first 20 natural numbers (a=1, l=20): S20 = (20/2)(1 + 20) = 10 x 21 = 210."
            },
            {
                "title": "HCF and LCM Product Theorem",
                "latex": r"\text{HCF}(a, b) \times \text{LCM}(a, b) = a \times b",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "For any two positive integers a and b, the product of their HCF and LCM equals their numerical product.",
                "variables": {
                    "a, b": "Two positive integers",
                    "\text{HCF}": "Highest Common Factor",
                    "\text{LCM}": "Lowest Common Multiple"
                },
                "units": "Integers",
                "conditions": "Holds strictly for TWO positive integers. Does NOT generally hold for three or more numbers.",
                "common_mistake": "Attempting to apply HCF(a,b,c) * LCM(a,b,c) = a*b*c for three numbers.",
                "example_application": "For 12 and 18: HCF = 6, LCM = 36. 6 x 36 = 216; 12 x 18 = 216."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # MATHEMATICS: TRIGONOMETRY & COORDINATE GEOMETRY
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["math", "mathematics"],
        "chapter_match": ["trigonometry", "coordinate", "triangles", "geometry"],
        "formulas": [
            {
                "title": "Distance Formula",
                "latex": r"d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Distance between two points A(x1, y1) and B(x2, y2) on a 2D Cartesian plane.",
                "variables": {
                    "d": "Euclidean straight-line distance",
                    "(x_1, y_1)": "Coordinates of first point",
                    "(x_2, y_2)": "Coordinates of second point"
                },
                "units": "Linear units",
                "conditions": "Distance is always non-negative (d >= 0).",
                "common_mistake": "Subtracting x from y instead of subtracting x2 from x1.",
                "example_application": "Distance between (2, 3) and (6, 6) is sqrt((6-2)^2 + (6-3)^2) = sqrt(16 + 9) = 5 units."
            },
            {
                "title": "Section Formula (Internal Division)",
                "latex": r"P(x, y) = \left( \frac{m_1 x_2 + m_2 x_1}{m_1 + m_2}, \; \frac{m_1 y_2 + m_2 y_1}{m_1 + m_2} \right)",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Coordinates of point P dividing line segment joining A(x1, y1) and B(x2, y2) internally in ratio m1:m2.",
                "variables": {
                    "P(x, y)": "Coordinates of dividing point",
                    "m_1 : m_2": "Internal division ratio"
                },
                "units": "Cartesian coordinate pair",
                "conditions": "m1 + m2 ≠ 0 for internal division.",
                "common_mistake": "Cross-multiplying incorrectly (matching m1 with x1 instead of x2).",
                "example_application": "Midpoint (m1:m2 = 1:1) between (2, 4) and (6, 8) is ((2+6)/2, (4+8)/2) = (4, 6)."
            },
            {
                "title": "Fundamental Pythagorean Trigonometric Identity",
                "latex": r"\sin^2 \theta + \cos^2 \theta = 1",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Primary trigonometric identity relating sine and cosine for any real angle θ.",
                "variables": {
                    r"\theta": "Angle in degrees or radians",
                    r"\sin\theta": "Opposite / Hypotenuse",
                    r"\cos\theta": "Adjacent / Hypotenuse"
                },
                "units": "Dimensionless identity",
                "conditions": "Valid for all angles θ.",
                "common_mistake": "Writing sin(θ^2) + cos(θ^2) = 1 instead of (sin θ)^2 + (cos θ)^2 = 1.",
                "example_application": "If sin θ = 3/5, then cos^2 θ = 1 - 9/25 = 16/25 => cos θ = 4/5 (for acute θ)."
            },
            {
                "title": "Secondary Trigonometric Identities",
                "latex": r"1 + \tan^2 \theta = \sec^2 \theta, \quad 1 + \cot^2 \theta = \csc^2 \theta",
                "category": "Derived / Useful Relations",
                "is_core": 1,
                "description": "Derived Pythagorean identities for tangent, secant, cotangent, and cosecant.",
                "variables": {
                    r"\tan\theta": "sin θ / cos θ",
                    r"\sec\theta": "1 / cos θ",
                    r"\cot\theta": "cos θ / sin θ",
                    r"\csc\theta": "1 / sin θ"
                },
                "units": "Dimensionless",
                "conditions": "θ ≠ 90° for tan/sec identity; θ ≠ 0° for cot/csc identity.",
                "common_mistake": "Writing sec^2 θ - tan^2 θ = -1 (the correct relation is sec^2 θ - tan^2 θ = 1).",
                "example_application": "If tan θ = 4/3, sec^2 θ = 1 + 16/9 = 25/9 => sec θ = 5/3."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # MATHEMATICS: MENSURATION, SURFACE AREAS, VOLUMES & STATISTICS
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["math", "mathematics"],
        "chapter_match": ["surface area", "volume", "circle", "statistic", "mensuration"],
        "formulas": [
            {
                "title": "Right Circular Cone Formulas",
                "latex": r"l = \sqrt{r^2 + h^2}, \quad \text{CSA} = \pi r l, \quad \text{TSA} = \pi r (l + r), \quad V = \frac{1}{3} \pi r^2 h",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Slant height (l), Curved Surface Area (CSA), Total Surface Area (TSA), and Volume (V) of a right circular cone.",
                "variables": {
                    "r": "Base radius",
                    "h": "Vertical height",
                    "l": "Slant height",
                    "V": "Volume"
                },
                "units": "Area in m^2/cm^2; Volume in m^3/cm^3",
                "conditions": "h and r must be in identical length units.",
                "common_mistake": "Using vertical height h instead of slant height l when computing CSA = πrl.",
                "example_application": "A cone with r=3 cm, h=4 cm has l = sqrt(9+16) = 5 cm. CSA = π(3)(5) = 15π cm^2; V = (1/3)π(9)(4) = 12π cm^3."
            },
            {
                "title": "Sphere & Hemisphere Formulas",
                "latex": r"\text{TSA}_{\text{sphere}} = 4 \pi r^2, \quad V_{\text{sphere}} = \frac{4}{3} \pi r^3, \quad \text{TSA}_{\text{hemi}} = 3 \pi r^2, \quad V_{\text{hemi}} = \frac{2}{3} \pi r^3",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Surface area and volume relations for solid spheres and solid hemispheres.",
                "variables": {
                    "r": "Radius of sphere/hemisphere"
                },
                "units": "Area in cm^2; Volume in cm^3",
                "conditions": "For a solid hemisphere, TSA includes the flat circular base (2πr^2 + πr^2 = 3πr^2).",
                "common_mistake": "Using 2πr^2 as TSA of a solid hemisphere (2πr^2 is only the curved CSA).",
                "example_application": "Solid hemisphere of radius 7 cm has TSA = 3 x (22/7) x 49 = 462 cm^2."
            },
            {
                "title": "Mean of Grouped Data (Direct Method)",
                "latex": r"\bar{x} = \frac{\sum f_i x_i}{\sum f_i}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Arithmetic mean of grouped frequency distribution.",
                "variables": {
                    "\bar{x}": "Sample mean",
                    "f_i": "Frequency of i-th class interval",
                    "x_i": "Class mark / midpoint of i-th class interval: (Upper limit + Lower limit) / 2"
                },
                "units": "Units of data variable",
                "conditions": "Class marks must be evaluated accurately from class boundaries.",
                "common_mistake": "Using class limits directly instead of class midpoints x_i.",
                "example_application": "For interval [10-20] with f=5: class mark x = (10+20)/2 = 15. fi*xi = 5*15 = 75."
            },
            {
                "title": "Empirical Relationship Between Measures of Central Tendency",
                "latex": r"\text{Mode} = 3 \times \text{Median} - 2 \times \text{Mean}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Empirical relationship connecting Mode, Median, and Mean for moderately skewed distributions.",
                "variables": {
                    "\text{Mode}": "Most frequent value",
                    "\text{Median}": "Middle 50th percentile value",
                    "\text{Mean}": "Arithmetic average"
                },
                "units": "Data units",
                "conditions": "Valid for unimodal, moderately skewed continuous data.",
                "common_mistake": "Inverting the coefficients (e.g. writing 3 Mean - 2 Median).",
                "example_application": "If Mean = 20 and Median = 22: Mode = 3(22) - 2(20) = 66 - 40 = 26."
            }
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CHEMISTRY: STOICHIOMETRY, ACIDS & CARBON
    # ──────────────────────────────────────────────────────────────────────────
    {
        "subject_match": ["chemistry", "science", "general science"],
        "chapter_match": ["chemical reaction", "acid", "carbon", "compound", "matter", "atom"],
        "formulas": [
            {
                "title": "Mole Concept Relations",
                "latex": r"n = \frac{m}{M} = \frac{N}{N_A} = \frac{V_{\text{STP}}}{22.4\text{ L}}",
                "category": "Core Formulas",
                "is_core": 1,
                "description": "Calculates number of moles (n) from given mass (m), particle count (N), or STP gas volume.",
                "variables": {
                    "n": "Number of moles",
                    "m": "Given mass in grams (g)",
                    "M": "Molar mass in g/mol",
                    "N": "Number of molecules / atoms / ions",
                    "N_A": "Avogadro's constant (6.022 x 10^23 particles/mol)",
                    "V_{STP}": "Volume of ideal gas at STP (0°C, 1 atm) in Liters"
                },
                "units": "mol",
                "conditions": "Gas volume relation valid specifically at Standard Temperature and Pressure (STP).",
                "common_mistake": "Using kilograms instead of grams when dividing by molar mass M (g/mol).",
                "example_application": "44 g of CO2 (M = 44 g/mol) contains n = 44/44 = 1 mole = 6.022 x 10^23 molecules and occupies 22.4 L at STP."
            },
            {
                "title": "pH Scale Definition",
                "latex": r"\text{pH} = -\log_{10} [\text{H}^+], \quad \text{pH} + \text{pOH} = 14 \text{ at } 25^\circ\text{C}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "Logarithmic measure of hydrogen ion concentration [H+] in an aqueous solution.",
                "variables": {
                    "\text{pH}": "Potential of Hydrogen (0 to 14)",
                    "[\text{H}^+]": "Molar concentration of hydronium/hydrogen ions (mol/L)"
                },
                "units": "Dimensionless scale",
                "conditions": "pH < 7 is acidic; pH = 7 is neutral; pH > 7 is alkaline at 25°C.",
                "common_mistake": "Thinking a solution of pH 3 is twice as acidic as pH 6 (it is 10^3 = 1000 times more acidic).",
                "example_application": "A 0.01 M HCl solution has [H+] = 10^-2 M => pH = -log10(10^-2) = 2.0."
            },
            {
                "title": "General Hydrocarbon Formulae",
                "latex": r"\text{Alkane: } \text{C}_n\text{H}_{2n+2}, \quad \text{Alkene: } \text{C}_n\text{H}_{2n}, \quad \text{Alkyne: } \text{C}_n\text{H}_{2n-2}",
                "category": "Definitions & Relations",
                "is_core": 1,
                "description": "General homologous series formulas for saturated and unsaturated aliphatic hydrocarbons.",
                "variables": {
                    "n": "Number of carbon atoms (n >= 1 for alkane; n >= 2 for alkene and alkyne)"
                },
                "units": "Chemical formula",
                "conditions": "Alkanes contain single bonds (saturated); Alkenes contain C=C double bond; Alkynes contain C≡C triple bond.",
                "common_mistake": "Confusing alkene (C_nH_2n) with cycloalkane isomerism.",
                "example_application": "A 3-carbon alkane is Propane (C3H8); 3-carbon alkene is Propene (C3H6); 3-carbon alkyne is Propyne (C3H4)."
            }
        ]
    }
]


def seed_user_canonical_formulas(user_id: int) -> int:
    """
    Scans the student's enrolled subjects and chapters in the database,
    matches relevant canonical formulas from CANONICAL_FORMULAS_CATALOG,
    and bulk-inserts them with zero duplicates.

    Returns the number of new formulas seeded.
    """
    subjects = get_all_subjects(user_id)
    if not subjects:
        return 0

    formulas_to_seed = []

    for subj in subjects:
        s_id = subj["id"]
        s_name_lower = subj["name"].lower()
        chapters = get_chapters_for_subject(user_id, s_id)
        if not chapters:
            continue

        for chap in chapters:
            c_id = chap["id"]
            c_name_lower = chap["name"].lower()

            # Match against catalog entries
            for entry in CANONICAL_FORMULAS_CATALOG:
                # Check subject match
                subj_matched = any(sm in s_name_lower for sm in entry["subject_match"])
                if not subj_matched:
                    continue

                # Check chapter match
                chap_matched = any(cm in c_name_lower for cm in entry["chapter_match"])
                if not chap_matched:
                    continue

                for f_data in entry["formulas"]:
                    formulas_to_seed.append({
                        "subject_id": s_id,
                        "chapter_id": c_id,
                        "topic_id": None,
                        "title": f_data["title"],
                        "formula_latex": f_data["latex"],
                        "description": f_data.get("description", ""),
                        "variables_json": f_data.get("variables", {}),
                        "units": f_data.get("units", ""),
                        "conditions": f_data.get("conditions", ""),
                        "category": f_data.get("category", "Core Formulas"),
                        "is_core": f_data.get("is_core", 1),
                        "is_custom": 0,
                        "common_mistake": f_data.get("common_mistake", ""),
                        "example_application": f_data.get("example_application", "")
                    })

    if formulas_to_seed:
        count = bulk_seed_canonical_formulas(user_id, formulas_to_seed)
        logger.info(f"Seeded {count} canonical formulas for user {user_id}")
        return count
    return 0
