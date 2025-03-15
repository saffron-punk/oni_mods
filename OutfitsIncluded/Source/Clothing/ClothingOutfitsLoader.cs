using Newtonsoft.Json;
using SaffronLib;
using System.Collections.Generic;
using System.IO;

namespace OutfitsIncluded.Clothing
{

	public static class ClothingOutfitsLoader
	{
		public class OutfitDataList
		{
			public List<ClothingOutfitData> outfits;
		}

		public static List<ClothingOutfitData> LoadFromJSONFile(string filePath)
		{
			if (!File.Exists(filePath))
			{
				Log.WriteDebug($"No file found at path: {filePath}");
				return null;
			}
			Log.WriteDebug($"Loading outfit data from {filePath}.");

			string json = FileUtils.LoadAsString(filePath);
			var data = JsonConvert.DeserializeObject<OutfitDataList>(json);
			if (data == null || data.outfits == null)
			{
				Log.WriteError($"No outfits found in {filePath}.");
				return null;
			}

			List<ClothingOutfitData> validOutfits = data.outfits.FindAll(x => x.IsValid());
			Log.WriteDebug($"Outfits loaded (valid/total): {validOutfits.Count}/{data.outfits.Count}");

			return validOutfits;
		}
	}
}
