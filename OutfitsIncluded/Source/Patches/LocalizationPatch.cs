using HarmonyLib;
using OutfitsIncluded.Core;
using SaffronLib;

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
				Log.WriteMethodName();
				LocalizationUtils.RegisterForTranslation(
					typeof(OutfitsIncluded.STRINGS),
					OIMod.ModPath);
			}
		}
	}
}
