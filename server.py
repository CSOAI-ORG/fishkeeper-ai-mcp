"""
FishKeeper.AI MCP Server - Aquarium Management AI
Built by MEOK AI Labs | https://fishkeeper.ai

Water analysis, species identification, compatibility checking,
disease diagnosis, stocking calculations, and feeding schedules.
"""

import time
from datetime import datetime, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "fishkeeper-ai")

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
_RATE_LIMITS = {
    "free": {"requests_per_hour": 60},
    "pro": {"requests_per_hour": 5000},
}
_request_log: list[float] = []
_tier = "free"


def _check_rate_limit() -> bool:
    now = time.time()
    _request_log[:] = [t for t in _request_log if now - t < 3600]
    if len(_request_log) >= _RATE_LIMITS[_tier]["requests_per_hour"]:
        return False
    _request_log.append(now)
    return True


# ---------------------------------------------------------------------------
# Species database - real aquarium data
# ---------------------------------------------------------------------------
_SPECIES_DB: dict[str, dict] = {
    # Tropical freshwater
    "neon_tetra": {
        "common_name": "Neon Tetra",
        "scientific_name": "Paracheirodon innesi",
        "family": "Characidae",
        "origin": "South America (Peru, Colombia, Brazil)",
        "adult_size_cm": 3.5,
        "adult_size_inches": 1.4,
        "lifespan_years": 5,
        "min_tank_litres": 40,
        "min_tank_gallons": 10,
        "min_school_size": 6,
        "temperament": "peaceful",
        "swim_level": "middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (20, 26), "ph": (6.0, 7.0), "hardness_dgh": (2, 10)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "egg scatterer",
        "compatible_with": ["other tetras", "corydoras", "rasboras", "small gouramis", "shrimp"],
        "incompatible_with": ["large cichlids", "oscars", "arowanas", "aggressive fish"],
        "notes": "Iconic community fish. Susceptible to Neon Tetra Disease (Pleistophora). Keep in groups of 6+.",
        "feeding": {"type": "micro pellets, flake, frozen daphnia, brine shrimp", "frequency": "2x daily", "amount": "pinch"},
    },
    "betta_splendens": {
        "common_name": "Betta / Siamese Fighting Fish",
        "scientific_name": "Betta splendens",
        "family": "Osphronemidae",
        "origin": "Southeast Asia (Thailand, Cambodia)",
        "adult_size_cm": 7,
        "adult_size_inches": 2.8,
        "lifespan_years": 3,
        "min_tank_litres": 20,
        "min_tank_gallons": 5,
        "min_school_size": 1,
        "temperament": "semi-aggressive",
        "swim_level": "top",
        "diet": "carnivore",
        "water_params": {"temp_c": (24, 28), "ph": (6.5, 7.5), "hardness_dgh": (3, 12)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "bubble nest builder",
        "compatible_with": ["corydoras", "snails", "small peaceful bottom dwellers", "shrimp (large)"],
        "incompatible_with": ["other bettas (male)", "guppies", "barbs", "fin nippers"],
        "notes": "Never keep two males together. Needs surface access for labyrinth breathing. Prefers low flow.",
        "feeding": {"type": "betta pellets, frozen bloodworm, daphnia", "frequency": "2x daily", "amount": "2-3 pellets"},
    },
    "corydoras_paleatus": {
        "common_name": "Peppered Corydoras",
        "scientific_name": "Corydoras paleatus",
        "family": "Callichthyidae",
        "origin": "South America (Argentina, Brazil, Uruguay)",
        "adult_size_cm": 7,
        "adult_size_inches": 2.8,
        "lifespan_years": 5,
        "min_tank_litres": 60,
        "min_tank_gallons": 15,
        "min_school_size": 6,
        "temperament": "peaceful",
        "swim_level": "bottom",
        "diet": "omnivore",
        "water_params": {"temp_c": (18, 24), "ph": (6.0, 7.5), "hardness_dgh": (2, 15)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "egg depositor",
        "compatible_with": ["tetras", "rasboras", "bettas", "gouramis", "shrimp"],
        "incompatible_with": ["large cichlids", "aggressive bottom dwellers"],
        "notes": "Must have sand or smooth gravel substrate (barbels are sensitive). Keep in groups of 6+. Excellent cleaner crew.",
        "feeding": {"type": "sinking pellets, wafers, frozen bloodworm", "frequency": "1-2x daily", "amount": "1 wafer per 3 fish"},
    },
    "cherry_barb": {
        "common_name": "Cherry Barb",
        "scientific_name": "Puntius titteya",
        "family": "Cyprinidae",
        "origin": "Sri Lanka",
        "adult_size_cm": 5,
        "adult_size_inches": 2.0,
        "lifespan_years": 5,
        "min_tank_litres": 50,
        "min_tank_gallons": 13,
        "min_school_size": 6,
        "temperament": "peaceful",
        "swim_level": "middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (22, 27), "ph": (6.0, 7.5), "hardness_dgh": (4, 15)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "egg scatterer",
        "compatible_with": ["tetras", "rasboras", "corydoras", "gouramis", "shrimp"],
        "incompatible_with": ["large cichlids", "very aggressive fish"],
        "notes": "Males turn deep red when breeding. Unlike tiger barbs, these are NOT fin nippers. Endangered in the wild.",
        "feeding": {"type": "flake, micro pellets, frozen brine shrimp", "frequency": "2x daily", "amount": "pinch"},
    },
    "bristlenose_pleco": {
        "common_name": "Bristlenose Pleco",
        "scientific_name": "Ancistrus cirrhosus",
        "family": "Loricariidae",
        "origin": "South America (Amazon basin)",
        "adult_size_cm": 13,
        "adult_size_inches": 5.0,
        "lifespan_years": 10,
        "min_tank_litres": 80,
        "min_tank_gallons": 20,
        "min_school_size": 1,
        "temperament": "peaceful",
        "swim_level": "bottom",
        "diet": "herbivore/omnivore",
        "water_params": {"temp_c": (20, 27), "ph": (6.0, 7.5), "hardness_dgh": (2, 20)},
        "bioload": "medium",
        "difficulty": "beginner",
        "breeding": "cave spawner",
        "compatible_with": ["most community fish", "tetras", "barbs", "gouramis", "cichlids (peaceful)"],
        "incompatible_with": ["other plecos in small tanks", "very aggressive large cichlids"],
        "notes": "Excellent algae eater. Needs driftwood (aids digestion). Much better choice than Common Pleco which grows to 50cm+.",
        "feeding": {"type": "algae wafers, blanched courgette/cucumber, driftwood", "frequency": "daily (evening)", "amount": "1 wafer"},
    },
    "angelfish": {
        "common_name": "Angelfish",
        "scientific_name": "Pterophyllum scalare",
        "family": "Cichlidae",
        "origin": "South America (Amazon basin)",
        "adult_size_cm": 15,
        "adult_size_inches": 6.0,
        "lifespan_years": 10,
        "min_tank_litres": 150,
        "min_tank_gallons": 40,
        "min_school_size": 2,
        "temperament": "semi-aggressive",
        "swim_level": "middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (24, 30), "ph": (6.0, 7.5), "hardness_dgh": (3, 10)},
        "bioload": "medium-high",
        "difficulty": "intermediate",
        "breeding": "substrate spawner (pair bond)",
        "compatible_with": ["larger tetras", "corydoras", "plecos", "gouramis", "discus"],
        "incompatible_with": ["small tetras (neons - will eat them)", "fin nippers", "tiger barbs"],
        "notes": "Tall body needs tank at least 45cm/18in high. Will eat fish small enough to fit in mouth. Pairs can be territorial when breeding.",
        "feeding": {"type": "cichlid pellets, flake, frozen bloodworm, brine shrimp", "frequency": "2x daily", "amount": "moderate"},
    },
    "oscar": {
        "common_name": "Oscar",
        "scientific_name": "Astronotus ocellatus",
        "family": "Cichlidae",
        "origin": "South America (Amazon, Orinoco basins)",
        "adult_size_cm": 35,
        "adult_size_inches": 14.0,
        "lifespan_years": 15,
        "min_tank_litres": 350,
        "min_tank_gallons": 90,
        "min_school_size": 1,
        "temperament": "aggressive",
        "swim_level": "middle",
        "diet": "carnivore/omnivore",
        "water_params": {"temp_c": (22, 28), "ph": (6.0, 8.0), "hardness_dgh": (5, 20)},
        "bioload": "very high",
        "difficulty": "intermediate",
        "breeding": "substrate spawner",
        "compatible_with": ["other large cichlids", "large plecos", "silver dollars", "severums"],
        "incompatible_with": ["small fish (anything mouth-sized)", "shrimp", "snails", "slow swimmers"],
        "notes": "Extremely messy eaters - need powerful filtration. Very intelligent, recognise owners. Will rearrange tank decor. Grow FAST.",
        "feeding": {"type": "cichlid pellets, earthworms, prawns, occasional fruit", "frequency": "1-2x daily", "amount": "several pellets"},
    },
    "guppy": {
        "common_name": "Guppy",
        "scientific_name": "Poecilia reticulata",
        "family": "Poeciliidae",
        "origin": "South America / Caribbean",
        "adult_size_cm": 5,
        "adult_size_inches": 2.0,
        "lifespan_years": 2,
        "min_tank_litres": 40,
        "min_tank_gallons": 10,
        "min_school_size": 3,
        "temperament": "peaceful",
        "swim_level": "top/middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (22, 28), "ph": (6.8, 7.8), "hardness_dgh": (8, 20)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "livebearer (prolific)",
        "compatible_with": ["tetras", "corydoras", "rasboras", "mollies", "platies", "shrimp"],
        "incompatible_with": ["bettas (colour/fins provoke aggression)", "large cichlids", "fin nippers"],
        "notes": "Will breed rapidly. Keep in ratio of 2-3 females per male to reduce harassment. Prefer harder, slightly alkaline water.",
        "feeding": {"type": "flake, micro pellets, frozen brine shrimp, blanched veg", "frequency": "2x daily", "amount": "pinch"},
    },
    "dwarf_gourami": {
        "common_name": "Dwarf Gourami",
        "scientific_name": "Trichogaster lalius",
        "family": "Osphronemidae",
        "origin": "South Asia (India, Bangladesh)",
        "adult_size_cm": 9,
        "adult_size_inches": 3.5,
        "lifespan_years": 4,
        "min_tank_litres": 40,
        "min_tank_gallons": 10,
        "min_school_size": 1,
        "temperament": "peaceful",
        "swim_level": "top/middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (22, 28), "ph": (6.0, 7.5), "hardness_dgh": (4, 15)},
        "bioload": "low",
        "difficulty": "intermediate",
        "breeding": "bubble nest builder",
        "compatible_with": ["tetras", "rasboras", "corydoras", "small barbs", "shrimp"],
        "incompatible_with": ["other male gouramis", "aggressive fish", "bettas"],
        "notes": "Susceptible to Dwarf Gourami Iridovirus (DGIV) - buy from reputable source. Males can be territorial with each other.",
        "feeding": {"type": "flake, micro pellets, frozen bloodworm, daphnia", "frequency": "2x daily", "amount": "small pinch"},
    },
    "zebra_danio": {
        "common_name": "Zebra Danio",
        "scientific_name": "Danio rerio",
        "family": "Cyprinidae",
        "origin": "South Asia (India, Nepal, Bangladesh)",
        "adult_size_cm": 5,
        "adult_size_inches": 2.0,
        "lifespan_years": 5,
        "min_tank_litres": 40,
        "min_tank_gallons": 10,
        "min_school_size": 6,
        "temperament": "peaceful",
        "swim_level": "top/middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (18, 26), "ph": (6.5, 7.5), "hardness_dgh": (5, 20)},
        "bioload": "low",
        "difficulty": "beginner",
        "breeding": "egg scatterer",
        "compatible_with": ["tetras", "barbs", "corydoras", "rasboras", "gouramis"],
        "incompatible_with": ["slow long-finned fish (may nip)", "large predatory fish"],
        "notes": "Very hardy - excellent cycling fish. Active swimmers, need horizontal swimming space. Can tolerate unheated tanks in temperate climates.",
        "feeding": {"type": "flake, micro pellets, frozen daphnia", "frequency": "2x daily", "amount": "pinch"},
    },
    # Coldwater
    "goldfish_fancy": {
        "common_name": "Fancy Goldfish",
        "scientific_name": "Carassius auratus (fancy varieties)",
        "family": "Cyprinidae",
        "origin": "East Asia (domesticated)",
        "adult_size_cm": 20,
        "adult_size_inches": 8.0,
        "lifespan_years": 15,
        "min_tank_litres": 100,
        "min_tank_gallons": 25,
        "min_school_size": 1,
        "temperament": "peaceful",
        "swim_level": "all levels",
        "diet": "omnivore",
        "water_params": {"temp_c": (15, 24), "ph": (7.0, 8.0), "hardness_dgh": (6, 18)},
        "bioload": "very high",
        "difficulty": "intermediate",
        "breeding": "egg scatterer",
        "compatible_with": ["other fancy goldfish", "weather loach", "white cloud minnows"],
        "incompatible_with": ["tropical fish", "single-tail goldfish (outcompete fancies)", "small fish"],
        "notes": "NOT suitable for bowls. Very messy - need excellent filtration. 20 gallons for first fish, +10 per additional. Prone to swim bladder issues.",
        "feeding": {"type": "sinking goldfish pellets, blanched peas, bloodworm (occasional)", "frequency": "2x daily", "amount": "2-3 pellets each"},
    },
    # Marine
    "clownfish": {
        "common_name": "Common Clownfish / Ocellaris",
        "scientific_name": "Amphiprion ocellaris",
        "family": "Pomacentridae",
        "origin": "Indo-Pacific",
        "adult_size_cm": 9,
        "adult_size_inches": 3.5,
        "lifespan_years": 10,
        "min_tank_litres": 75,
        "min_tank_gallons": 20,
        "min_school_size": 1,
        "temperament": "semi-aggressive",
        "swim_level": "middle",
        "diet": "omnivore",
        "water_params": {"temp_c": (24, 27), "ph": (8.1, 8.4), "hardness_dgh": None, "salinity_ppt": (33, 35)},
        "bioload": "low",
        "difficulty": "intermediate",
        "breeding": "substrate spawner (pair bond)",
        "compatible_with": ["tangs", "gobies", "blennies", "cardinalfish", "anemones (host)"],
        "incompatible_with": ["other clownfish species", "aggressive damselfish", "large predators"],
        "notes": "Captive-bred recommended over wild-caught. Doesn't require an anemone to thrive. All born male - dominant fish becomes female.",
        "feeding": {"type": "marine pellets, frozen mysis, brine shrimp", "frequency": "2x daily", "amount": "small pinch"},
    },
}

# Common diseases database
_DISEASES = {
    "ich": {
        "name": "White Spot Disease (Ich/Ick)",
        "pathogen": "Ichthyophthirius multifiliis",
        "symptoms": ["white spots like grains of salt on body/fins", "flashing/rubbing against objects", "clamped fins", "loss of appetite", "lethargy"],
        "cause": "Parasite; triggered by stress, temperature drops, new fish introduction",
        "treatment": [
            "Raise temperature to 30C/86F gradually (2 degrees per day) to speed parasite lifecycle",
            "Add aquarium salt (1 tbsp per 5 gallons) for freshwater fish",
            "Medication: malachite green + formalin (e.g. Waterlife Protozin, API Super Ick Cure)",
            "Treat entire tank, not just affected fish",
            "Continue treatment for 3 days after last visible spot",
            "Increase aeration during treatment",
        ],
        "prevention": "Quarantine new fish 2 weeks, maintain stable temperature, reduce stress",
        "contagious": True,
        "severity": "moderate - fatal if untreated",
    },
    "fin_rot": {
        "name": "Fin Rot",
        "pathogen": "Aeromonas, Pseudomonas, or Flavobacterium bacteria",
        "symptoms": ["ragged, fraying fin edges", "fins appear shorter over time", "white or red edges on fins", "fin membrane dissolving", "lethargy"],
        "cause": "Poor water quality (primary cause), injury, stress, overcrowding",
        "treatment": [
            "FIRST: Test water and do 50% water change",
            "Address root cause - improve water quality (ammonia/nitrite must be 0)",
            "Mild cases: clean water alone may resolve it",
            "Moderate: anti-bacterial medication (Melafix, API Furan-2, eSHa 2000)",
            "Severe: antibiotics (erythromycin, kanamycin) if available",
            "Add Indian almond leaves or StressGuard to aid healing",
        ],
        "prevention": "Regular water changes, don't overstock, maintain good filtration",
        "contagious": False,
        "severity": "moderate - progressive if untreated, reversible if caught early",
    },
    "dropsy": {
        "name": "Dropsy (Edema)",
        "pathogen": "Usually Aeromonas hydrophila (bacterial)",
        "symptoms": ["pinecone-like scales (raised/protruding)", "severely bloated abdomen", "bulging eyes (popeye)", "pale gills", "lethargy", "loss of appetite"],
        "cause": "Organ failure (often kidneys), bacterial infection, poor water quality, internal parasites",
        "treatment": [
            "Isolate affected fish immediately",
            "Epsom salt bath (1 tbsp per gallon in hospital tank) to reduce fluid",
            "Antibiotic food (kanamycin or similar) if fish is still eating",
            "Maintain pristine water quality in hospital tank",
            "WARNING: Dropsy has a very poor survival rate once pineconing is visible",
            "Consider euthanasia (clove oil method) if fish is suffering",
        ],
        "prevention": "Excellent water quality, varied diet, avoid stress",
        "contagious": False,
        "severity": "severe - often fatal",
    },
    "velvet": {
        "name": "Velvet Disease",
        "pathogen": "Oodinium pilularis (freshwater) / Amyloodinium ocellatum (marine)",
        "symptoms": ["gold/rusty dust-like coating on body", "clamped fins", "rapid breathing", "flashing/scratching", "lethargy", "loss of colour"],
        "cause": "Parasite, similar lifecycle to ich but harder to spot",
        "treatment": [
            "Dim lights / blackout tank (parasite needs light)",
            "Raise temperature to 28-30C gradually",
            "Copper-based medication (Seachem Cupramine) - LETHAL to invertebrates",
            "Alternative: Malachite green + formalin",
            "Treat for at least 14 days to break lifecycle",
            "Remove carbon from filter during treatment",
        ],
        "prevention": "Quarantine all new fish, maintain stable conditions",
        "contagious": True,
        "severity": "severe - can be fatal quickly, especially in marine tanks",
    },
    "swim_bladder": {
        "name": "Swim Bladder Disorder",
        "pathogen": "Not infectious - mechanical/dietary issue",
        "symptoms": ["floating at surface unable to dive", "sinking to bottom unable to rise", "swimming sideways or upside down", "bloated abdomen"],
        "cause": "Overfeeding, constipation, gulping air, poor diet, deformity (fancy goldfish), bacterial infection",
        "treatment": [
            "Fast the fish for 24-48 hours",
            "Then feed blanched, deshelled pea (acts as laxative)",
            "If constipation: Epsom salt bath (1 tsp per gallon, 15 min)",
            "Soak dry food before feeding to prevent air gulping",
            "If persistent: may be bacterial - try broad-spectrum antibiotic",
            "For fancy goldfish: switch to sinking pellets permanently",
        ],
        "prevention": "Don't overfeed, soak dry foods, feed varied diet, fast 1 day per week",
        "contagious": False,
        "severity": "mild-moderate - usually treatable",
    },
    "columnaris": {
        "name": "Columnaris (Cotton Wool Disease)",
        "pathogen": "Flavobacterium columnare",
        "symptoms": ["white/grey patches on body or mouth", "cotton-like growth on fins/mouth", "fin erosion", "gill damage", "rapid death in acute form"],
        "cause": "Bacterial; triggered by stress, high temperature, poor water quality, overcrowding",
        "treatment": [
            "LOWER temperature (columnaris thrives in warm water - opposite of ich!)",
            "Reduce to 22-24C if fish can tolerate",
            "Medicate: Furan-2 or kanamycin + nitrofurazone",
            "Salt dip (1 tbsp per gallon) can help",
            "Improve water quality immediately",
            "External: potassium permanganate or methylene blue dip",
        ],
        "prevention": "Avoid overcrowding, maintain water quality, reduce stress, quarantine new fish",
        "contagious": True,
        "severity": "severe - can kill within 24-48 hours in acute form",
    },
}


# ===========================================================================
# MCP Tools
# ===========================================================================


@mcp.tool()
def analyze_water_params(
    ph: float,
    ammonia_ppm: float,
    nitrite_ppm: float,
    nitrate_ppm: float,
    temperature_c: float,
    gh_dgh: Optional[float] = None,
    kh_dgh: Optional[float] = None,
    tank_type: str = "freshwater_tropical") -> dict:
    """Analyze aquarium water parameters and return health assessment.

    Compares readings against safe ranges for the tank type and provides
    specific actionable advice for any parameters out of range.

    Args:
        ph: pH level (0-14 scale).
        ammonia_ppm: Ammonia in parts per million (NH3/NH4+).
        nitrite_ppm: Nitrite in parts per million (NO2-).
        nitrate_ppm: Nitrate in parts per million (NO3-).
        temperature_c: Water temperature in Celsius.
        gh_dgh: General hardness in degrees (optional).
        kh_dgh: Carbonate hardness in degrees (optional).
        tank_type: One of: freshwater_tropical, freshwater_coldwater, marine_reef, marine_fowlr, brackish.

    Returns:
        Health assessment with parameter-by-parameter analysis and recommendations.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to Pro at https://fishkeeper.ai/pricing"}

    # Safe ranges by tank type
    ranges = {
        "freshwater_tropical": {
            "ph": (6.5, 7.5), "ammonia_ppm": (0, 0), "nitrite_ppm": (0, 0),
            "nitrate_ppm": (0, 40), "temperature_c": (24, 28), "gh_dgh": (4, 12), "kh_dgh": (3, 8),
        },
        "freshwater_coldwater": {
            "ph": (7.0, 8.0), "ammonia_ppm": (0, 0), "nitrite_ppm": (0, 0),
            "nitrate_ppm": (0, 40), "temperature_c": (15, 22), "gh_dgh": (6, 18), "kh_dgh": (4, 10),
        },
        "marine_reef": {
            "ph": (8.1, 8.4), "ammonia_ppm": (0, 0), "nitrite_ppm": (0, 0),
            "nitrate_ppm": (0, 5), "temperature_c": (24, 27), "gh_dgh": None, "kh_dgh": (7, 11),
        },
        "marine_fowlr": {
            "ph": (8.0, 8.4), "ammonia_ppm": (0, 0), "nitrite_ppm": (0, 0),
            "nitrate_ppm": (0, 20), "temperature_c": (24, 27), "gh_dgh": None, "kh_dgh": (7, 11),
        },
        "brackish": {
            "ph": (7.5, 8.5), "ammonia_ppm": (0, 0), "nitrite_ppm": (0, 0),
            "nitrate_ppm": (0, 30), "temperature_c": (24, 28), "gh_dgh": (10, 25), "kh_dgh": (8, 15),
        },
    }

    safe = ranges.get(tank_type)
    if not safe:
        return {"error": f"Unknown tank type. Options: {', '.join(ranges.keys())}"}

    params_analysis = []
    alerts = []
    overall_status = "healthy"

    def _check(name, value, safe_range, unit=""):
        nonlocal overall_status
        if safe_range is None or value is None:
            return
        low, high = safe_range
        status = "ok"
        advice = None

        if name == "ammonia_ppm":
            if value > 0:
                if value >= 1.0:
                    status = "critical"
                    overall_status = "critical"
                    advice = "EMERGENCY: Perform 50% water change immediately. Ammonia is acutely toxic. Dose Prime/Safe to detoxify. Check filter is running. Do NOT feed."
                elif value >= 0.25:
                    status = "danger"
                    if overall_status != "critical":
                        overall_status = "danger"
                    advice = "Perform 30-50% water change now. Dose water conditioner (Prime/Safe). Check filtration. Tank may not be cycled."
                else:
                    status = "warning"
                    if overall_status in ("healthy"):
                        overall_status = "warning"
                    advice = "Trace ammonia detected. Do a 25% water change. Monitor daily. May indicate cycle disruption."
        elif name == "nitrite_ppm":
            if value > 0:
                if value >= 1.0:
                    status = "critical"
                    overall_status = "critical"
                    advice = "EMERGENCY: Nitrite is toxic. 50% water change now. Add aquarium salt (1 tsp/gallon) to block nitrite uptake through gills. Dose Prime."
                elif value >= 0.25:
                    status = "danger"
                    if overall_status != "critical":
                        overall_status = "danger"
                    advice = "Perform 30% water change. Add salt (1 tsp per 5 gallons). Tank is still cycling or cycle crashed."
                else:
                    status = "warning"
                    if overall_status in ("healthy"):
                        overall_status = "warning"
                    advice = "Trace nitrite. 25% water change, monitor daily."
        elif name == "nitrate_ppm":
            if value > high:
                if value > 80:
                    status = "danger"
                    if overall_status in ("healthy", "warning"):
                        overall_status = "danger"
                    advice = f"Nitrate very high. Do multiple 25% water changes over several days (don't shock fish). Reduce feeding. Add live plants. Clean substrate."
                else:
                    status = "warning"
                    if overall_status in ("healthy"):
                        overall_status = "warning"
                    advice = f"Nitrate above ideal ({high} ppm max for {tank_type}). Do a 25-30% water change. Consider more plants or reducing stock."
        elif name == "ph":
            if value < low:
                status = "warning"
                if overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"pH low ({value}). Check KH (buffering capacity). Crushed coral or baking soda can raise pH. Do NOT adjust more than 0.2 per day."
            elif value > high:
                status = "warning"
                if overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"pH high ({value}). Can lower with driftwood, peat, or Indian almond leaves. Stable pH is more important than perfect pH."
        elif name == "temperature_c":
            if value < low:
                status = "warning" if value > low - 3 else "danger"
                if status == "danger" and overall_status not in ("critical"):
                    overall_status = "danger"
                elif overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"Temperature low ({value}C). Check heater is working and correctly set. For {tank_type}, aim for {low}-{high}C."
            elif value > high:
                status = "warning" if value < high + 3 else "danger"
                if status == "danger" and overall_status not in ("critical"):
                    overall_status = "danger"
                elif overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"Temperature high ({value}C). Increase surface agitation for oxygenation. Float ice packs in bag if needed."
        else:
            if value < low:
                status = "warning"
                if overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"{name} below ideal range ({low}-{high})."
            elif value > high:
                status = "warning"
                if overall_status in ("healthy"):
                    overall_status = "warning"
                advice = f"{name} above ideal range ({low}-{high})."

        entry = {"parameter": name, "value": value, "safe_range": f"{low}-{high}{unit}", "status": status}
        if advice:
            entry["advice"] = advice
            alerts.append({"parameter": name, "severity": status, "message": advice})
        params_analysis.append(entry)

    _check("ph", ph, safe["ph"])
    _check("ammonia_ppm", ammonia_ppm, safe["ammonia_ppm"], " ppm")
    _check("nitrite_ppm", nitrite_ppm, safe["nitrite_ppm"], " ppm")
    _check("nitrate_ppm", nitrate_ppm, safe["nitrate_ppm"], " ppm")
    _check("temperature_c", temperature_c, safe["temperature_c"], "C")
    if gh_dgh is not None:
        _check("gh_dgh", gh_dgh, safe["gh_dgh"], " dGH")
    if kh_dgh is not None:
        _check("kh_dgh", kh_dgh, safe["kh_dgh"], " dKH")

    return {
        "overall_status": overall_status,
        "tank_type": tank_type,
        "parameters": params_analysis,
        "alerts": alerts,
        "recommendation": {
            "healthy": "Parameters look good. Continue regular maintenance schedule.",
            "warning": "Some parameters need attention. Follow advice above. Re-test in 24-48 hours.",
            "danger": "Urgent action needed. Perform water changes as advised. Re-test in 12-24 hours.",
            "critical": "EMERGENCY. Act immediately. Fish lives at risk. Follow critical advice NOW.",
        }[overall_status],
        "powered_by": "fishkeeper.ai",
    }


@mcp.tool()
def identify_fish(
    description: Optional[str] = None,
    species_name: Optional[str] = None) -> dict:
    """Identify fish species and return detailed care requirements.

    Search by common name, scientific name, or physical description.

    Args:
        description: Physical description or partial name to search for.
        species_name: Known species name (common or scientific).

    Returns:
        Species details including care requirements, water parameters, compatibility.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    search = (species_name or description or "").lower()
    if not search:
        return {"error": "Provide a description or species_name to search."}

    matches = []
    for sp_id, sp in _SPECIES_DB.items():
        searchable = f"{sp['common_name']} {sp['scientific_name']} {sp['family']} {sp.get('notes', '')}".lower()
        if search in searchable or search in sp_id:
            matches.append({"species_id": sp_id, **sp})

    if not matches:
        return {
            "results": [],
            "count": 0,
            "suggestion": f"No match for '{search}'. Try common names like 'neon tetra', 'betta', 'guppy', 'angelfish', 'clownfish', 'goldfish'.",
            "available_species": [sp["common_name"] for sp in _SPECIES_DB.values()],
        }

    return {
        "results": matches,
        "count": len(matches),
        "powered_by": "fishkeeper.ai",
    }


@mcp.tool()
def check_compatibility(species_list: list[str]) -> dict:
    """Check if multiple fish species are compatible in the same tank.

    Analyzes temperament, water parameter overlap, size differences,
    and known compatibility issues.

    Args:
        species_list: List of species IDs or common names to check together.

    Returns:
        Compatibility matrix with warnings and recommended tank parameters.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    if len(species_list) < 2:
        return {"error": "Provide at least 2 species to check compatibility."}

    # Resolve species
    resolved = []
    for name in species_list:
        found = None
        search = name.lower().replace(" ", "_")
        # Try direct ID match first
        if search in _SPECIES_DB:
            found = (search, _SPECIES_DB[search])
        else:
            # Search by name
            for sp_id, sp in _SPECIES_DB.items():
                if name.lower() in sp["common_name"].lower() or name.lower() in sp["scientific_name"].lower():
                    found = (sp_id, sp)
                    break
        if found:
            resolved.append(found)
        else:
            return {"error": f"Species '{name}' not found. Use identify_fish to search."}

    issues = []
    warnings = []
    overall = "compatible"

    # Check pairwise compatibility
    for i, (id_a, sp_a) in enumerate(resolved):
        for j, (id_b, sp_b) in enumerate(resolved):
            if i >= j:
                continue

            name_a = sp_a["common_name"]
            name_b = sp_b["common_name"]

            # Check known incompatibilities
            a_incompat = " ".join(sp_a["incompatible_with"]).lower()
            b_incompat = " ".join(sp_b["incompatible_with"]).lower()

            for keyword in sp_b["common_name"].lower().split():
                if keyword in a_incompat and len(keyword) > 3:
                    issues.append(f"{name_a} is listed as incompatible with {name_b}")
                    overall = "incompatible"
                    break
            for keyword in sp_a["common_name"].lower().split():
                if keyword in b_incompat and len(keyword) > 3:
                    issues.append(f"{name_b} is listed as incompatible with {name_a}")
                    overall = "incompatible"
                    break

            # Check temperament conflicts
            if sp_a["temperament"] == "aggressive" and sp_b["temperament"] == "peaceful":
                issues.append(f"{name_a} (aggressive) may bully/eat {name_b} (peaceful)")
                overall = "incompatible"
            elif sp_b["temperament"] == "aggressive" and sp_a["temperament"] == "peaceful":
                issues.append(f"{name_b} (aggressive) may bully/eat {name_a} (peaceful)")
                overall = "incompatible"

            # Check size disparity (predation risk)
            size_ratio = max(sp_a["adult_size_cm"], sp_b["adult_size_cm"]) / max(min(sp_a["adult_size_cm"], sp_b["adult_size_cm"]), 1)
            if size_ratio > 4:
                smaller = name_a if sp_a["adult_size_cm"] < sp_b["adult_size_cm"] else name_b
                larger = name_b if smaller == name_a else name_a
                issues.append(f"Size mismatch: {larger} may eat {smaller} (size ratio {size_ratio:.1f}x)")
                if overall != "incompatible":
                    overall = "risky"
            elif size_ratio > 2.5:
                warnings.append(f"Moderate size difference between {name_a} and {name_b}")

            # Check water parameter overlap
            params_a = sp_a["water_params"]
            params_b = sp_b["water_params"]

            for param in ["temp_c", "ph"]:
                range_a = params_a.get(param)
                range_b = params_b.get(param)
                if range_a and range_b:
                    overlap_low = max(range_a[0], range_b[0])
                    overlap_high = min(range_a[1], range_b[1])
                    if overlap_low > overlap_high:
                        issues.append(f"No {param} overlap: {name_a} needs {range_a}, {name_b} needs {range_b}")
                        overall = "incompatible"
                    elif overlap_high - overlap_low < 1:
                        warnings.append(f"Narrow {param} overlap between {name_a} and {name_b}: {overlap_low}-{overlap_high}")

    # Calculate overlapping parameter ranges for all species
    if overall != "incompatible":
        all_temp = [(sp["water_params"]["temp_c"][0], sp["water_params"]["temp_c"][1]) for _, sp in resolved]
        all_ph = [(sp["water_params"]["ph"][0], sp["water_params"]["ph"][1]) for _, sp in resolved]

        target_temp = (max(t[0] for t in all_temp), min(t[1] for t in all_temp))
        target_ph = (max(p[0] for p in all_ph), min(p[1] for p in all_ph))

        min_tank = max(sp["min_tank_litres"] for _, sp in resolved)
        # Add space for each additional species group
        recommended_tank = min_tank + sum(sp["min_tank_litres"] * 0.5 for _, sp in resolved[1:])

        recommended_params = {
            "temperature_c": f"{target_temp[0]}-{target_temp[1]}" if target_temp[0] <= target_temp[1] else "NO OVERLAP",
            "ph": f"{target_ph[0]}-{target_ph[1]}" if target_ph[0] <= target_ph[1] else "NO OVERLAP",
            "minimum_tank_litres": int(recommended_tank),
            "minimum_tank_gallons": int(recommended_tank * 0.264),
        }
    else:
        recommended_params = None

    if not issues and not warnings:
        overall = "compatible"

    return {
        "overall_compatibility": overall,
        "species_checked": [sp["common_name"] for _, sp in resolved],
        "issues": issues,
        "warnings": warnings,
        "recommended_parameters": recommended_params,
        "swim_level_distribution": {
            "top": [sp["common_name"] for _, sp in resolved if "top" in sp["swim_level"]],
            "middle": [sp["common_name"] for _, sp in resolved if "middle" in sp["swim_level"]],
            "bottom": [sp["common_name"] for _, sp in resolved if "bottom" in sp["swim_level"]],
        },
        "powered_by": "fishkeeper.ai",
    }


@mcp.tool()
def diagnose_disease(
    symptoms: list[str],
    species: Optional[str] = None,
    water_params: Optional[dict] = None) -> dict:
    """Diagnose fish disease from symptoms and suggest treatments.

    Matches symptoms against a database of common aquarium diseases and
    provides treatment protocols.

    Args:
        symptoms: List of observed symptoms (e.g. ["white spots", "flashing", "loss of appetite"]).
        species: Affected species name (for species-specific advice).
        water_params: Optional dict with current water parameters (ph, ammonia_ppm, etc).

    Returns:
        Possible diagnoses ranked by symptom match, with treatment plans.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    if not symptoms:
        return {"error": "Provide at least one symptom to diagnose."}

    symptom_text = " ".join(s.lower() for s in symptoms)
    matches = []

    for disease_id, disease in _DISEASES.items():
        score = 0
        matched_symptoms = []
        for ds in disease["symptoms"]:
            ds_lower = ds.lower()
            # Check if any words in the disease symptom match input symptoms
            for input_s in symptoms:
                input_lower = input_s.lower()
                if input_lower in ds_lower or ds_lower in input_lower:
                    score += 2
                    matched_symptoms.append(ds)
                    break
                # Partial word matching
                input_words = set(input_lower.split())
                ds_words = set(ds_lower.split())
                overlap = input_words & ds_words
                if len(overlap) >= 1 and any(len(w) > 3 for w in overlap):
                    score += 1
                    matched_symptoms.append(ds)
                    break

        if score > 0:
            matches.append({
                "disease": disease["name"],
                "match_score": score,
                "matched_symptoms": list(set(matched_symptoms)),
                "all_symptoms": disease["symptoms"],
                "pathogen": disease["pathogen"],
                "cause": disease["cause"],
                "treatment": disease["treatment"],
                "prevention": disease["prevention"],
                "contagious": disease["contagious"],
                "severity": disease["severity"],
            })

    matches.sort(key=lambda x: -x["match_score"])

    # Water quality note
    water_note = None
    if water_params:
        ammonia = water_params.get("ammonia_ppm", 0)
        nitrite = water_params.get("nitrite_ppm", 0)
        if ammonia > 0 or nitrite > 0:
            water_note = (
                "WARNING: Ammonia/nitrite detected. Poor water quality is the #1 cause of fish disease. "
                "Fix water parameters FIRST before medicating. Many diseases resolve with clean water alone."
            )

    return {
        "possible_diagnoses": matches[:3],
        "symptoms_provided": symptoms,
        "species": species,
        "water_quality_note": water_note or "Always test water when fish are sick - most disease is triggered by poor water quality.",
        "general_advice": [
            "Isolate sick fish in a hospital tank if possible",
            "Test water parameters immediately (ammonia, nitrite, nitrate, pH, temp)",
            "Do NOT add multiple medications at once",
            "Remove activated carbon from filter before medicating",
            "Increase aeration during treatment",
        ],
        "powered_by": "fishkeeper.ai",
    }


@mcp.tool()
def calculate_stocking(
    tank_litres: float,
    tank_length_cm: Optional[float] = None,
    species_list: Optional[list[dict]] = None,
    filtration_quality: str = "standard",
    planted: bool = False) -> dict:
    """Calculate maximum fish stocking for a tank.

    Uses a combination of inch-per-gallon baseline, bioload weighting,
    swimming space requirements, and filtration capacity.

    Args:
        tank_litres: Tank volume in litres.
        tank_length_cm: Tank length in cm (important for active swimmers).
        species_list: List of dicts with "species_id" and "count" keys.
        filtration_quality: One of "minimal", "standard", "excellent", "over-filtered".
        planted: Whether tank has live plants (improves capacity slightly).

    Returns:
        Stocking assessment with bioload percentage and recommendations.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    gallons = tank_litres * 0.264
    filtration_multiplier = {
        "minimal": 0.7,
        "standard": 1.0,
        "excellent": 1.2,
        "over-filtered": 1.4,
    }.get(filtration_quality, 1.0)

    plant_bonus = 1.1 if planted else 1.0

    # Effective capacity
    effective_gallons = gallons * filtration_multiplier * plant_bonus

    # Classic rule: 1 inch of fish per gallon (tropical) / 1 inch per 2 gallons (goldfish)
    max_inches_tropical = effective_gallons
    max_inches_coldwater = effective_gallons * 0.5

    if not species_list:
        return {
            "tank_volume_litres": tank_litres,
            "tank_volume_gallons": round(gallons, 1),
            "effective_capacity_gallons": round(effective_gallons, 1),
            "stocking_guideline": {
                "tropical_max_total_inches": round(max_inches_tropical, 1),
                "coldwater_max_total_inches": round(max_inches_coldwater, 1),
            },
            "note": "Provide species_list with [{species_id, count}] for detailed analysis.",
            "powered_by": "fishkeeper.ai",
        }

    # Detailed analysis
    total_inches = 0
    total_bioload_score = 0
    species_details = []
    min_tank_needed = 0

    bioload_scores = {"low": 1.0, "medium": 2.0, "medium-high": 2.5, "high": 3.0, "very high": 4.0}

    for entry in species_list:
        sp_id = entry.get("species_id", "").lower().replace(" ", "_")
        count = entry.get("count", 1)

        sp = _SPECIES_DB.get(sp_id)
        if not sp:
            # Try name search
            for sid, s in _SPECIES_DB.items():
                if sp_id in s["common_name"].lower() or sp_id in sid:
                    sp = s
                    sp_id = sid
                    break

        if not sp:
            species_details.append({"species": entry.get("species_id"), "error": "Species not found"})
            continue

        inches = sp["adult_size_inches"] * count
        bioload = bioload_scores.get(sp["bioload"], 2.0) * count
        total_inches += inches
        total_bioload_score += bioload
        min_tank_needed = max(min_tank_needed, sp["min_tank_litres"])

        detail = {
            "species": sp["common_name"],
            "count": count,
            "adult_size_inches_each": sp["adult_size_inches"],
            "total_inches": round(inches, 1),
            "bioload": sp["bioload"],
            "min_school_size": sp["min_school_size"],
        }

        if count < sp["min_school_size"] and sp["min_school_size"] > 1:
            detail["warning"] = f"Need at least {sp['min_school_size']} for a proper school"

        species_details.append(detail)

    # Calculate stocking percentage
    stocking_pct = (total_inches / max_inches_tropical * 100) if max_inches_tropical > 0 else 999

    if stocking_pct <= 60:
        stocking_status = "lightly_stocked"
        advice = "Plenty of room. You could add more fish if desired."
    elif stocking_pct <= 80:
        stocking_status = "well_stocked"
        advice = "Good stocking level. Room for a few more small fish."
    elif stocking_pct <= 100:
        stocking_status = "fully_stocked"
        advice = "At capacity. Maintain excellent filtration and regular water changes."
    elif stocking_pct <= 120:
        stocking_status = "overstocked"
        advice = "Over recommended limits. Increase filtration and water change frequency. Consider upgrading tank."
    else:
        stocking_status = "critically_overstocked"
        advice = "Severely overstocked. Fish health will suffer. Rehome some fish or upgrade tank urgently."

    tank_size_ok = tank_litres >= min_tank_needed

    return {
        "tank_volume_litres": tank_litres,
        "tank_volume_gallons": round(gallons, 1),
        "filtration": filtration_quality,
        "planted": planted,
        "species": species_details,
        "stocking_analysis": {
            "total_fish_inches": round(total_inches, 1),
            "max_recommended_inches": round(max_inches_tropical, 1),
            "stocking_percentage": round(stocking_pct, 1),
            "status": stocking_status,
            "bioload_score": round(total_bioload_score, 1),
        },
        "tank_size_adequate": tank_size_ok,
        "min_tank_needed_litres": min_tank_needed,
        "advice": advice,
        "maintenance_note": {
            "lightly_stocked": "Weekly 20% water change recommended",
            "well_stocked": "Weekly 25% water change recommended",
            "fully_stocked": "Weekly 30-40% water change recommended",
            "overstocked": "Twice-weekly 30% water changes needed",
            "critically_overstocked": "Urgent: daily water changes until stock reduced",
        }[stocking_status],
        "powered_by": "fishkeeper.ai",
    }


@mcp.tool()
def get_feeding_schedule(
    species_list: list[str],
    tank_type: str = "freshwater_tropical") -> dict:
    """Generate a feeding schedule based on species mix.

    Creates a practical daily/weekly feeding plan accounting for different
    dietary needs, swim levels, and feeding behaviors.

    Args:
        species_list: List of species IDs or common names in the tank.
        tank_type: Tank type for context (freshwater_tropical, freshwater_coldwater, marine_reef).

    Returns:
        Detailed feeding schedule with food types, amounts, and timing.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    if not species_list:
        return {"error": "Provide at least one species."}

    resolved = []
    for name in species_list:
        search = name.lower().replace(" ", "_")
        sp = _SPECIES_DB.get(search)
        if not sp:
            for sid, s in _SPECIES_DB.items():
                if name.lower() in s["common_name"].lower() or name.lower() in sid:
                    sp = s
                    break
        if sp:
            resolved.append(sp)

    if not resolved:
        return {"error": "No recognized species found. Use identify_fish to look up species."}

    # Determine diet types present
    diets = set(sp["diet"] for sp in resolved)
    swim_levels = set(sp["swim_level"] for sp in resolved)

    # Build schedule
    morning_feeds = []
    evening_feeds = []
    weekly_supplements = []
    shopping_list = set()

    has_bottom = any("bottom" in sp["swim_level"] for sp in resolved)
    has_herbivore = any("herbivore" in sp["diet"] for sp in resolved)
    has_carnivore = any(sp["diet"] == "carnivore" for sp in resolved)

    # Morning feed
    morning_feeds.append({
        "time": "08:00-09:00",
        "food": "High-quality flake or micro pellet",
        "amount": "What fish consume in 2 minutes",
        "notes": "Crush flake for small-mouthed species",
    })
    shopping_list.add("quality flake food")

    if has_bottom:
        morning_feeds.append({
            "time": "08:00 (simultaneous)",
            "food": "Sinking pellets/wafers for bottom dwellers",
            "amount": "1 wafer per 3-4 bottom feeders",
            "notes": "Drop in after surface feeders are occupied with flake",
        })
        shopping_list.add("sinking catfish wafers")

    # Evening feed
    evening_feeds.append({
        "time": "18:00-19:00",
        "food": "Varied from morning - alternate between pellet and frozen",
        "amount": "Slightly less than morning feed",
        "notes": "Feed at least 1 hour before lights out",
    })

    if has_carnivore:
        evening_feeds.append({
            "time": "18:00",
            "food": "Frozen bloodworm or brine shrimp (thawed)",
            "amount": "Small cube, enough for 2 min consumption",
            "notes": "Carnivores and most fish love frozen foods",
        })
        shopping_list.add("frozen bloodworm")
        shopping_list.add("frozen brine shrimp")

    # Weekly supplements
    weekly_supplements.append({
        "day": "Wednesday",
        "food": "Frozen food treat (daphnia, brine shrimp, or bloodworm)",
        "notes": "Thaw in tank water before adding. Excellent for colour and health.",
    })
    shopping_list.add("frozen daphnia")

    if has_herbivore:
        weekly_supplements.append({
            "day": "Saturday",
            "food": "Blanched vegetable (courgette, cucumber, pea, spinach)",
            "amount": "1 slice, remove uneaten after 4 hours",
            "notes": "Weigh down with plant weight or fork. Plecos love courgette.",
        })
        shopping_list.add("fresh courgette/cucumber")

    weekly_supplements.append({
        "day": "Sunday",
        "food": "FASTING DAY - no food",
        "notes": "Weekly fast aids digestion, reduces waste, mimics natural conditions. Fish can easily go 2-3 days without food.",
    })

    # Species-specific notes
    species_notes = []
    for sp in resolved:
        feeding_info = sp.get("feeding", {})
        if feeding_info:
            species_notes.append({
                "species": sp["common_name"],
                "preferred_food": feeding_info.get("type", "general"),
                "frequency": feeding_info.get("frequency", "2x daily"),
                "amount": feeding_info.get("amount", "moderate"),
            })

    return {
        "schedule": {
            "morning": morning_feeds,
            "evening": evening_feeds,
            "weekly_supplements": weekly_supplements,
        },
        "species_specific": species_notes,
        "shopping_list": sorted(shopping_list),
        "general_rules": [
            "Feed only what fish consume in 2-3 minutes",
            "Remove uneaten food after 5 minutes to prevent water fouling",
            "Vary diet throughout the week for best health and colour",
            "Fast 1 day per week (healthy for most species)",
            "Soak dried foods briefly before feeding to prevent swim bladder issues",
            "Feed bottom dwellers separately - sinking food AFTER surface feeders are eating",
            "Holiday: fish are fine for 3-5 days without food. Use auto-feeder for longer.",
        ],
        "overfeeding_warning": "Overfeeding is the #1 cause of water quality problems. When in doubt, feed less.",
        "powered_by": "fishkeeper.ai",
    }


if __name__ == "__main__":
    mcp.run()
