using KMod;
using OutfitsIncluded.Core;
using SaffronLib;
using System.Collections.Generic;
using System.IO;

namespace OutfitsIncluded.OutfitPacks
{
	public class OutfitPackLoader
	{
		public static List<OutfitPack> LoadAll(IReadOnlyList<Mod> mods)
		{
			var outfitPacks = new List<OutfitPack>();
			if (mods == null) { return outfitPacks; }

			foreach (Mod mod in mods)
			{
				if (!mod.IsEnabledForActiveDlc()) { continue; }
				string path = Path.Combine(mod.ContentPath, OIPaths.OutfitPackDir);
				if (!Directory.Exists(path)) { continue; }

				// If an Outfit Pack mod is in the "dev" mods folder,
				// change log level to at least debug.
				// (Since OI has its own "Outfit Pack", it being in the dev folder
				// will also trigger the change.)
				if (mod.IsDev)
				{
					if (Log.CurrentLogLevel > Log.LogLevel.Debug)
					{
						Log.CurrentLogLevel = Log.LogLevel.Debug;
					}
				}

				Log.WriteDebug($"Found outfit pack: <{mod.staticID}>.");
				OutfitPack outfitPack = new OutfitPack(mod, path);
				outfitPacks.Add(outfitPack);
			}

			return outfitPacks;
		}
	}
}
