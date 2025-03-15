using Database;
using Newtonsoft.Json;
using SaffronLib;
using System;
using System.Collections.Generic;
using static OutfitsIncluded.Clothing.CategoryMaps;

namespace OutfitsIncluded.Clothing
{
	public class ClothingItemData : ClothingData
	{
		public PermitCategory Category { get; private set; }
		public ClothingOutfitUtility.OutfitType OutfitType { get; private set; }
		public string Kanim { get; private set; }

		private string _subcategory { get; set; }
		private ClothingItemResource _resource;

		[JsonConstructor]
		public ClothingItemData(string id = "",
					   string category = "",
					   string subcategory = "",
					   string kanim = "",
					   string name = "",
					   string description = "")
		{
			if (id.IsNullOrWhiteSpace())
			{
				MakeInvalid("No id provided for clothing item.");
				return;
			}
			else
			{
				Id = id;
			}

			if (!Enum.TryParse<PermitCategory>(category, out PermitCategory permitCategory))
			{
				MakeInvalid($"Unable to find PermitCategory with name '{category}'");
				return;
			}
			else
			{
				Category = permitCategory;
			}

			// If blank or invalid, will change to default subcategory later.
			_subcategory = subcategory;

			if (kanim.IsNullOrWhiteSpace())
			{
				Kanim = id + "_kanim";
			}
			else
			{
				Kanim = kanim;
			}

			// TODO: Put in try/catch block
			if (Assets.GetAnim(Kanim) == null)
			{
				MakeInvalid($"No kanim found with name '{Kanim}'");
				return;
			}

			if (!DefaultOutfitTypes.TryGetValue(Category, out ClothingOutfitUtility.OutfitType outfitType))
			{
				MakeInvalid($"No OutfitType found for category {Category}");
				return;
			}
			OutfitType = outfitType;

			if (name.IsNullOrWhiteSpace())
			{
				Name = id;
			}
			else
			{
				Name = name;
			}

			if (description.IsNullOrWhiteSpace())
			{
				Description = "";
			}
			else
			{
				Description = description;
			}
		}

		public ClothingItemResource GetResource()
		{
			if (!IsValid()) return null;
			if (_resource == null)
			{
				_resource = new ClothingItemResource(
					Id,
					GetLocalizedName(),
					GetLocalizedDescription(),
					OutfitType,
					Category,
					PermitRarity.Universal,
					Kanim,
					requiredDlcIds: null,
					forbiddenDlcIds: null);
			}
			return _resource;
		}

		public HashSet<string> GetSupplyClosetItemIdsSet()
		{
			if (_subcategory.IsNullOrWhiteSpace() ||
				!InventoryOrganization.subcategoryIdToPermitIdsMap.TryGetValue(
						_subcategory, out HashSet<string> itemIdsSet))
			{
				if (!DefaultSubcategories.TryGetValue(
					Category, out string defaultSubcategory))
				{
					Log.WriteError($"Provided subcategory ({_subcategory}) is null or invalid, " +
						$"and no default subcategory found for category {Category}.");
					return null;
				}
				Log.WriteDebug($"Using default subcategory for {Id}.");
				if (!InventoryOrganization.subcategoryIdToPermitIdsMap.TryGetValue(
					defaultSubcategory, out itemIdsSet))
				{
					Log.WriteError($"Item ids set for subcategory '{defaultSubcategory}' not found.");
					return null;
				}
			}
			return itemIdsSet;
		}
	}
}
