using HarmonyLib;
using OutfitsIncluded.Core;
using SaffronLib;
using UnityEngine;

namespace OutfitsIncluded.Patches
{
	public class BaseMinionConfigPatch
	{
		[HarmonyPatch(typeof(BaseMinionConfig))]
		[HarmonyPatch(nameof(BaseMinionConfig.BaseMinion))]
		public class BaseMinionConfig_BaseMinion_Patch
		{
			public static void Postfix(GameObject __result)
			{
				Log.Info("BaseMinionConfig_BaseMinion_Patch: Postfix()");
				GameObject go = __result;

				if (go.IsNullOrDestroyed())
				{
					Log.Error("BaseMinion is null.");
					return;
				}

				go.AddOrGet<OutfitRestorer>();
				Log.Info($"Added OutfitRestorer component to {go}");
			}
		}
	}
}

