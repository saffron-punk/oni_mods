using HarmonyLib;
using SaffronLib;
using System;

namespace OutfitsIncluded.Patches
{
	public class WearableAccessorizerPatch
	{
		[HarmonyPatch(typeof(WearableAccessorizer))]
		[HarmonyPatch(nameof(WearableAccessorizer.UpdateVisibleSymbols))]
		[HarmonyPatch(new Type[] { typeof(WearableAccessorizer.WearableType) })]
		public class WearableAccessorizer_UpdateVisibleSymbols_Patch
		{
			public static void Postfix(WearableAccessorizer __instance)
			{
				Log.Info("WearableAccessorizer_UpdateVisibleSymbols_Patch.Postfix()");
				KAnimControllerBase animController = (KAnimControllerBase)Traverse.Create(__instance).Field("animController").GetValue();
				animController.SetSymbolVisiblity(Db.Get().AccessorySlots.Belt.targetSymbolId, true);
			}
		}
	}
}
