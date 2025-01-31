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

				ClothingOutfits clothingOutfitsDb = __instance;
				if (clothingOutfitsDb == null)
				{
					Log.Error("ClothingOutfits_Constructor_Patch: clothingOutfitsDb is null.");
					return;
				}

				ClothingItems allClothingItems = items_resource;
				if (allClothingItems == null)
				{
					Log.Error("ClothingOutfits_Constructor_Patch: allClothingItems is null.");
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
					if (!AreOutfitItemsValid(outfit, allClothingItems)) { continue; }

					ClothingOutfitResource resource = outfit.GetResource();
					if (resource == null) { continue; }
					clothingOutfitsDb.resources.Add(resource);
				}
			}
		}

		private static bool AreOutfitItemsValid(
			ClothingOutfitData outfit,
			ClothingItems allClothingItems)
		{
			bool isValid = true;
			foreach (string itemId in outfit.Items)
			{
				// We won't break on failure, so we can report all errors.
				ClothingItemResource itemResource = allClothingItems.resources.Find(x => x.Id == itemId);
				if (itemResource == null)
				{
					Log.Error($"Item '{itemId}' not found for '{outfit}'");
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
