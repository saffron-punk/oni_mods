using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;

namespace SaffronLib
{
	// References:
	// https://github.com/Sgt-Imalas/Sgt_Imalas-Oni-Mods/blob/master/UtilLibs/LocalisationUtil.cs
	// https://github.com/aki-art/ONI-Mods/blob/master/Futility/FLocalization/Translations.cs#L21

	// Should be accessed from Localization initialize postfix patch.
	// Otherwise, the locale code may not be assigned yet.

	public static class LocalizationUtils
	{
		private const string TRANSLATIONS_DIR = "translations";
		private const string TEMPLATE_FILE_NAME = "translation_template.pot";

		public static void RegisterForTranslation(
				Type root,
				string modPath,
				string translationsDir = TRANSLATIONS_DIR,
				bool generateTemplate = true)
		{
			Log.Info($"Registering {root.Name} for translation...");
			Localization.RegisterForTranslation(root);
			string translationsPath = Path.Combine(modPath, translationsDir);
			OverloadStrings(translationsPath);
			LocString.CreateLocStringKeys(root, null);
			if (generateTemplate) { GenerateTemplate(root, translationsPath); }
		}

		private static void OverloadStrings(string translationsPath)
		{
			string path = GetFilePathForCurrentLocale(translationsPath);
			if (path.IsNullOrWhiteSpace()) { return; }
			Localization.OverloadStrings(Localization.LoadStringsFile(path, false));
			Log.Info($"Loaded translation file at {path}.");
		}

		public static void GenerateTemplate(Type root, string translationsPath)
		{
			if (!Directory.Exists(translationsPath))
			{
				Directory.CreateDirectory(translationsPath);
			}
			Localization.GenerateStringsTemplate(
				root.Namespace,
				Assembly.GetExecutingAssembly(),
				Path.Combine(translationsPath, TEMPLATE_FILE_NAME),
				null);
		}

		public static Dictionary<string, string> LoadCustomStrings(
				string translationsPath)
		{
			string filePath = GetFilePathForCurrentLocale(translationsPath);
			if (filePath.IsNullOrWhiteSpace()) { return null; }

			if (!File.Exists(filePath)) { return null; }

			Dictionary<string, string> dict;
			try
			{
				dict = Localization.LoadStringsFile(filePath, false);
			}
			catch (Exception ex)
			{
				Log.Error($"Error loading custom strings from {translationsPath}: {ex}");
				dict = null;
			}
			return dict;
		}

		// Based on ONI's Localization class GenerateStringsTemplate() and WriteStringsTemplate()
		public static void GenerateCustomTemplate(
				Dictionary<string, string> dict,
				string modName,
				string translationsPath)
		{
			if (dict == null)
			{
				Log.Error("GenerateCustomTemplate(): Dict is null.");
				return;
			}

			if (!Directory.Exists(translationsPath))
			{
				Directory.CreateDirectory(translationsPath);

			}
			string filePath = Path.Combine(translationsPath, TEMPLATE_FILE_NAME);

			using (StreamWriter writer = new StreamWriter(
				filePath,
				false,
				(Encoding)new UTF8Encoding(false)))
			{
				writer.WriteLine("msgid \"\"");
				writer.WriteLine("msgstr \"\"");
				writer.WriteLine($"\"Application: {modName}\"");
				writer.WriteLine("\"POT Version: 2.0\"");
				writer.WriteLine("");
				foreach (KeyValuePair<string, string> kvp in dict)
				{
					string key = kvp.Key;
					string value = kvp.Value
						.Replace("\\", "\\\\")
						.Replace("\"", "\\\"")
						.Replace("\n", "\\n")
						.Replace("’", "'")
						.Replace("“", "\\\"")
						.Replace("”", "\\\"")
						.Replace("…", "...");
					writer.WriteLine("#. {key}" + key);
					writer.WriteLine($"msgctxt \"{key}\"");
					writer.WriteLine("msgid \"" + value + "\"");
					writer.WriteLine("msgstr \"\"");
					writer.WriteLine("");
				}
			}

			Log.Status($"Custom translations template created: {translationsPath}");
		}

		private static string GetFilePathForCurrentLocale(string translationsPath)
		{
			string code = Localization.GetLocale()?.Code;
			Log.Info($"Code={code}");
			if (code.IsNullOrWhiteSpace())
			{
				return null;
			}

			var path = Path.Combine(translationsPath, code + ".po");
			if (!File.Exists(path))
			{
				return null;
			}
			return path;
		}

		public static string GetLocaleCode()
		{
			return Localization.GetLocale()?.Code;
		}
	}
}
