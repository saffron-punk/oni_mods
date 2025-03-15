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
			if (!CategoryMaps.OutfitItemCategories.TryGetValue(
				outfit.OutfitType, out List<PermitCategory> expectedItemCategories))
			{
				Log.WriteWarning($"No expected categories found for outfit type={outfit.OutfitType}");
			}

			var missingCategories = new List<PermitCategory>(expectedItemCategories);

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
				else
				{
					missingCategories.Remove(itemResource.Category);
				}
			}

			if (!isValid)
			{
				return false;
			}

			// We will add empty placeholder items to outfits that are missing items in a category.
			// Without doing this, outfits will behave correctly when applied to dupes,
			// but, when edited, ONI will add the default items in place of missing items.
			// (For now, we will stick to the atmo belt. Plan to add others if needed in the future.)
			Log.WriteTrace($"Outfit {outfit.Id} is missing {missingCategories.Count} categories");
			foreach (PermitCategory category in missingCategories)
			{
				if (!OIConstants.EMPTY_CLOTHING_ITEM_IDS.TryGetValue(category, out string emptyItemId))
				{
					Log.WriteTrace($"Unable to find empty item for missing category {category}.");
					continue;
				}

				// Make sure the empty item Id exists.
				ClothingItemResource emptyItemResource = allClothingItems.resources.Find(x => x.Id == emptyItemId);
				if (emptyItemResource == null)
				{
					Log.WriteWarning($"No resource found for empty clothing item {emptyItemId}");
					continue;
				}

				Log.WriteDebug($"\tAdding {emptyItemId} for {category}");
				outfit.AddItemId(emptyItemId);
			}
			return true;
		}
	}
}
