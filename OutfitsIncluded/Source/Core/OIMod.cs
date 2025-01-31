using HarmonyLib;
using KMod;
using System;
using System.Collections.Generic;
using System.IO;
using _SaffronUtils;
using OutfitsIncluded.Clothing;
using Database;
using OutfitsIncluded.OutfitPacks;

// Code for adding custom blueprints is based on Decor Pack A by Aki:
// https://github.com/aki-art/ONI-Mods/blob/master/DecorPackA/

namespace OutfitsIncluded.Core
{
	public class OIMod : UserMod2
	{
		public static Harmony HarmonyInstance;
		public static string ModPath;

		public static HashSet<OutfitPack> OutfitPacks;

		public override void OnLoad(Harmony harmony)
		{
			HarmonyInstance = harmony;
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

			// TODO: Patch if outfit pack count > 0
			harmony.PatchAll(assembly);
		}
	}
}
