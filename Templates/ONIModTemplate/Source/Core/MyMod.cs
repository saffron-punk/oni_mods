using HarmonyLib;
using KMod;
using System;
using System.Collections.Generic;


namespace ONIModTemplate.Core
{
	public class MyMod : UserMod2
	{
		public static Harmony HarmonyInstance;
		public static string ModPath;

		public override void OnLoad(Harmony harmony)
		{
			HarmonyInstance = harmony;
			ModPath = path;

			base.OnLoad(harmony); // PatchAll()
		}
	}
}
