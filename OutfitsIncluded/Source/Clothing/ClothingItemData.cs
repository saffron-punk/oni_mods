using Database;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using static OutfitsIncluded.Clothing.CategoryMaps;
using _SaffronUtils;

namespace OutfitsIncluded.Clothing
{
	public class ClothingItemData : ClothingData
	{
		public PermitCategory Category { get; private set; }
		public string Subcategory { get; private set; }
		public ClothingOutfitUtility.OutfitType OutfitType { get; private set; }
		public string Kanim { get; private set; }

		private ClothingItemResource resource;

		[JsonConstructor]
		public ClothingItemData(string id = "",
					   string category = "",
					   string subcategory = "",
					   string kanim = "",
					   string stringId = "")
		{
			if (id.IsNullOrWhiteSpace())
			{
				RegisterError("No id provided for clothing item.");
				return;
			}
			else
			{
				Id = id;
			}

			if (!Enum.TryParse<PermitCategory>(category, out PermitCategory permitCategory))
			{
				RegisterError($"Unable to find PermitCategory with name '{category}'");
				return;
			}
			else
			{
				Category = permitCategory;
			}

			if (subcategory.IsNullOrWhiteSpace())
			{
				if (!DefaultSubcategories.TryGetValue(Category, out string defaultSubcategory))
				{
					RegisterError($"No default subcategory found for category {Category}");
					return;
				}
				else
				{
					Subcategory = defaultSubcategory;
				}
			}
			else
			{
				Subcategory = subcategory;
			}

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
				RegisterError($"No kanim found with name '{Kanim}'");
				return;
			}

			if (!DefaultOutfitTypes.TryGetValue(Category, out ClothingOutfitUtility.OutfitType outfitType))
			{
				RegisterError($"No OutfitType found for category {Category}");
				return;
			}
			OutfitType = outfitType;

			// TODO: get string ID & parse name/description
		}

		public ClothingItemResource GetResource()
		{
			if (!IsValid()) return null;
			if (resource == null)
			{
				resource = new ClothingItemResource(
					Id,
					Id, // TODO: name
					Id, // TODO: description
					OutfitType,
					Category,
					PermitRarity.Universal,
					Kanim,
					DlcManager.AVAILABLE_ALL_VERSIONS);
			}
			return resource;
		}

	}
}
