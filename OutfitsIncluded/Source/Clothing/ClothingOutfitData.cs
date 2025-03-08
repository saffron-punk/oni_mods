using Database;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;

namespace OutfitsIncluded.Clothing
{
	public class ClothingOutfitData : ClothingData
	{


		public ClothingOutfitUtility.OutfitType OutfitType { get; private set; }
		public List<string> ItemIds { get; set; }

		private ClothingOutfitResource _resource;

		[JsonConstructor]
		public ClothingOutfitData(string id = "",
							string type = "",
							string[] items = null,
							string name = "")
		{
			if (id.IsNullOrWhiteSpace())
			{
				MakeInvalid("No id provided.");
				return;
			}
			else
			{
				Id = id;
			}

			if (!Enum.TryParse<ClothingOutfitUtility.OutfitType>(type,
							out ClothingOutfitUtility.OutfitType outfitType))
			{
				MakeInvalid($"Unable to find OutfitType='{type}'");
				return;
			}
			else
			{
				OutfitType = outfitType;
			}

			if (items == null || items.Length == 0)
			{
				MakeInvalid("No items provided.");
				return;
			}
			ItemIds = new List<string>(items);

			Name = name ?? Id;
		}

		public ClothingOutfitResource GetResource()
		{
			if (!IsValid()) { return null; }
			if (_resource == null)
			{
				_resource = new ClothingOutfitResource(
					Id,
					ItemIds.ToArray(),
					GetLocalizedName(),
					OutfitType);
			}
			return _resource;
		}

		public void AddItemId(string itemId)
		{
			ItemIds.Add(itemId);
		}
	}
}
