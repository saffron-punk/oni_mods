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
	public class DbPatch
	{

		[HarmonyPatch(typeof(Db)), HarmonyPatch("Initialize")]
		public class Db_Initialize_Patch
		{
			public static void Prefix()
			{
				Log.Info("Db_Initialize_Patch.Prefix()");
				ClothingItemsPatch.Patch(Core.OutfitsIncluded.HarmonyInstance);
				ClothingOutfitsPatch.Patch(Core.OutfitsIncluded.HarmonyInstance);
			}

			public static void Postfix()
			{
				Log.Info("Db_Initialize_Patch.Postfix()");
			}
		}
	}
}
