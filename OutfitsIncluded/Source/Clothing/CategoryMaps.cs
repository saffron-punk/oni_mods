using Database;
using System.Collections.Generic;

namespace OutfitsIncluded.Clothing
{
	public class CategoryMaps
	{
		public static readonly Dictionary<PermitCategory, string> DefaultSubcategories = new Dictionary<PermitCategory, string>()
		{
            //{ PermitCategory.Equipment, InventoryOrganization.PermitSubcategories.PRIMO_GARB },
            { PermitCategory.DupeTops, InventoryOrganization.PermitSubcategories.CLOTHING_TOPS_BASIC },
			{ PermitCategory.DupeBottoms, InventoryOrganization.PermitSubcategories.CLOTHING_BOTTOMS_BASIC },
			{ PermitCategory.DupeGloves, InventoryOrganization.PermitSubcategories.CLOTHING_GLOVES_BASIC },
			{ PermitCategory.DupeShoes, InventoryOrganization.PermitSubcategories.CLOTHING_SHOES_BASIC },
            //{ PermitCategory.DupeHats, InventoryOrganization.PermitSubcategories.UNCATEGORIZED },
            //{ PermitCategory.DupeAccessories, InventoryOrganization.PermitSubcategories.UNCATEGORIZED },
            { PermitCategory.AtmoSuitHelmet, InventoryOrganization.PermitSubcategories.ATMOSUIT_HELMETS_BASIC },
			{ PermitCategory.AtmoSuitBody, InventoryOrganization.PermitSubcategories.ATMOSUIT_BODIES_BASIC },
			{ PermitCategory.AtmoSuitGloves, InventoryOrganization.PermitSubcategories.ATMOSUIT_GLOVES_BASIC },
			{ PermitCategory.AtmoSuitBelt, InventoryOrganization.PermitSubcategories.ATMOSUIT_BELTS_BASIC },
			{ PermitCategory.AtmoSuitShoes, InventoryOrganization.PermitSubcategories.ATMOSUIT_SHOES_BASIC },
		};

		public static readonly Dictionary<PermitCategory, ClothingOutfitUtility.OutfitType> DefaultOutfitTypes = new Dictionary<PermitCategory, ClothingOutfitUtility.OutfitType>()
		{
            //{ PermitCategory.Equipment, ClothingOutfitUtility.OutfitType.Clothing },
            { PermitCategory.DupeTops, ClothingOutfitUtility.OutfitType.Clothing },
			{ PermitCategory.DupeBottoms, ClothingOutfitUtility.OutfitType.Clothing },
			{ PermitCategory.DupeGloves, ClothingOutfitUtility.OutfitType.Clothing },
			{ PermitCategory.DupeShoes, ClothingOutfitUtility.OutfitType.Clothing },
            //{ PermitCategory.DupeHats, ClothingOutfitUtility.OutfitType.Clothing },
            //{ PermitCategory.DupeAccessories, ClothingOutfitUtility.OutfitType.Clothing },
            { PermitCategory.AtmoSuitHelmet, ClothingOutfitUtility.OutfitType.AtmoSuit },
			{ PermitCategory.AtmoSuitBody, ClothingOutfitUtility.OutfitType.AtmoSuit },
			{ PermitCategory.AtmoSuitGloves, ClothingOutfitUtility.OutfitType.AtmoSuit },
			{ PermitCategory.AtmoSuitBelt, ClothingOutfitUtility.OutfitType.AtmoSuit },
			{ PermitCategory.AtmoSuitShoes, ClothingOutfitUtility.OutfitType.AtmoSuit },
		};

		public static readonly Dictionary<ClothingOutfitUtility.OutfitType, List<PermitCategory>> OutfitItemCategories = new Dictionary<ClothingOutfitUtility.OutfitType, List<PermitCategory>>()
		{
			{ ClothingOutfitUtility.OutfitType.Clothing, new List<PermitCategory>()
				{
					PermitCategory.DupeTops,
					PermitCategory.DupeBottoms,
					PermitCategory.DupeGloves,
					PermitCategory.DupeShoes,
				}
			},
			{ ClothingOutfitUtility.OutfitType.AtmoSuit, new List<PermitCategory>()
				{
					PermitCategory.AtmoSuitHelmet,
					PermitCategory.AtmoSuitBody,
					PermitCategory.AtmoSuitGloves,
					PermitCategory.AtmoSuitBelt,
					PermitCategory.AtmoSuitShoes,
				}
			}
		};
	}
}

