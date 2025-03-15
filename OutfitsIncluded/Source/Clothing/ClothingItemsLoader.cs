using Newtonsoft.Json;
using SaffronLib;
using System.Collections.Generic;
using System.IO;

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
				Log.WriteDebug($"No file found at path: {filePath}");
				return null;
			}
			Log.WriteDebug($"Loading clothing items from {filePath}");
			string json = FileUtils.LoadAsString(filePath);
			var data = JsonConvert.DeserializeObject<ClothingItemDataList>(json);

			if (data == null || data.items == null)
			{
				Log.WriteWarning($"No clothing items found in {filePath}.");
				return null;
			}

			List<ClothingItemData> validItems = data.items.FindAll(x => x.IsValid());
			Log.WriteDebug($"Clothing items loaded (valid/total): {validItems.Count}/{data.items.Count}");

			return validItems;
		}
	}
}
