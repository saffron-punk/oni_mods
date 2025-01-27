using HarmonyLib;
using KMod;
using System;
using System.Collections.Generic;
using System.IO;
using _SaffronUtils;
using OutfitsIncluded.Clothing;

// Code for adding custom blueprints is based on Decor Pack A by Aki:
// https://github.com/aki-art/ONI-Mods/blob/master/DecorPackA/

namespace OutfitsIncluded.Core
{
	public class OutfitsIncluded : UserMod2
	{
		public static Harmony HarmonyInstance;
		public static string ModPath;

		private static List<ClothingItemData> clothingItemsList;
		public static List<ClothingItemData> GetClothingItemsList()
		{
			if (clothingItemsList == null)
			{
				clothingItemsList = ClothingItemsLoader.LoadFromJSONFile(Path.Combine(ModPath, Paths.FacadesJSON));
			}
			return clothingItemsList;
		}

		private static List<ClothingOutfitData> clothingOutfitsList;
		public static List<ClothingOutfitData> GetClothingOutfitsList()
		{
			if (clothingOutfitsList == null)
			{
				clothingOutfitsList = ClothingOutfitsLoader.LoadFromJSONFile(Path.Combine(ModPath, Paths.OutfitsFileName));
			}
			return clothingOutfitsList;
		}

		public override void OnLoad(Harmony harmony)
		{
			HarmonyInstance = harmony;
			ModPath = path;

			Log.SetModName(mod.staticID);

			base.OnLoad(harmony); // PatchAll()
		}
	}
}
