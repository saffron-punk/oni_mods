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
				Log.WriteMethodName();
				GameObject go = __result;

				if (go.IsNullOrDestroyed())
				{
					Log.WriteError("BaseMinion is null.");
					return;
				}

				go.AddOrGet<OutfitRestorer>();
				Log.WriteDebug($"Added OutfitRestorer component to {go}");
			}
		}
	}
}

