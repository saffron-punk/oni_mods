using KMod;
using System;
using System.IO;
using _SaffronUtils;

namespace OutfitsIncluded.Core
{
	// https://github.com/aki-art/ONI-Mods/blob/master/Futility/FLocalization/Translations.cs#L21
	public class Translations
	{
		public static void Translate(Type root)
		{
			Localization.RegisterForTranslation(root);
			LoadStrings();
			Log.Info("Loading strings");
			LocString.CreateLocStringKeys(root, null);
		}
		public static void LoadStrings()
		{
			string code = Localization.GetLocale()?.Code;
			if (code.IsNullOrWhiteSpace())
			{
				return;
			}

			var path = Path.Combine(OutfitsIncluded.ModPath, "translations", code + ".po");
			if (File.Exists(path))
			{
				Localization.OverloadStrings(Localization.LoadStringsFile(path, false));
				Log.Info($"Found translation file for {code}.");
			}

		}
	}

}