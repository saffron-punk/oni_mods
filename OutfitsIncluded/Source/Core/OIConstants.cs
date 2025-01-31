using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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
		
		public static string DefaultOutfitPackColor = "#" + UnityEngine.Color.green.ToHexString();
	}
}
