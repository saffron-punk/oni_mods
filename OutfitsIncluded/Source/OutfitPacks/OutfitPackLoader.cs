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

				Log.Info($"Found outfit pack: <{mod.staticID}>.");
				OutfitPack outfitPack = new OutfitPack(mod, path);
				outfitPacks.Add(outfitPack);
			}

			return outfitPacks;
		}
	}
}
