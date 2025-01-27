using Database;
using HarmonyLib;
using System;
using System.Collections.Generic;
using OutfitsIncluded.Core;
using OutfitsIncluded.Clothing;
using _SaffronUtils;

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
				Log.Info("InventoryOrganization_GenerateSubCategories_Patch.Postfix()");
				AddItemsToSupplyCloset();
			}
		}

		private static void AddItemsToSupplyCloset()
		{
			List<ClothingItemData> items = Core.OutfitsIncluded.GetClothingItemsList();
			if (items == null) { return; }

			foreach (ClothingItemData item in items)
			{
				string subcategory = item.Subcategory;
				if (subcategory.IsNullOrWhiteSpace()) { continue; }
				
				if (!InventoryOrganization.subcategoryIdToPermitIdsMap.TryGetValue(
					subcategory, out HashSet<string> blueprintIds))
				{
					Log.Error($"Blueprint Ids set for subcategory '{subcategory}' not found.");
					continue;
				}
				if (!blueprintIds.Add(item.Id))
				{
					Log.Error($"Duplicate blueprint id: '{item.Id}'.");
					continue;
				}
				Log.Info($"{item.Id} added to supply closet. Subcategory={subcategory}.");
			}
		}
	}
}
