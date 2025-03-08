WIP

## Description
Outfits Included is a mod loader for Outfit Pack mods, which add Supply Closet clothing and atmo suits to Oxygen Not Included. It allows modders to add new dupe clothing to the game without programming or compiling DLLs.

#### Features
- Adding clothing and atmo suit items and outfits to the Supply Closet.
- Safe save functions. (Uninstalling Outfits Included or any Outfit Pack mods will not prevent loading the save file.)
- Translations support.

#### Attributions
- Blueprint loading and safe save functions are based off of [Aki's mods](https://github.com/aki-art/ONI-Mods) (including Decor Pack I and Spooky Pumpkin).


### How ONI clothing works
A dupe looks at 3 things in order when deciding what to wear:
- 1. Their default clothing - Every dupe is assigned default clothing along with their hair, skin color, and facial features. These come from the dupe's "personality".
- 2. Their Supply Closet clothing and atmo suits (aka Blueprints) - ONI includes some Supply Closet items for all players. Klei adds additional items in DLC's and their incentives system.
- 3. Their equippable clothing - Players assign these to dupes during gameplay. They include hats, Snazzy Suits and Primo Garb.

Mods like Dupery (fixed) and Duplicant Stat Selector can edit a dupe's default clothing (#1).

Outfits Included adds Supply Closet clothing and atmo suits (#2).

Some special mods (see Aki's collection) add equippable clothing (#3).



## Outfit Pack mods

To make a mod an "outfit pack", your mod folder needs to contain a folder called `outfits_included`. Inside that folder, you should have `clothing_items.json` and/or `clothing_outfits.json`. Both files are optional, but without at least one of them, nothing will happen.

     OutfitPackExampleMod/
        mod.yaml
        mod_info.yaml
        anim/assets/
        outfits_included/
            clothing_items.json
            clothing_outfits.json
            translations/ - if it doesn't already exist, this folder will be created when you launch ONI with the mod enabled
                translation_template.pot - this template will be automatically created from the names and descriptions in the json files
                es.po - a Spanish translation
                fr.po - a French translation


### JSON files

#### clothing_items.json

    {
        "items": [
            {
                "id": "prefix_example_atmo_helmet" // required, must be unique among other clothing items loaded by the base game and mods
                "kanim": "prefix_example_atmo_helmet_kanim" // optional, defaults to the id + "_kanim"
                "category": "AtmoSuitHelmet" // required
                "subcategory": "ATMOSUIT_HELMETS_BASIC" // optional, defaults to 'basic' subcategory
                "name": "Example Atmo Helmet" // optional, defaults to the id
                "description": "An example of an atmo helmet." // optional, defaults to an empty string
            }
        ]
    }


#### Categories
The value should match a key from ONI's Database.PermitCategory enum (case-sensitive).

See also: CategoryMaps.cs

- DupeTops
- DupeBottoms
- DupeGloves
- DupeShoes
- AtmoSuitHelmet
- AtmoSuitBody
- AtmoSuitGloves
- AtmoSuitBelt
- AtmoSuitShoes

#### Subcategories (optional)
The value should match a constant from ONI's InventoryOrganization.PermitSubcategories class (case-sensitive). If the value is not given or is not found, OI will assign the relevant "basic" subcategory.

Note: ONI defines certain subcategories source code but doesn't use them (yet). These include the fancy atmosuit categories. If a clothing item's "subcategory" value references an existing subcategory that ONI hasn't set up, it will revert to the default subcategory and print a warning in player.log.

See also: CategoryMaps.cs

- CLOTHING_TOPS_BASIC
- CLOTHING_TOPS_TSHIRT
- CLOTHING_TOPS_FANCY
- CLOTHING_TOPS_JACKET
- CLOTHING_TOPS_UNDERSHIRT
- CLOTHING_TOPS_DRESS
- CLOTHING_BOTTOMS_BASIC
- CLOTHING_BOTTOMS_FANCY
- CLOTHING_BOTTOMS_SHORTS
- CLOTHING_BOTTOMS_SKIRTS
- CLOTHING_BOTTOMS_UNDERWEAR
- CLOTHING_GLOVES_BASIC
- CLOTHING_GLOVES_PRINTS
- CLOTHING_GLOVES_SHORT
- CLOTHING_GLOVES_FORMAL
- CLOTHING_SHOES_BASIC
- CLOTHING_SHOES_FANCY
- CLOTHING_SHOE_SOCKS
- ATMOSUIT_HELMETS_BASIC
- ATMOSUIT_HELMETS_FANCY
- ATMOSUIT_BODIES_BASIC
- ATMOSUIT_BODIES_FANCY
- ATMOSUIT_GLOVES_BASIC
- ATMOSUIT_GLOVES_FANCY
- ATMOSUIT_BELTS_BASIC
- ATMOSUIT_BELTS_FANCY
- ATMOSUIT_SHOES_BASIC
- ATMOSUIT_SHOES_FANCY


#### clothing_outfits.json

    {
        "outfits": [
            {
                "id": "asp_adventurer_atmosuit", // required, must be unique among other outfits in the game
                "items": [
                    "prefix_example_atmo_helmet", // list of clothing item IDs
                    "prefix_example_atmo_body",
                    "prefix_example_atmo_belt",
                    "prefix_example_atmo_gloves",
                    "prefix_example_atmo_shoes",
                ],
                "name": "asp_adventurer_atmosuit",
                "type": "AtmoSuit"
            }
        ]
    }

#### Items
These will usually contain items from this mod. But it can also contain item IDs from the base game, or from other mods. Outfits are loaded after all clothing items are loaded, so mod load order does not matter.

If you use ONI clothing items that are in a DLC that the user does not own or are an incentive blueprint the user doesn't have, the outfit won't show up in the duplicant clothing tab. It will still show up in the supply closet outfits panel with a locked icon.


#### Type
Should match keys in the ClothingOutfitUtility.OutfitType enum (case-sensitive).

- Clothing
- AtmoSuit




### Translations
Because OI loads outfit packs at runtime, it also needs to generate translations at runtime. This means it bypasses the normal ONI translation functions. This change is mostly behind the scenes, and effort was made to stick with the conventions used in other ONI mods.

The main difference is the location of the files: in the `outfits_included/translations` subfolder.

Like other mods, OI generates a `.pot` translation template automatically every time it runs. Language-specific translation files should also follow the naming convention of language code + `.po`.



