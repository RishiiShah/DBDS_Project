from __future__ import annotations

from copy import deepcopy


def root(name, *children):
    return {"name": name, "children": list(children)}


def branch(name, *leaves):
    return {"name": name, "leaves": list(leaves)}


def leaf(name, required_fields):
    return {"name": name, "required_fields": list(required_fields)}


def product(name, condition="good", **attrs):
    return {
        "name": name,
        "condition": condition,
        "attrs": {key: str(value) for key, value in attrs.items()},
    }


SEED_USERS = [
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
    },
    {
        "username": "janesmith",
        "email": "jane@example.com",
        "password": "password",
        "first_name": "Jane",
        "last_name": "Smith",
        "role": "user",
    },
    {
        "username": "alice",
        "email": "alice@example.com",
        "password": "password",
        "first_name": "Alice",
        "last_name": "Walker",
        "role": "user",
    },
    {
        "username": "bob",
        "email": "bob@example.com",
        "password": "password",
        "first_name": "Bob",
        "last_name": "Jones",
        "role": "user",
    },
    {
        "username": "maya",
        "email": "maya@example.com",
        "password": "password",
        "first_name": "Maya",
        "last_name": "Patel",
        "role": "user",
    },
    {
        "username": "carlos",
        "email": "carlos@example.com",
        "password": "password",
        "first_name": "Carlos",
        "last_name": "Rivera",
        "role": "user",
    },
    {
        "username": "priya",
        "email": "priya@example.com",
        "password": "password",
        "first_name": "Priya",
        "last_name": "Nair",
        "role": "user",
    },
    {
        "username": "ethan",
        "email": "ethan@example.com",
        "password": "password",
        "first_name": "Ethan",
        "last_name": "Brooks",
        "role": "user",
    },
]


SELLER_USERNAMES = [user["username"] for user in SEED_USERS]
ROOT_LISTING_MULTIPLIERS = {
    "Electronics": 2,
}


CATEGORY_TREE = [
    root(
        "Electronics",
        branch(
            "Computers",
            leaf("Laptops", ["brand", "ram", "storage", "screen_size", "cpu", "os"]),
            leaf("Desktops", ["brand", "ram", "storage", "cpu", "gpu", "form_factor"]),
            leaf("Monitors", ["brand", "size", "resolution", "panel_type", "refresh_rate"]),
        ),
        branch(
            "Mobile",
            leaf("Smartphones", ["brand", "os", "screen_size", "storage", "ram", "battery"]),
            leaf("Tablets", ["brand", "os", "screen_size", "storage", "ram", "connectivity"]),
            leaf("Smartwatches", ["brand", "compatibility", "case_size", "battery_life", "connectivity"]),
        ),
        branch(
            "Audio",
            leaf("Headphones", ["brand", "type", "wireless", "noise_cancelling", "color"]),
            leaf("Speakers", ["brand", "type", "connectivity", "power", "color"]),
        ),
        branch(
            "Gaming",
            leaf("Consoles", ["brand", "model", "storage", "generation", "format"]),
        ),
    ),
    root(
        "Sporting Goods",
        branch(
            "Cycling",
            leaf("Bikes", ["brand", "type", "frame_size", "frame_material", "gears", "wheel_size"]),
        ),
        branch(
            "Fitness",
            leaf("Cardio Equipment", ["brand", "type", "max_user_weight", "foldable", "resistance_type"]),
        ),
        branch(
            "Outdoor & Adventure",
            leaf("Camping Gear", ["brand", "type", "capacity", "material", "season_rating"]),
        ),
        branch(
            "Team Sports",
            leaf("Basketball", ["brand", "size", "material", "indoor_outdoor"]),
        ),
    ),
    root(
        "Home & Kitchen",
        branch(
            "Coffee & Kitchen",
            leaf("Espresso Machines", ["brand", "type", "capacity", "finish", "power"]),
            leaf("Stand Mixers", ["brand", "bowl_capacity", "speed_settings", "color", "power"]),
            leaf("Air Fryers", ["brand", "capacity", "finish", "power", "preset_count"]),
        ),
        branch(
            "Home Care",
            leaf("Vacuum Cleaners", ["brand", "type", "capacity", "power", "cordless"]),
        ),
    ),
    root(
        "Fashion",
        branch(
            "Footwear",
            leaf("Sneakers", ["brand", "size", "color", "material", "style"]),
        ),
        branch(
            "Accessories",
            leaf("Watches", ["brand", "movement", "band_material", "case_size", "water_resistance"]),
            leaf("Handbags", ["brand", "material", "color", "style", "size"]),
        ),
        branch(
            "Apparel",
            leaf("Outerwear", ["brand", "size", "color", "material", "style"]),
        ),
    ),
    root(
        "Collectibles",
        branch(
            "Cards",
            leaf("Trading Cards", ["brand", "franchise", "year", "condition_grade", "set_name"]),
        ),
        branch(
            "Comics",
            leaf("Comic Books", ["publisher", "franchise", "year", "condition_grade", "issue_number"]),
        ),
        branch(
            "Figures",
            leaf("Action Figures", ["brand", "franchise", "scale", "material", "boxed"]),
        ),
        branch(
            "Memorabilia",
            leaf("Memorabilia", ["franchise", "year", "signed", "material", "display_type"]),
        ),
    ),
    root(
        "Books & Media",
        branch(
            "Music",
            leaf("Vinyl Records", ["artist", "genre", "format", "pressing", "condition_grade"]),
        ),
        branch(
            "Games",
            leaf("Board Games", ["brand", "player_count", "play_time", "genre", "edition"]),
        ),
        branch(
            "Entertainment",
            leaf("Box Sets", ["franchise", "format", "edition", "region", "condition_grade"]),
        ),
    ),
    root(
        "Automotive",
        branch(
            "In-Car Tech",
            leaf("Car Electronics", ["brand", "compatibility", "power", "connectivity", "condition_grade"]),
        ),
        branch(
            "Detailing",
            leaf("Detailing Tools", ["brand", "type", "power", "material", "condition_grade"]),
        ),
        branch(
            "Garage",
            leaf("Garage Equipment", ["brand", "type", "capacity", "material", "condition_grade"]),
        ),
    ),
    root(
        "Office & Creative",
        branch(
            "Workspace",
            leaf("Desks", ["brand", "width", "material", "color", "adjustable"]),
            leaf("Office Chairs", ["brand", "material", "color", "adjustable", "weight_capacity"]),
        ),
        branch(
            "Imaging",
            leaf("Cameras", ["brand", "sensor", "lens_mount", "resolution", "condition_grade"]),
        ),
    ),
]


LEAF_INVENTORY = {
    "Laptops": {
        "base_price": 980,
        "items": [
            product("Apple MacBook Pro 14 M3", "like_new", brand="Apple", ram="16GB", storage="512GB SSD", screen_size='14"', cpu="Apple M3", os="macOS"),
            product("Dell XPS 15 OLED", "good", brand="Dell", ram="32GB", storage="1TB SSD", screen_size='15.6"', cpu="Intel i9-13900H", os="Windows 11"),
            product("Lenovo ThinkPad X1 Carbon Gen 11", "good", brand="Lenovo", ram="16GB", storage="1TB SSD", screen_size='14"', cpu="Intel i7-1365U", os="Windows 11 Pro"),
            product("HP Spectre x360 14", "like_new", brand="HP", ram="16GB", storage="1TB SSD", screen_size='13.5"', cpu="Intel i7-1355U", os="Windows 11"),
            product("ASUS ROG Zephyrus G14", "good", brand="ASUS", ram="32GB", storage="1TB SSD", screen_size='14"', cpu="AMD Ryzen 9 8945HS", os="Windows 11"),
        ],
    },
    "Desktops": {
        "base_price": 1100,
        "items": [
            product("Apple iMac 24 M3", "like_new", brand="Apple", ram="16GB", storage="512GB SSD", cpu="Apple M3", gpu="Integrated 10-core GPU", form_factor="All-in-One"),
            product("Alienware Aurora R16", "good", brand="Alienware", ram="32GB", storage="2TB SSD", cpu="Intel i7-14700F", gpu="RTX 4070 Super", form_factor="Tower"),
            product("Dell OptiPlex 7010 Plus", "good", brand="Dell", ram="16GB", storage="512GB SSD", cpu="Intel i5-13500", gpu="Intel UHD 770", form_factor="Small Form Factor"),
            product("HP Omen 45L", "good", brand="HP", ram="32GB", storage="1TB SSD", cpu="Intel i9-14900K", gpu="RTX 4080", form_factor="Full Tower"),
            product("Lenovo Legion T5", "fair", brand="Lenovo", ram="16GB", storage="1TB SSD", cpu="AMD Ryzen 7 7700", gpu="RTX 4060 Ti", form_factor="Mid Tower"),
        ],
    },
    "Monitors": {
        "base_price": 320,
        "items": [
            product("Dell UltraSharp U2723QE", "like_new", brand="Dell", size='27"', resolution="4K", panel_type="IPS Black", refresh_rate="60Hz"),
            product("LG UltraGear 27GR95QE", "good", brand="LG", size='27"', resolution="1440p", panel_type="OLED", refresh_rate="240Hz"),
            product("Samsung Odyssey G7 32", "good", brand="Samsung", size='32"', resolution="1440p", panel_type="VA", refresh_rate="240Hz"),
            product("ASUS ProArt PA279CV", "like_new", brand="ASUS", size='27"', resolution="4K", panel_type="IPS", refresh_rate="60Hz"),
            product("BenQ MOBIUZ EX2710U", "good", brand="BenQ", size='27"', resolution="4K", panel_type="IPS", refresh_rate="144Hz"),
        ],
    },
    "Smartphones": {
        "base_price": 720,
        "items": [
            product("iPhone 15 Pro 256GB", "like_new", brand="Apple", os="iOS 18", screen_size='6.1"', storage="256GB", ram="8GB", battery="3274mAh"),
            product("Samsung Galaxy S24 Ultra", "good", brand="Samsung", os="Android 14", screen_size='6.8"', storage="512GB", ram="12GB", battery="5000mAh"),
            product("Google Pixel 8 Pro", "good", brand="Google", os="Android 14", screen_size='6.7"', storage="256GB", ram="12GB", battery="5050mAh"),
            product("OnePlus 12", "like_new", brand="OnePlus", os="Android 14", screen_size='6.82"', storage="512GB", ram="16GB", battery="5400mAh"),
            product("Nothing Phone (2)", "good", brand="Nothing", os="Android 14", screen_size='6.7"', storage="256GB", ram="12GB", battery="4700mAh"),
        ],
    },
    "Tablets": {
        "base_price": 540,
        "items": [
            product("iPad Pro 11 M4", "like_new", brand="Apple", os="iPadOS 18", screen_size='11"', storage="256GB", ram="8GB", connectivity="Wi-Fi"),
            product("Samsung Galaxy Tab S9+", "good", brand="Samsung", os="Android 14", screen_size='12.4"', storage="512GB", ram="12GB", connectivity="Wi-Fi"),
            product("Microsoft Surface Pro 10", "good", brand="Microsoft", os="Windows 11", screen_size='13"', storage="512GB", ram="16GB", connectivity="Wi-Fi"),
            product("Lenovo Tab P12 Pro", "good", brand="Lenovo", os="Android 14", screen_size='12.7"', storage="256GB", ram="8GB", connectivity="Wi-Fi"),
            product("OnePlus Pad 2", "like_new", brand="OnePlus", os="Android 14", screen_size='12.1"', storage="256GB", ram="12GB", connectivity="Wi-Fi"),
        ],
    },
    "Smartwatches": {
        "base_price": 260,
        "items": [
            product("Apple Watch Series 10", "like_new", brand="Apple", compatibility="iPhone", case_size="45mm", battery_life="18 hours", connectivity="GPS"),
            product("Samsung Galaxy Watch Ultra", "good", brand="Samsung", compatibility="Android", case_size="47mm", battery_life="60 hours", connectivity="LTE"),
            product("Google Pixel Watch 3", "good", brand="Google", compatibility="Android", case_size="41mm", battery_life="24 hours", connectivity="Wi-Fi"),
            product("Garmin Venu 3", "like_new", brand="Garmin", compatibility="iOS/Android", case_size="45mm", battery_life="14 days", connectivity="Bluetooth"),
            product("OnePlus Watch 2", "good", brand="OnePlus", compatibility="Android", case_size="47mm", battery_life="100 hours", connectivity="Wi-Fi"),
        ],
    },
    "Headphones": {
        "base_price": 220,
        "items": [
            product("Sony WH-1000XM5", "like_new", brand="Sony", type="Over-ear", wireless="Yes", noise_cancelling="Yes", color="Black"),
            product("Bose QuietComfort Ultra", "good", brand="Bose", type="Over-ear", wireless="Yes", noise_cancelling="Yes", color="Sandstone"),
            product("Apple AirPods Pro 2 USB-C", "good", brand="Apple", type="In-ear", wireless="Yes", noise_cancelling="Yes", color="White"),
            product("Sennheiser Momentum 4 Wireless", "like_new", brand="Sennheiser", type="Over-ear", wireless="Yes", noise_cancelling="Yes", color="Graphite"),
            product("SteelSeries Arctis Nova Pro Wireless", "good", brand="SteelSeries", type="Gaming headset", wireless="Yes", noise_cancelling="Hybrid", color="Black"),
        ],
    },
    "Speakers": {
        "base_price": 190,
        "items": [
            product("Sonos Era 300", "like_new", brand="Sonos", type="Smart Speaker", connectivity="Wi-Fi", power="AC", color="White"),
            product("Bose SoundLink Max", "good", brand="Bose", type="Portable Speaker", connectivity="Bluetooth", power="Battery", color="Black"),
            product("JBL Authentics 500", "good", brand="JBL", type="Home Speaker", connectivity="Wi-Fi", power="AC", color="Black"),
            product("Marshall Stanmore III", "like_new", brand="Marshall", type="Home Speaker", connectivity="Bluetooth", power="AC", color="Cream"),
            product("Ultimate Ears Hyperboom", "good", brand="Ultimate Ears", type="Party Speaker", connectivity="Bluetooth", power="Battery", color="Black"),
        ],
    },
    "Consoles": {
        "base_price": 360,
        "items": [
            product("PlayStation 5 Slim Disc Edition", "good", brand="Sony", model="PS5 Slim", storage="1TB", generation="9th Gen", format="Disc"),
            product("Xbox Series X 1TB", "good", brand="Microsoft", model="Xbox Series X", storage="1TB", generation="9th Gen", format="Digital + Disc"),
            product("Nintendo Switch OLED", "like_new", brand="Nintendo", model="Switch OLED", storage="64GB", generation="8th Gen", format="Hybrid"),
            product("Steam Deck OLED 1TB", "like_new", brand="Valve", model="Steam Deck OLED", storage="1TB", generation="Handheld", format="Digital"),
            product("ASUS ROG Ally Z1 Extreme", "good", brand="ASUS", model="ROG Ally", storage="512GB", generation="Handheld", format="Digital"),
        ],
    },
    "Bikes": {
        "base_price": 640,
        "items": [
            product("Trek Marlin 7", "like_new", brand="Trek", type="Mountain", frame_size='Medium 17.5"', frame_material="Aluminum", gears="12-speed", wheel_size='29"'),
            product("Specialized Sirrus 3.0", "good", brand="Specialized", type="Hybrid", frame_size='Large 56cm', frame_material="Aluminum", gears="18-speed", wheel_size="700c"),
            product("Giant Defy Advanced 2", "good", brand="Giant", type="Road", frame_size='Medium 54cm', frame_material="Carbon", gears="22-speed", wheel_size="700c"),
            product("Cannondale Trail 5", "good", brand="Cannondale", type="Mountain", frame_size='Large', frame_material="Aluminum", gears="10-speed", wheel_size='29"'),
            product("Santa Cruz Hightower C", "fair", brand="Santa Cruz", type="Trail", frame_size='Medium', frame_material="Carbon", gears="12-speed", wheel_size='29"'),
        ],
    },
    "Cardio Equipment": {
        "base_price": 540,
        "items": [
            product("Peloton Bike+", "good", brand="Peloton", type="Stationary Bike", max_user_weight="297 lbs", foldable="No", resistance_type="Magnetic"),
            product("NordicTrack T 6.5 Si", "good", brand="NordicTrack", type="Treadmill", max_user_weight="300 lbs", foldable="Yes", resistance_type="Incline + motorized"),
            product("Concept2 RowErg", "like_new", brand="Concept2", type="Rowing Machine", max_user_weight="500 lbs", foldable="No", resistance_type="Air"),
            product("AssaultRunner Pro", "good", brand="Assault Fitness", type="Curved Treadmill", max_user_weight="350 lbs", foldable="No", resistance_type="Manual"),
            product("Schwinn IC4", "like_new", brand="Schwinn", type="Indoor Cycle", max_user_weight="330 lbs", foldable="No", resistance_type="Magnetic"),
        ],
    },
    "Camping Gear": {
        "base_price": 180,
        "items": [
            product("REI Co-op Half Dome 2 Plus", "like_new", brand="REI Co-op", type="Backpacking Tent", capacity="2 person", material="Ripstop Nylon", season_rating="3-season"),
            product("Coleman Sundome 4-Person Tent", "good", brand="Coleman", type="Dome Tent", capacity="4 person", material="Polyester", season_rating="3-season"),
            product("Big Agnes Copper Spur HV UL3", "like_new", brand="Big Agnes", type="Ultralight Tent", capacity="3 person", material="Silnylon", season_rating="3-season"),
            product("NEMO Disco 15 Sleeping Bag", "good", brand="NEMO", type="Sleeping Bag", capacity="1 person", material="Down", season_rating="15F"),
            product("Marmot Limestone 6P", "good", brand="Marmot", type="Family Tent", capacity="6 person", material="Polyester", season_rating="3-season"),
        ],
    },
    "Basketball": {
        "base_price": 95,
        "items": [
            product("Spalding NBA Official Game Ball", "good", brand="Spalding", size='29.5"', material="Leather", indoor_outdoor="Indoor"),
            product("Wilson Evolution", "like_new", brand="Wilson", size='29.5"', material="Composite Leather", indoor_outdoor="Indoor"),
            product("Nike Elite Competition", "good", brand="Nike", size='28.5"', material="Composite Leather", indoor_outdoor="Indoor/Outdoor"),
            product("Molten BG4500", "good", brand="Molten", size='29.5"', material="Premium Composite", indoor_outdoor="Indoor"),
            product("Under Armour 495 Indoor/Outdoor", "fair", brand="Under Armour", size='29.5"', material="Rubber Composite", indoor_outdoor="Indoor/Outdoor"),
        ],
    },
    "Espresso Machines": {
        "base_price": 420,
        "items": [
            product("Breville Barista Express", "good", brand="Breville", type="Semi-automatic", capacity="2L", finish="Brushed Stainless", power="1600W"),
            product("DeLonghi La Specialista Arte", "like_new", brand="DeLonghi", type="Semi-automatic", capacity="1.7L", finish="Stainless", power="1550W"),
            product("Gaggia Classic Pro", "good", brand="Gaggia", type="Manual", capacity="2.1L", finish="Brushed Steel", power="1450W"),
            product("Breville Bambino Plus", "like_new", brand="Breville", type="Compact automatic", capacity="1.9L", finish="Black Truffle", power="1560W"),
            product("Philips 3200 LatteGo", "good", brand="Philips", type="Fully automatic", capacity="1.8L", finish="Matte Black", power="1500W"),
        ],
    },
    "Stand Mixers": {
        "base_price": 260,
        "items": [
            product("KitchenAid Artisan 5-Quart", "like_new", brand="KitchenAid", bowl_capacity="5 qt", speed_settings="10", color="Milkshake", power="325W"),
            product("Bosch Universal Plus", "good", brand="Bosch", bowl_capacity="6.5 qt", speed_settings="4", color="White", power="500W"),
            product("Ankarsrum Original", "like_new", brand="Ankarsrum", bowl_capacity="7 qt", speed_settings="Variable", color="Harmony Beige", power="600W"),
            product("Kenwood Chef XL", "good", brand="Kenwood", bowl_capacity="6.7 qt", speed_settings="Variable", color="Silver", power="1400W"),
            product("Cuisinart Precision SM-50", "good", brand="Cuisinart", bowl_capacity="5.5 qt", speed_settings="12", color="Pearl White", power="500W"),
        ],
    },
    "Air Fryers": {
        "base_price": 120,
        "items": [
            product("Ninja Foodi DZ201", "good", brand="Ninja", capacity="8 qt", finish="Gray", power="1690W", preset_count="6"),
            product("Instant Vortex Plus ClearCook", "like_new", brand="Instant", capacity="6 qt", finish="Black", power="1700W", preset_count="6"),
            product("COSORI Pro LE", "good", brand="COSORI", capacity="5 qt", finish="Matte Black", power="1500W", preset_count="9"),
            product("Philips Premium Airfryer XXL", "good", brand="Philips", capacity="7 qt", finish="Black", power="1725W", preset_count="7"),
            product("Breville Smart Oven Air Fryer Compact", "like_new", brand="Breville", capacity="18L", finish="Brushed Steel", power="1800W", preset_count="10"),
        ],
    },
    "Vacuum Cleaners": {
        "base_price": 240,
        "items": [
            product("Dyson V15 Detect", "like_new", brand="Dyson", type="Stick Vacuum", capacity="0.77L", power="660W", cordless="Yes"),
            product("Shark Stratos AZ3000", "good", brand="Shark", type="Upright Vacuum", capacity="1.7L", power="1416W", cordless="No"),
            product("Miele Classic C1 Turbo Team", "good", brand="Miele", type="Canister Vacuum", capacity="4.5L", power="1200W", cordless="No"),
            product("Roborock Q Revo", "like_new", brand="Roborock", type="Robot Vacuum", capacity="5L dock", power="60W", cordless="Yes"),
            product("Tineco Pure One S15", "good", brand="Tineco", type="Stick Vacuum", capacity="0.5L", power="500W", cordless="Yes"),
        ],
    },
    "Sneakers": {
        "base_price": 140,
        "items": [
            product("Nike Dunk Low Panda", "good", brand="Nike", size="US 10", color="Black/White", material="Leather", style="Lifestyle"),
            product("Adidas Samba OG", "like_new", brand="Adidas", size="US 9", color="Cloud White", material="Leather", style="Terrace"),
            product("New Balance 990v6", "good", brand="New Balance", size="US 11", color="Grey", material="Suede/Mesh", style="Runner"),
            product("ASICS Gel-Kayano 14", "like_new", brand="ASICS", size="US 9.5", color="Silver Green", material="Mesh", style="Runner"),
            product("Salomon XT-6", "good", brand="Salomon", size="US 10.5", color="Vanilla Ice", material="Textile", style="Trail"),
        ],
    },
    "Watches": {
        "base_price": 220,
        "items": [
            product("Tissot PRX Quartz", "like_new", brand="Tissot", movement="Quartz", band_material="Steel", case_size="40mm", water_resistance="100m"),
            product("Seiko Presage Cocktail Time", "good", brand="Seiko", movement="Automatic", band_material="Leather", case_size="40.5mm", water_resistance="50m"),
            product("Hamilton Khaki Field Mechanical", "good", brand="Hamilton", movement="Hand-wound", band_material="NATO", case_size="38mm", water_resistance="50m"),
            product("Casio G-Shock GM-2100", "like_new", brand="Casio", movement="Quartz", band_material="Resin", case_size="44.4mm", water_resistance="200m"),
            product("Orient Bambino Version 8", "good", brand="Orient", movement="Automatic", band_material="Leather", case_size="40.5mm", water_resistance="30m"),
        ],
    },
    "Handbags": {
        "base_price": 180,
        "items": [
            product("Coach Tabby Shoulder Bag 26", "like_new", brand="Coach", material="Pebbled Leather", color="Chalk", style="Shoulder Bag", size="Medium"),
            product("Kate Spade Knott Satchel", "good", brand="Kate Spade", material="Leather", color="Warm Beige", style="Satchel", size="Medium"),
            product("Michael Kors Manhattan", "good", brand="Michael Kors", material="Saffiano Leather", color="Black", style="Tote", size="Large"),
            product("Telfar Shopping Bag", "like_new", brand="Telfar", material="Vegan Leather", color="Tan", style="Shopping Bag", size="Medium"),
            product("Longchamp Le Pliage Original", "good", brand="Longchamp", material="Recycled Canvas", color="Paper", style="Top Handle", size="Large"),
        ],
    },
    "Outerwear": {
        "base_price": 240,
        "items": [
            product("Patagonia Nano Puff Jacket", "good", brand="Patagonia", size="Men's M", color="Forge Grey", material="Recycled Polyester", style="Insulated"),
            product("Arc'teryx Beta LT Jacket", "like_new", brand="Arc'teryx", size="Men's L", color="Black Sapphire", material="GORE-TEX", style="Shell"),
            product("The North Face Nuptse 700", "good", brand="The North Face", size="Women's M", color="Gardenia White", material="Nylon", style="Puffer"),
            product("Barbour Beaufort Wax Jacket", "good", brand="Barbour", size="40", color="Olive", material="Waxed Cotton", style="Field"),
            product("Canada Goose Wyndham Parka", "fair", brand="Canada Goose", size="Men's M", color="Navy", material="Arctic Tech", style="Parka"),
        ],
    },
    "Trading Cards": {
        "base_price": 210,
        "items": [
            product("Charizard ex PSA 10", "like_new", brand="Pokemon", franchise="Pokemon", year="2023", condition_grade="PSA 10", set_name="Scarlet & Violet 151"),
            product("LeBron James Prizm Silver PSA 9", "good", brand="Panini", franchise="NBA", year="2020", condition_grade="PSA 9", set_name="Prizm"),
            product("Blue-Eyes White Dragon BGS 8.5", "good", brand="Konami", franchise="Yu-Gi-Oh!", year="2002", condition_grade="BGS 8.5", set_name="Legend of Blue Eyes"),
            product("Shohei Ohtani Rookie Debut PSA 10", "like_new", brand="Topps", franchise="MLB", year="2018", condition_grade="PSA 10", set_name="Update Series"),
            product("Pikachu Van Gogh Promo CGC 9.5", "like_new", brand="Pokemon", franchise="Pokemon", year="2023", condition_grade="CGC 9.5", set_name="Promo"),
        ],
    },
    "Comic Books": {
        "base_price": 160,
        "items": [
            product("Amazing Spider-Man #300", "good", publisher="Marvel", franchise="Spider-Man", year="1988", condition_grade="CGC 8.5", issue_number="300"),
            product("Batman: The Killing Joke", "good", publisher="DC", franchise="Batman", year="1988", condition_grade="VF/NM", issue_number="1"),
            product("Saga #1", "like_new", publisher="Image", franchise="Saga", year="2012", condition_grade="CGC 9.6", issue_number="1"),
            product("Giant-Size X-Men #1", "fair", publisher="Marvel", franchise="X-Men", year="1975", condition_grade="CGC 4.5", issue_number="1"),
            product("Invincible #1", "good", publisher="Image", franchise="Invincible", year="2003", condition_grade="CGC 9.2", issue_number="1"),
        ],
    },
    "Action Figures": {
        "base_price": 140,
        "items": [
            product("Hot Toys Iron Man Mark 85", "like_new", brand="Hot Toys", franchise="Marvel", scale="1/6", material="ABS/PVC", boxed="Yes"),
            product("Hasbro Black Series Darth Vader", "good", brand="Hasbro", franchise="Star Wars", scale="6-inch", material="PVC", boxed="Yes"),
            product("S.H.Figuarts Goku Ultra Instinct", "like_new", brand="Bandai", franchise="Dragon Ball", scale="6-inch", material="PVC/ABS", boxed="Yes"),
            product("NECA TMNT Leonardo", "good", brand="NECA", franchise="Teenage Mutant Ninja Turtles", scale="7-inch", material="PVC", boxed="No"),
            product("McFarlane Batman Hush", "good", brand="McFarlane", franchise="DC", scale="7-inch", material="PVC", boxed="Yes"),
        ],
    },
    "Memorabilia": {
        "base_price": 260,
        "items": [
            product("Stephen Curry Signed Warriors Jersey", "good", franchise="NBA", year="2022", signed="Yes", material="Polyester", display_type="Framed"),
            product("New York Yankees Signed Baseball", "like_new", franchise="MLB", year="2021", signed="Yes", material="Leather", display_type="Display Case"),
            product("Manchester United Retro Match Poster", "good", franchise="Premier League", year="1999", signed="No", material="Paper", display_type="Poster Frame"),
            product("Taylor Swift Eras Tour VIP Poster", "like_new", franchise="Music", year="2023", signed="No", material="Cardstock", display_type="Portfolio Sleeve"),
            product("Marvel Studios Premiere Badge Set", "good", franchise="Marvel", year="2019", signed="No", material="Metal", display_type="Shadow Box"),
        ],
    },
    "Vinyl Records": {
        "base_price": 75,
        "items": [
            product("Taylor Swift 1989 (Taylor's Version) Blue Vinyl", "like_new", artist="Taylor Swift", genre="Pop", format="2xLP", pressing="Blue vinyl", condition_grade="NM"),
            product("Daft Punk Random Access Memories", "good", artist="Daft Punk", genre="Electronic", format="2xLP", pressing="Standard", condition_grade="VG+"),
            product("Fleetwood Mac Rumours", "good", artist="Fleetwood Mac", genre="Rock", format="LP", pressing="Reissue", condition_grade="VG+"),
            product("Miles Davis Kind of Blue", "like_new", artist="Miles Davis", genre="Jazz", format="LP", pressing="180g audiophile", condition_grade="NM"),
            product("Radiohead In Rainbows", "good", artist="Radiohead", genre="Alternative", format="LP", pressing="XL Recordings", condition_grade="VG+"),
        ],
    },
    "Board Games": {
        "base_price": 80,
        "items": [
            product("Wingspan", "good", brand="Stonemaier Games", player_count="1-5", play_time="70 min", genre="Engine building", edition="Standard"),
            product("Gloomhaven Jaws of the Lion", "good", brand="Cephalofair", player_count="1-4", play_time="120 min", genre="Dungeon crawler", edition="Retail"),
            product("Catan 25th Anniversary", "like_new", brand="Catan Studio", player_count="3-4", play_time="90 min", genre="Strategy", edition="Anniversary"),
            product("Brass Birmingham", "like_new", brand="Roxley", player_count="2-4", play_time="120 min", genre="Economic strategy", edition="Deluxe"),
            product("Dune Imperium Uprising", "like_new", brand="Dire Wolf", player_count="1-6", play_time="90 min", genre="Deck building", edition="First"),
        ],
    },
    "Box Sets": {
        "base_price": 95,
        "items": [
            product("The Lord of the Rings 4K Trilogy", "like_new", franchise="The Lord of the Rings", format="4K UHD", edition="Extended Edition", region="Region Free", condition_grade="NM"),
            product("The Sopranos Complete Series", "good", franchise="The Sopranos", format="Blu-ray", edition="Complete Series", region="Region A", condition_grade="VG+"),
            product("Wong Kar-wai World of Cinema", "like_new", franchise="Criterion Collection", format="Blu-ray", edition="Box Set", region="Region A", condition_grade="NM"),
            product("Harry Potter 8-Film Collection", "good", franchise="Harry Potter", format="4K UHD", edition="Steelbook", region="Region Free", condition_grade="VG+"),
            product("Studio Ghibli Collector's Edition", "good", franchise="Studio Ghibli", format="Blu-ray", edition="Collector's Box", region="Region A", condition_grade="VG"),
        ],
    },
    "Car Electronics": {
        "base_price": 180,
        "items": [
            product("Garmin Dash Cam Mini 2", "like_new", brand="Garmin", compatibility="Universal 12V", power="USB", connectivity="Bluetooth/Wi-Fi", condition_grade="NM"),
            product("Sony XAV-AX6000 Receiver", "good", brand="Sony", compatibility="Double DIN", power="4x55W", connectivity="Wireless CarPlay", condition_grade="VG+"),
            product("Pioneer DMH-WC5700NEX", "good", brand="Pioneer", compatibility="Modular dash install", power="4x50W", connectivity="Wireless CarPlay/Android Auto", condition_grade="VG"),
            product("Kenwood Excelon KDC-X705", "good", brand="Kenwood", compatibility="Single DIN", power="4x50W", connectivity="Bluetooth", condition_grade="VG+"),
            product("JBL BassPro Hub", "like_new", brand="JBL", compatibility="Spare tire well", power="200W RMS", connectivity="Wired", condition_grade="NM"),
        ],
    },
    "Detailing Tools": {
        "base_price": 110,
        "items": [
            product("Chemical Guys TORQX Polisher", "good", brand="Chemical Guys", type="Dual-action polisher", power="700W", material="Composite", condition_grade="VG+"),
            product("Ryobi 1800 PSI Pressure Washer", "good", brand="Ryobi", type="Pressure washer", power="13A", material="Plastic/Steel", condition_grade="VG"),
            product("Adams Foam Cannon Pro", "like_new", brand="Adam's Polishes", type="Foam cannon", power="Pressure driven", material="Brass", condition_grade="NM"),
            product("Griot's Garage 6-inch Orbital", "good", brand="Griot's Garage", type="Orbital polisher", power="850W", material="Composite", condition_grade="VG+"),
            product("IK Foam Pro 12", "like_new", brand="IK", type="Pump sprayer", power="Manual", material="HDPE", condition_grade="NM"),
        ],
    },
    "Garage Equipment": {
        "base_price": 190,
        "items": [
            product("Milwaukee M18 Inflator", "like_new", brand="Milwaukee", type="Inflator", capacity="150 PSI", material="Composite", condition_grade="NM"),
            product("DeWalt 20V Max Impact Wrench", "good", brand="DeWalt", type="Impact wrench", capacity="700 ft-lbs", material="Metal/Composite", condition_grade="VG+"),
            product("Husky 52-inch Tool Chest", "good", brand="Husky", type="Tool chest", capacity="18 drawers", material="Steel", condition_grade="VG"),
            product("RhinoRamps MAX", "good", brand="RhinoRamps", type="Vehicle ramps", capacity="16,000 lbs GVW", material="Resin", condition_grade="VG"),
            product("Craftsman LED Work Light", "like_new", brand="Craftsman", type="Work light", capacity="2000 lumens", material="Aluminum", condition_grade="NM"),
        ],
    },
    "Desks": {
        "base_price": 290,
        "items": [
            product("Fully Jarvis Bamboo Desk", "good", brand="Fully", width='60"', material="Bamboo", color="Natural", adjustable="Yes"),
            product("IKEA Bekant Corner Desk", "good", brand="IKEA", width='63"', material="Laminate", color="White", adjustable="No"),
            product("Herman Miller Nevi Sit-Stand", "like_new", brand="Herman Miller", width='58"', material="Laminate", color="Walnut", adjustable="Yes"),
            product("Vari Electric Standing Desk", "like_new", brand="Vari", width='60"', material="Reclaimed Wood Finish", color="Darkwood", adjustable="Yes"),
            product("Branch Standing Desk", "good", brand="Branch", width='58"', material="MDF", color="White Oak", adjustable="Yes"),
        ],
    },
    "Office Chairs": {
        "base_price": 340,
        "items": [
            product("Herman Miller Aeron Remastered", "good", brand="Herman Miller", material="Mesh", color="Graphite", adjustable="Yes", weight_capacity="300 lbs"),
            product("Steelcase Leap v2", "good", brand="Steelcase", material="Fabric", color="Blue Jay", adjustable="Yes", weight_capacity="400 lbs"),
            product("Branch Ergonomic Chair", "like_new", brand="Branch", material="Mesh", color="Sand", adjustable="Yes", weight_capacity="275 lbs"),
            product("Autonomous ErgoChair Pro", "good", brand="Autonomous", material="Mesh", color="Black", adjustable="Yes", weight_capacity="300 lbs"),
            product("Haworth Soji", "good", brand="Haworth", material="Fabric", color="Basalt", adjustable="Yes", weight_capacity="325 lbs"),
        ],
    },
    "Cameras": {
        "base_price": 920,
        "items": [
            product("Sony A7 IV Body", "like_new", brand="Sony", sensor="Full-frame", lens_mount="Sony E", resolution="33MP", condition_grade="NM"),
            product("Fujifilm X-T5 Silver", "good", brand="Fujifilm", sensor="APS-C", lens_mount="Fujifilm X", resolution="40MP", condition_grade="VG+"),
            product("Canon EOS R6 Mark II", "good", brand="Canon", sensor="Full-frame", lens_mount="Canon RF", resolution="24MP", condition_grade="VG"),
            product("Nikon Zf", "like_new", brand="Nikon", sensor="Full-frame", lens_mount="Nikon Z", resolution="24MP", condition_grade="NM"),
            product("DJI Osmo Pocket 3 Creator Combo", "like_new", brand="DJI", sensor="1-inch", lens_mount="Fixed", resolution="4K", condition_grade="NM"),
        ],
    },
}


def get_category_tree():
    return deepcopy(CATEGORY_TREE)


def iter_leaf_categories():
    for root_category in CATEGORY_TREE:
        for child in root_category["children"]:
            for leaf_category in child["leaves"]:
                yield {
                    "root": root_category["name"],
                    "branch": child["name"],
                    "name": leaf_category["name"],
                    "required_fields": list(leaf_category["required_fields"]),
                }


def collect_leaf_requirements():
    return {
        leaf_category["name"]: list(leaf_category["required_fields"])
        for leaf_category in iter_leaf_categories()
    }


def _bid_increment(base_price):
    if base_price < 100:
        return 5.0
    if base_price < 250:
        return 10.0
    if base_price < 700:
        return 15.0
    if base_price < 1400:
        return 25.0
    return 50.0


def _price_profile(base_price, item_index):
    starting_price = round(base_price * (0.82 + item_index * 0.05), 2)
    reserve_price = round(starting_price * 1.18, 2)
    return starting_price, reserve_price, _bid_increment(base_price)


def _build_description(item_name, attrs, condition):
    highlight_pairs = list(attrs.items())[:3]
    highlights = ", ".join(
        f"{key.replace('_', ' ')} {value}" for key, value in highlight_pairs
    )
    condition_text = condition.replace("_", " ")
    return (
        f"{item_name} in {condition_text} condition with {highlights}. "
        "Part of the expanded BuyMe marketplace catalog."
    )


def _build_bids(seller_username, starting_price, reserve_price, increment, spec_index, status):
    eligible_bidders = [
        username for username in SELLER_USERNAMES if username != seller_username
    ]
    bids = []

    if status == "closed":
        amounts = [
            round(starting_price + increment, 2),
            round(max(reserve_price, starting_price + increment * 2), 2),
            round(max(reserve_price + increment, starting_price + increment * 3), 2),
        ]
    else:
        bid_count = spec_index % 4
        amounts = []
        current_amount = starting_price
        for step in range(bid_count):
            next_amount = round(current_amount + increment * (1 + (step % 2)), 2)
            if next_amount >= reserve_price:
                next_amount = round(reserve_price - increment, 2)
            if next_amount <= current_amount:
                break
            amounts.append(next_amount)
            current_amount = next_amount

    for offset, amount in enumerate(amounts):
        bids.append(
            {
                "bidder": eligible_bidders[(spec_index + offset) % len(eligible_bidders)],
                "amount": amount,
            }
        )

    return bids


def _days_left_for_spec(status, spec_index):
    if status == "closed":
        return -((spec_index % 5) + 1)

    active_day_schedule = [3, 5, 7, 10, 14, 18, 21, 24, 28, 32, 36, 45]
    return active_day_schedule[spec_index % len(active_day_schedule)]


def _listing_name(item_name, root_category, variant_index):
    if variant_index == 0:
        return item_name
    return f"{item_name} (Alt Listing {variant_index + 1})"


def get_seed_auction_specs():
    auction_specs = []
    base_spec_index = 0
    for leaf_index, leaf_category in enumerate(iter_leaf_categories()):
        leaf_name = leaf_category["name"]
        leaf_inventory = LEAF_INVENTORY[leaf_name]
        base_price = leaf_inventory["base_price"]
        variant_count = ROOT_LISTING_MULTIPLIERS.get(leaf_category["root"], 1)

        for item_index, item in enumerate(leaf_inventory["items"]):
            for variant_index in range(variant_count):
                spec_index = base_spec_index if variant_index == 0 else len(auction_specs)
                pricing_index = item_index + variant_index
                starting_price, reserve_price, bid_increment = _price_profile(base_price, pricing_index)
                seller_username = SELLER_USERNAMES[
                    (base_spec_index + item_index + variant_index) % len(SELLER_USERNAMES)
                ]
                status = "closed" if spec_index % 7 == 0 else "active"
                days_left = _days_left_for_spec(status, spec_index)
                bids = _build_bids(
                    seller_username,
                    starting_price,
                    reserve_price,
                    bid_increment,
                    spec_index,
                    status,
                )
                current_price = bids[-1]["amount"] if bids else starting_price

                listing_name = _listing_name(item["name"], leaf_category["root"], variant_index)
                auction_specs.append(
                    {
                        "category": leaf_name,
                        "root_category": leaf_category["root"],
                        "branch_category": leaf_category["branch"],
                        "seller": seller_username,
                        "name": listing_name,
                        "description": _build_description(listing_name, item["attrs"], item["condition"]),
                        "condition": item["condition"],
                        "attrs": dict(item["attrs"]),
                        "starting_price": starting_price,
                        "reserve_price": reserve_price,
                        "bid_increment": bid_increment,
                        "status": status,
                        "days_left": days_left,
                        "bids": bids,
                    }
                )
            base_spec_index += 1

    return auction_specs


def get_seed_summary():
    leaf_count = sum(1 for _ in iter_leaf_categories())
    return {
        "top_level_category_count": len(CATEGORY_TREE),
        "leaf_category_count": leaf_count,
        "auction_count": len(get_seed_auction_specs()),
    }
