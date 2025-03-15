using Database;
using HarmonyLib;
using OutfitsIncluded.Clothing;
using OutfitsIncluded.Core;
using SaffronLib;
using System.Collections.Generic;
using System.Reflection;

namespace OutfitsIncluded.Patches
{
	public class ClothingItemsPatch
	{
		// Called by Db_Initialize_Patch.Prefix()
		public static void Patch(Harmony harmony)
		{
			ConstructorInfo target = AccessTools.Constructor(
				typeof(ClothingItems),
				new[] { typeof(ResourceSet) });

			MethodInfo postfix = AccessTools.Method(
				typeof(ClothingItems_Constructor_Patch),
				nameof(ClothingItems_Constructor_Patch.Postfix));

			harmony.Patch(target, postfix: new HarmonyMethod(postfix));
		}

		public class ClothingItems_Constructor_Patch
		{
			public static void Postfix(ClothingItems __instance)
			{
				Log.WriteMethodName();

				ClothingItems clothingItemsDb = __instance;
				if (clothingItemsDb == null)
				{
					Log.WriteError("ClothingItems_Constructor_Patch: ClothingItems is null.");
					return;
				}

				AddItemsToDatabase(clothingItemsDb);
			}
		}

		private static void AddItemsToDatabase(ClothingItems clothingItemsDb)
		{
			foreach (OutfitPacks.OutfitPack outfitPack in OIMod.OutfitPacks)
			{
				List<ClothingItemData> items = outfitPack.GetClothingItems();
				if (items == null) { continue; }

				foreach (ClothingItemData item in items)
				{
					ClothingItemResource resource = item.GetResource();
					if (resource == null) { continue; }
					clothingItemsDb.resources.Add(resource);
				}
			}
		}
	}
}
