using Database;
using HarmonyLib;
using System;
using System.Reflection;
using System.Collections.Generic;
using OutfitsIncluded.Core;
using OutfitsIncluded.Clothing;
using _SaffronUtils;
using System.Runtime.CompilerServices;

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
				Log.Info("ClothingOutfits_Constructor_Patch.Postfix()");

				ClothingOutfits clothingOutfits = __instance;
				if (clothingOutfits == null)
				{
					Log.Error("ClothingOutfits_Constructor_Patch: ClothingOutfits is null.");
					return;
				}

				ClothingItems clothingItems = items_resource;
				if (clothingItems == null)
				{
					Log.Error("ClothingOutfits_Constructor_Patch: ClothingItems is null.");
					return;
				}

				AddOutfitsToDatabase(clothingOutfits, clothingItems);
			}
		}

		private static void AddOutfitsToDatabase(ClothingOutfits clothingOutfits,
										  ClothingItems clothingItems)
		{
			List<ClothingOutfitData> outfits = Core.OutfitsIncluded.GetClothingOutfitsList();
			if (outfits == null) { return; }

			foreach (ClothingOutfitData outfit in outfits)
			{
				if (!AreOutfitItemsValid(outfit, clothingItems)) { continue; }

				ClothingOutfitResource resource = outfit.GetResource();
				if (resource == null) { continue; }
				clothingOutfits.resources.Add(resource);
			}
		}

		private static bool AreOutfitItemsValid(ClothingOutfitData outfit, ClothingItems allClothingItems)
		{
			bool isValid = true;
			foreach (string itemId in outfit.Items)
			{
				// Don't break on failure. We want to report all errors.
				ClothingItemResource itemResource = allClothingItems.resources.Find(x => x.Id == itemId);
				if (itemResource == null)
				{
					Log.Error($"Item '{itemId}' not found for outfit '{outfit.Id}'");
					isValid = false;
				}
				else if (itemResource.outfitType != outfit.OutfitType)
				{
					Log.Error($"Mismatched outfit and item types: '{outfit.Id}'={outfit.OutfitType} and item '{itemId}'={itemResource.outfitType}.");
					isValid = false;
				}
			}
			return isValid;
		}
	}
}
