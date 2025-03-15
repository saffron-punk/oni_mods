using HarmonyLib;
using OutfitsIncluded.Core;
using SaffronLib;
using System;

namespace OutfitsIncluded.Patches
{
	// https://github.com/aki-art/ONI-Mods/blob/master/SpookyPumpkin/Patches/SaveLoaderPatch.cs
	[HarmonyPatch(typeof(SaveLoader))]
	[HarmonyPatch(nameof(SaveLoader.Save))]
	[HarmonyPatch(new Type[] { typeof(string), typeof(bool), typeof(bool) })]
	public class SaveLoader_Save_Patch
	{
		public static void Prefix()
		{
			Log.WriteMethodName();
			foreach (OutfitRestorer outfitRestorer in OIMod.OutfitRestorers)
			{
				outfitRestorer.OnSaveStarted();
			}
		}

		public static void Postfix()
		{
			Log.WriteMethodName();
			foreach (OutfitRestorer outfitRestorer in OIMod.OutfitRestorers)
			{
				outfitRestorer.OnSaveFinished();
			}
		}
	}
}
