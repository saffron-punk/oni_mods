using HarmonyLib;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using OutfitsIncluded.Core;
using _SaffronUtils;
using _SaffronUtils.Source;

namespace OutfitsIncluded.Patches
{
	public class LocalizationPatch
	{
		[HarmonyPatch(typeof(Localization), "Initialize")]
		public static class Localization_Initialize_Patch
		{
			[HarmonyPriority(Priority.VeryLow)]
			public static void Postfix()
			{
				Log.Info("Localization_Initialize_Patch.Postfix()");
				LocalizationUtils.RegisterForTranslation(
					typeof(OutfitsIncluded.STRINGS),
					OIMod.ModPath);
			}
		}
	}
}
