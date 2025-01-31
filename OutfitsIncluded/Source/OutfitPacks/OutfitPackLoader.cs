using KMod;
using _SaffronUtils;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static STRINGS.UI.FRONTEND;
using OutfitsIncluded.Core;
using OutfitsIncluded.Clothing;

namespace OutfitsIncluded.OutfitPacks
{
	public class OutfitPackLoader
	{
		public static HashSet<OutfitPack> LoadAll(IReadOnlyList<Mod> mods)
		{
			var outfitPacks = new HashSet<OutfitPack>();
			if (mods == null) { return outfitPacks; }

			foreach (Mod mod in mods)
			{
				string path = Path.Combine(mod.ContentPath, OIPaths.OutfitPackDir);
				// TODO: mod.enabled yields false negatives for enabled mods.
				// But, without a check, OI attempts to load disabled mods.
				// The kanims in disabled mods won't load,
				// so OI won't actually load the clothing items.
				// But there must be a cleaner way to check here...
				//if (!mod.enabled) { continue; }
				if (!Directory.Exists(path)) { continue; }
				Log.Info($"Found outfit pack: {mod.staticID}");
				outfitPacks.Add(new OutfitPack(mod, path));
			}

			return outfitPacks;
		}
	}
}
