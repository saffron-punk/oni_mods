using Database;
using HarmonyLib;
using OutfitsIncluded.Clothing;
using OutfitsIncluded.Core;
using SaffronLib;
using System.Collections.Generic;
using System.Reflection;

namespace OutfitsIncluded.Patches
{
	public class ClothingOutfitsPatch
	{
		// Called by Db_Initialize_Patch.Prefix()
		public static void Patch(Harmony harmony)
		{
			ConstructorInfo target = AccessTools.Constructor(
				typeof(ClothingOutfits),
				new[] { typeof(ResourceSet), typeof(ClothingItems) });

			MethodInfo postfix = AccessTools.Method(
				typeof(ClothingOutfits_Constructor_Patch),
				nameof(ClothingOutfits_Constructor_Patch.Postfix));

			harmony.Patch(target, postfix: new HarmonyMethod(postfix));
		}

		public class ClothingOutfits_Constructor_Patch
		{
			public static void Postfix(ClothingOutfits __instance,
									   ClothingItems items_resource)
			{
				Log.WriteMethodName();

				ClothingOutfits clothingOutfitsDb = __instance;
				if (clothingOutfitsDb == null)
				{
					Log.WriteError("ClothingOutfits_Constructor_Patch: clothingOutfitsDb is null.");
					return;
				}

				ClothingItems allClothingItems = items_resource;
				if (allClothingItems == null)
				{
					Log.WriteError("ClothingOutfits_Constructor_Patch: allClothingItems is null.");
					return;
				}

				AddOutfitsToDatabase(clothingOutfitsDb, allClothingItems);
			}
		}

		private static void AddOutfitsToDatabase(
			ClothingOutfits clothingOutfitsDb,
			ClothingItems allClothingItems)
		{
			foreach (OutfitPacks.OutfitPack outfitPack in OIMod.OutfitPacks)
			{
				List<ClothingOutfitData> outfits = outfitPack.GetClothingOutfits();
				if (outfits == null) { continue; }

				foreach (ClothingOutfitData outfit in outfits)
				{
					if (!ValidateOutfitItems(outfit, allClothingItems)) { continue; }

					ClothingOutfitResource resource = outfit.GetResource();
					if (resource == null) { continue; }
					clothingOutfitsDb.resources.Add(resource);
				}
			}
		}

		private static bool ValidateOutfitItems(
			ClothingOutfitData outfit,
			ClothingItems allClothingItems)
		{
			bool isValid = true;
			foreach (string itemId in outfit.ItemIds)
			{
				// We won't break on failure, so we can report all errors.
				ClothingItemResource itemResource = allClothingItems.resources.Find(x => x.Id == itemId);
				if (itemResource == null)
				{
					Log.WriteError($"Item '{itemId}' not found for '{outfit}'");
					isValid = false;
				}
				else if (itemResource.outfitType != outfit.OutfitType)
				{
					Log.WriteError($"Mismatched outfit and item types: '{outfit.Id}'={outfit.OutfitType} and item '{itemId}'={itemResource.outfitType}.");
					isValid = false;
				}
			}

			if (!isValid)
			{
				return false;
			}
			return true;
		}
	}
}
