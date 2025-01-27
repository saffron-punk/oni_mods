using HarmonyLib;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using OutfitsIncluded.Core;
using _SaffronUtils;

namespace OutfitsIncluded.Patches
{
	public class LocalizationPatch
	{
		[HarmonyPatch(typeof(Localization), "Initialize")]
		public static class Localization_Initialize_Patch
		{
			public static void Postfix()
			{
				Log.Info("Localization_Initialize_Patch.Postfix()");
			}
		}
	}
}
