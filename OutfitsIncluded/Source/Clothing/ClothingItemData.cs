using Database;
using Newtonsoft.Json;
using System;
using static OutfitsIncluded.Clothing.CategoryMaps;

namespace OutfitsIncluded.Clothing
{
	public class ClothingItemData : ClothingData
	{
		public PermitCategory Category { get; private set; }
		public string Subcategory { get; private set; }
		public ClothingOutfitUtility.OutfitType OutfitType { get; private set; }
		public string Kanim { get; private set; }

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
			Subcategory = subcategory;

			if (kanim.IsNullOrWhiteSpace())
			{
				Kanim = id + "_kanim";
			}
			else
			{
				Kanim = kanim;
			}

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
	}
}
