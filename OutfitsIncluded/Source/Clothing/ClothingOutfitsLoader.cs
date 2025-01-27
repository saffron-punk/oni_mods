using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using _SaffronUtils;
using Database;

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
				Log.Error($"File not found at path: {filePath}");
				return null;
			}
			Log.Info($"Loading outfit data from {filePath}.");

			string json = FileUtils.LoadAsString(filePath);
			var data = JsonConvert.DeserializeObject<OutfitDataList>(json);
			if (data == null || data.outfits == null)
			{
				Log.Error($"No outfits found in {filePath}.");
				return null;
			}
			
#if DEBUG
			foreach (var outfit in data.outfits)
			{
				Log.ObjectData(outfit);
			}
#endif

			Log.Info($"All outfits: {data.outfits.Count}");
			List<ClothingOutfitData> validOutfits = data.outfits.FindAll(x => x.IsValid());
			Log.Info($"Valid outfits: {validOutfits.Count}");

			return validOutfits;
		}
	}
}
