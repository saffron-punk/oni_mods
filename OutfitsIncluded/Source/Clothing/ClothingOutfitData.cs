using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using _SaffronUtils;
using Database;

namespace OutfitsIncluded.Clothing
{
	public class ClothingOutfitData : ClothingData
	{
		
		public ClothingOutfitUtility.OutfitType OutfitType { get; private set; }
		public string[] Items { get; private set; }

		private ClothingOutfitResource _resource;

		[JsonConstructor]
		public ClothingOutfitData(string id = "",
							string type = "",
							string[] items = null)
		{
			if (id.IsNullOrWhiteSpace())
			{
				RegisterError("No id provided.");
				return;
			}
			else
			{
				Id = id;
			}

			if (!Enum.TryParse<ClothingOutfitUtility.OutfitType>(type,
							out ClothingOutfitUtility.OutfitType outfitType))
			{
				RegisterError($"Unable to find OutfitType with name '{type}'");
				return;
			}
			else
			{
				OutfitType = outfitType;
			}

			if (items == null || items.Length == 0)
			{
				RegisterError("No items provided.");
				return;
			}
			Items = items;
		}

		public ClothingOutfitResource GetResource()
		{
			if (!IsValid()) { return null; }
			if (_resource == null)
			{
				_resource = new ClothingOutfitResource(
					Id,
					Items,
					Id, // TODO: name
					OutfitType);
			}
			return _resource;
		}
	}
}
