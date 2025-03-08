using OutfitsIncluded.Clothing;
using OutfitsIncluded.Core;
using SaffronLib;
using System.Collections.Generic;
using System.IO;

namespace OutfitsIncluded.OutfitPacks
{
	public class OutfitPack
	{
		public KMod.Mod Mod { get; }
		public string DirPath { get; }
		private string _translationsPath { get; }

		public string Id { get => Mod.staticID; }

		public string Name { get => Mod.label.title; }

		// We will lazy load data since not all resources (i.e. kanims) required
		// for validation are loaded at the time the OutfitPack is created.
		private List<ClothingItemData> _clothingItems { get; set; } = null;
		private List<ClothingOutfitData> _clothingOutfits { get; set; } = null;

		private Dictionary<string, string> _strings { get; } = new Dictionary<string, string>();

		private Dictionary<string, string> _localizedStrings { get; set; }
		private bool _clothingItemStringsCreated = false;
		private bool _clothingOutfitStringsCreated = false;

		public OutfitPack(KMod.Mod mod, string path)
		{
			Mod = mod;
			DirPath = path;
			_translationsPath = Path.Combine(DirPath, OIPaths.OutfitPackTranslationsDir);
		}

		public List<ClothingItemData> GetClothingItems()
		{
			if (_clothingItems == null) { LoadClothingItems(); }
			return _clothingItems;
		}

		public List<ClothingOutfitData> GetClothingOutfits()
		{
			if (_clothingOutfits == null) { LoadClothingOutfits(); }
			return _clothingOutfits;
		}

		private void LoadClothingItems()
		{
			string itemsFile = Path.Combine(DirPath, OIPaths.ClothingItemsFile);
			_clothingItems =
				ClothingItemsLoader.LoadFromJSONFile(itemsFile)
				?? new List<ClothingItemData>();
			InjectOutfitPackRef(_clothingItems);
			Log.Info($"{this}: {_clothingItems.Count} clothing item(s) loaded.");

			RegisterClothingItems();
			CreateClothingItemStrings();
		}

		private void RegisterClothingItems()
		{
			// Duplicate list to iterate so we can edit the main list.
			List<ClothingItemData> clothingItemsCopy = new List<ClothingItemData>(_clothingItems);
			foreach (var item in clothingItemsCopy)
			{
				if (OIMod.OIItemResources.ContainsKey(item.Id))
				{
					Log.Error($"Duplicate item ids found: {item.Id}");
					_clothingItems.Remove(item);
					continue;
				}
				OIMod.OIItemResources[item.Id] = item.GetResource();
			}
		}

		private void CreateClothingItemStrings()
		{
			Dictionary<string, string> itemStrings = new Dictionary<string, string>();
			foreach (ClothingItemData item in _clothingItems)
			{
				item.StringIdBase =
					OIConstants.OI_STRING_CLASS + "."
					+ OIConstants.CLOTHING_ITEMS_STRING_CLASS + "."
					+ this.Id.ToUpperInvariant() + "."
					+ item.Id.ToUpperInvariant();

				itemStrings[item.GetStringIdName()] = item.Name ?? item.Id;
				itemStrings[item.GetStringIdDescription()] = item.Description ?? item.Id;
			}

			AddStringsToTemplate(itemStrings);
			AddLocalizedStringsToGame(itemStrings);

			_clothingItemStringsCreated = true;
			if (IsStringCreationComplete())
			{
				GenerateStringsTemplate();
			}
		}

		private void LoadClothingOutfits()
		{
			string outfitsFile = Path.Combine(DirPath, OIPaths.ClothingOutfitsFile);
			_clothingOutfits =
				ClothingOutfitsLoader.LoadFromJSONFile(outfitsFile)
				?? new List<ClothingOutfitData>();
			InjectOutfitPackRef(_clothingOutfits);
			Log.Info($"{this}: {_clothingOutfits.Count} clothing outfit(s) loaded.");

			CreateClothingOutfitStrings();

		}

		private void CreateClothingOutfitStrings()
		{
			Dictionary<string, string> outfitStrings = new Dictionary<string, string>();
			foreach (ClothingOutfitData outfit in _clothingOutfits)
			{
				outfit.StringIdBase =
					OIConstants.OI_STRING_CLASS + "."
					+ OIConstants.CLOTHING_OUTFITS_STRING_CLASS + "."
					+ this.Id.ToUpperInvariant() + "."
					+ outfit.Id.ToUpperInvariant();

				outfitStrings[outfit.GetStringIdName()] = outfit.Name ?? outfit.Id;
			}

			AddStringsToTemplate(outfitStrings);
			AddLocalizedStringsToGame(outfitStrings);

			_clothingOutfitStringsCreated = true;
			if (IsStringCreationComplete())
			{
				GenerateStringsTemplate();
			}
		}

		private void InjectOutfitPackRef<T>(List<T> clothingDataList)
		{
			for (int i = 0; i < clothingDataList.Count; i++)
			{
				(clothingDataList[i] as ClothingData).OutfitPack = this;
			}
		}

		private void AddStringsToTemplate(Dictionary<string, string> newStrings)
		{
			foreach (KeyValuePair<string, string> kvp in newStrings)
			{
				_strings[kvp.Key] = kvp.Value;
			}
		}

		private void AddLocalizedStringsToGame(Dictionary<string, string> originalStrings)
		{
			Dictionary<string, string> localizedStrings = GetLocalizedStrings();
			foreach (KeyValuePair<string, string> kvp in originalStrings)
			{
				string key = kvp.Key;
				string originalValue = kvp.Value;

				if (!localizedStrings.TryGetValue(key, out string value))
				{
					value = originalValue;
				}

				Strings.Add(key, value);
				//Log.Info($"Added string: {key}={value}; success={Strings.HasKey(key)}");
			}
		}

		private Dictionary<string, string> GetLocalizedStrings()
		{
			// We will lazy load localized strings since we may not have correct
			// localization code at the time the OutfitPack is created.
			if (_localizedStrings == null)
			{
				_localizedStrings = LocalizationUtils.LoadCustomStrings(_translationsPath);
				if (_localizedStrings == null)
				{
					Log.Warning($"{this}: No localization found for code '{LocalizationUtils.GetLocaleCode()}'.");
					_localizedStrings = new Dictionary<string, string>();
				}
				else
				{
					Log.Info($"{this}: Localization loaded: {_localizedStrings?.Count ?? null} entries");
					Log.PrintDict(_localizedStrings);
				}
			}
			return _localizedStrings;
		}

		private bool IsStringCreationComplete()
		{
			return _clothingItemStringsCreated && _clothingOutfitStringsCreated;
		}

		private void GenerateStringsTemplate()
		{
			PrintData();
			LocalizationUtils.GenerateCustomTemplate(
				_strings,
				"Outfits Included",
				_translationsPath);
		}
		private void PrintData()
		{
#if DEBUG
			Log.Info(Name);
			Log.Info($"\tClothing items:");
			foreach (var item in _clothingItems)
			{
				Log.PrintObject(item);
			}
			Log.Info($"\tClothing outfits:");
			foreach (var outfit in _clothingOutfits)
			{
				Log.PrintObject(outfit);
			}
#endif
		}

		public override string ToString()
		{
			return $"[OutfitPack:{Id}]";
		}
	}
}
