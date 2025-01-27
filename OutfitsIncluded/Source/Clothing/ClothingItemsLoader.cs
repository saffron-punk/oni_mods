using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using _SaffronUtils;
using Database;
using static STRINGS.UI.CODEX;

namespace OutfitsIncluded.Clothing
{

	public static class ClothingItemsLoader
	{
		public class ClothingItemDataList
		{
			public List<ClothingItemData> items;
		}

		public static List<ClothingItemData> LoadFromJSONFile(string filePath)
		{
			if (!File.Exists(filePath))
			{
				Log.Error($"File not found at path: {filePath}");
				return null;
			}
			Log.Info($"Loading clothing items from {filePath}");
			string json = FileUtils.LoadAsString(filePath);
			var data = JsonConvert.DeserializeObject<ClothingItemDataList>(json);

			if (data == null || data.items == null)
			{
				Log.Error($"No items found in {filePath}.");
				return null;
			}

#if DEBUG
			foreach (var item in data.items)
			{
				Log.ObjectData(item);
			}
#endif

			Log.Info($"All clothing items: {data.items.Count}");
			List<ClothingItemData> validClothingItems = data.items.FindAll(x => x.IsValid());
			Log.Info($"Valid clothing items: {validClothingItems.Count}");

			return validClothingItems;
		}


	}
}
