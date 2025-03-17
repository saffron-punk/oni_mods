using HarmonyLib;
using OutfitsIncluded.Clothing;
using OutfitsIncluded.Core;
using OutfitsIncluded.OutfitPacks;
using SaffronLib;
using System;
using System.Collections.Generic;
using static OutfitsIncluded.Clothing.CategoryMaps;

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
					HashSet<string> itemIdsSet = GetItemIdsSetForClothingItem(item);
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

		private static HashSet<string> GetItemIdsSetForClothingItem(ClothingItemData item)
		{
			if (item == null) { return null; }

			// First try to get item ids for provided subcategory
			HashSet<string> itemIdsSet = GetSubcategoryItemIdsSet(item.Subcategory);
			if (itemIdsSet != null) { return itemIdsSet; }
			Log.WriteTrace($"No itemIdsSet found for subcategory: {item.Subcategory}");

			// Then try to get item ids for the Outfit Pack's subcategory
			string outfitPackSubcategory = GetOutfitPackSubcategoryId(item);
			itemIdsSet = GetSubcategoryItemIdsSet(outfitPackSubcategory);
			if (itemIdsSet != null) { return itemIdsSet; }

			// Create outfit pack subcategory if not found and try again.
			CreateNewOutfitPackSubcategory(item);
			itemIdsSet = GetSubcategoryItemIdsSet(outfitPackSubcategory);
			if (itemIdsSet != null) { return itemIdsSet; }
			Log.WriteTrace($"No itemIdsSet found for outfit pack: {outfitPackSubcategory}");

			// Then try default subcategory for category.
			if (!DefaultSubcategories.TryGetValue(
					item.Category, out string defaultSubcategory))
			{
				Log.WriteTrace($"No default subcategory found for category: {item.Category}");
				return null;
			}
			itemIdsSet = GetSubcategoryItemIdsSet(defaultSubcategory);
			if (itemIdsSet != null) { return itemIdsSet; }

			Log.WriteWarning($"Unable to find Supply Closet subcategory for clothing item: {item}");
			return null;
		}

		private static HashSet<string> GetSubcategoryItemIdsSet(string subcategory)
		{
			if (subcategory.IsNullOrWhiteSpace())
			{
				return null;
			}

			if (!InventoryOrganization.subcategoryIdToPermitIdsMap.TryGetValue(
						subcategory, out HashSet<string> itemIdsSet))
			{
				return null;
			}

			return itemIdsSet;
		}

		private static string GetOutfitPackSubcategoryId(ClothingItemData item)
		{
			if (item == null) { return null; }

			string outfitPackId = item.outfitPack?.Id;
			if (outfitPackId.IsNullOrWhiteSpace())
			{
				Log.WriteWarning($"No ID found for outfit pack {item.outfitPack}");
				return null;
			}

			string category = item.Category.ToString();
			string subcategory = $"{outfitPackId}_{category}";
			subcategory = subcategory.Replace(".", "_").ToUpperInvariant();
			return subcategory;
		}

		private static void CreateNewOutfitPackSubcategory(ClothingItemData item)
		{
			if (item == null || item.outfitPack == null) { return; }

			string subcategoryId = GetOutfitPackSubcategoryId(item);
			if (subcategoryId.IsNullOrWhiteSpace()) { return; }

			string subcategoryString = item.outfitPack.Name;
			if (subcategoryString.IsNullOrWhiteSpace())
			{
				Log.WriteWarning($"No outfit pack name found for {item.outfitPack}");
				subcategoryString = subcategoryId;
			}

			// TODO: get localized outfit pack name
			Strings.Add(
				"STRINGS.UI.KLEI_INVENTORY_SCREEN.SUBCATEGORIES." + subcategoryId,
				subcategoryString);

			UnityEngine.Sprite uiSprite = GetOutfitPackSprite(item.outfitPack);
			int priority = 9999;
			string[] emptyItemIds = new string[] { };

			_ = Traverse.Create(typeof(InventoryOrganization))
				.Method(
					"AddSubcategory",
					new Type[] { typeof(string), typeof(UnityEngine.Sprite), typeof(int), typeof(string[]) })
				.GetValue(subcategoryId, uiSprite, priority, emptyItemIds);

			Log.WriteDebug($"Created new outfit pack subcategory: {subcategoryId}");
		}

		private static UnityEngine.Sprite GetOutfitPackSprite(OutfitPack outfitPack)
		{
			string kanim = outfitPack.Id.Replace(".", "_").ToLowerInvariant() + "_icon_kanim";
			Log.WriteTrace($"{outfitPack}: kanim_name={kanim}");
			UnityEngine.Sprite uiSprite = GetSpriteFromKanim(kanim);
			if (uiSprite == null)
			{
				// If the outfit pack doesn't have a kanim icon, use OI's icon.
				uiSprite = GetSpriteFromKanim(Core.OIConstants.OI_ICON_KANIM);
			}

			if (uiSprite == null)
			{
				// If something went wrong with the kanim icons, use generic icon.
				uiSprite = Assets.GetSprite((HashedString)"status_item_event");
			}

			return uiSprite;
		}

		private static UnityEngine.Sprite GetSpriteFromKanim(string kanim)
		{
			KAnimFile kAnimFile = Assets.GetAnim(kanim);
			UnityEngine.Sprite sprite = null;
			if (kAnimFile != null)
			{
				sprite = Def.GetUISpriteFromMultiObjectAnim(kAnimFile);
			}
			return sprite;
		}
	}
}
