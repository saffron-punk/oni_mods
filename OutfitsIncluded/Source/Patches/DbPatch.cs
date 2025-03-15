using HarmonyLib;
using SaffronLib;

namespace OutfitsIncluded.Patches
{
	public class DbPatch
	{

		[HarmonyPatch(typeof(Db)), HarmonyPatch("Initialize")]
		public class Db_Initialize_Patch
		{
			public static void Prefix()
			{
				Log.WriteMethodName();
				ClothingItemsPatch.Patch(Core.OIMod.HarmonyInstance);
				ClothingOutfitsPatch.Patch(Core.OIMod.HarmonyInstance);
			}
		}
	}
}
