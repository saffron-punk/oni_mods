using HarmonyLib;
using OutfitsIncluded.Clothing;
using OutfitsIncluded.Core;
using SaffronLib;
using System.Collections.Generic;

namespace OutfitsIncluded.Patches
{
	public class InventoryOrganizationPatch
	{
		// Called via InventoryOrganization.Initialize()
		// from KleiInventoryScreen and OutfitDesignerScreen.
		[HarmonyPatch(typeof(InventoryOrganization), "GenerateSubcategories")]
		public static class InventoryOrganization_GenerateSubCategories_Patch
		{
			public static void Postfix()
			{
				Log.WriteMethodName();
				AddItemsToSupplyCloset();
			}
		}

		private static void AddItemsToSupplyCloset()
		{
			foreach (OutfitPacks.OutfitPack outfitPack in OIMod.OutfitPacks)
			{
				List<ClothingItemData> items = outfitPack.GetClothingItems();
				if (items == null) { continue; }
				foreach (ClothingItemData item in items)
				{
					HashSet<string> itemIdsSet = item.GetSupplyClosetItemIdsSet();
					if (itemIdsSet == null)
					{
						Log.WriteError($"Error adding {item} to supply closet. " +
							$"No item ids set found.");
						continue;
					}
					if (!itemIdsSet.Add(item.Id))
					{
						Log.WriteError($"Error adding {item} to supply closet. " +
							$"Duplicate item id: '{item.Id}'.");
						continue;
					}
					Log.WriteDebug($"{item.Id} added to supply closet. ");
				}
			}
		}
	}
}
