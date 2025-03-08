using Database;
using System.Collections.Generic;

namespace OutfitsIncluded.Core
{
	public static class OIConstants
	{
		public const string OUTFIT_PACK_NAME_TAG = "[OUTFIT_PACK]";
		public const string OUTFIT_PACK_COLOR_TAG = "[OUTFIT_PACK_COLOR]";

		public const string OI_STRING_CLASS = "STRINGS.OUTFITS_INCLUDED";
		public const string CLOTHING_ITEMS_STRING_CLASS = "CLOTHING_ITEMS";
		public const string CLOTHING_OUTFITS_STRING_CLASS = "CLOTHING_OUTFITS";
		public const string NAME_STRING = "NAME";
		public const string DESC_STRING = "DESC";

		// Items other than belts (tested with atmo suit gloves and atmo suit shoes)
		// seem to cause problems with supply closet display.
		public static Dictionary<PermitCategory, string> EMPTY_CLOTHING_ITEM_IDS = new Dictionary<PermitCategory, string>()
		{
			//{ PermitCategory.DupeTops, "oi_empty_top" },
			//{ PermitCategory.DupeBottoms, "oi_empty_bottom" },
			//{ PermitCategory.DupeGloves, "oi_empty_gloves" },
			//{ PermitCategory.DupeShoes, "oi_empty_shoes" },
			//{ PermitCategory.AtmoSuitHelmet, "oi_empty_atmo_helmet" },
			//{ PermitCategory.AtmoSuitBody, "oi_empty_atmo_body" },
			//{ PermitCategory.AtmoSuitGloves, "oi_empty_atmo_gloves" },
			{ PermitCategory.AtmoSuitBelt, "oi_empty_atmo_belt" },
			//{ PermitCategory.AtmoSuitShoes, "oi_empty_atmo_shoes" },
		};

		public static string DefaultOutfitPackColor = "#" + UnityEngine.Color.green.ToHexString();
	}
}
