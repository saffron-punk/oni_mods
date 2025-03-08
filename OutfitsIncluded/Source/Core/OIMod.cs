using Database;
using HarmonyLib;
using KMod;
using OutfitsIncluded.OutfitPacks;
using SaffronLib;
using System.Collections.Generic;


namespace OutfitsIncluded.Core
{
	public class OIMod : UserMod2
	{
		public static Harmony HarmonyInstance;
		public static Mod ModInstance;
		public static string ModPath;

		public static OutfitPack OIOutfitPack;
		public static List<OutfitPack> OutfitPacks;
		public static List<OutfitRestorer> OutfitRestorers = new List<OutfitRestorer>();
		public static Dictionary<string, ClothingItemResource> OIItemResources = new Dictionary<string, ClothingItemResource>();

		public override void OnLoad(Harmony harmony)
		{
			HarmonyInstance = harmony;
			ModInstance = mod;
			ModPath = path;

			Log.SetModName(mod.staticID);

			//base.OnLoad(harmony); // PatchAll()
		}

		public override void OnAllModsLoaded(Harmony harmony, IReadOnlyList<Mod> mods)
		{
			OutfitPacks = OutfitPackLoader.LoadAll(mods);
			if (OutfitPacks.Count == 0)
			{
				Log.Status("No outfit packs found.");
				return;
			}
			Log.Info($"Found {OutfitPacks.Count} outfit packs.");

			foreach (OutfitPack outfitPack in OutfitPacks)
			{
				if (outfitPack.Mod == ModInstance)
				{
					OIOutfitPack = outfitPack;
					break;
				}
			}

			if (OIOutfitPack == null)
			{
				Log.Warning("No Outfits Included outfit pack found.");
			}
			else
			{
				// Ensure that this mod's items are always parsed last.
				OutfitPacks.Remove(OIOutfitPack);
				OutfitPacks.Add(OIOutfitPack);
			}
			harmony.PatchAll(assembly);
		}
	}
}
