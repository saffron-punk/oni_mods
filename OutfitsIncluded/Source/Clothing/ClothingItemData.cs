using Database;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using static OutfitsIncluded.Clothing.CategoryMaps;
using _SaffronUtils;
using KMod;
using OutfitsIncluded.Core;

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

			if (name.IsNullOrWhiteSpace())
			{
				Name = id;
			} else
			{
				Name = name;
			}

			if (description.IsNullOrWhiteSpace())
			{
				Description = "";
			} else
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
					DlcManager.AVAILABLE_ALL_VERSIONS);
			}
			return _resource;
		}

	}
}
