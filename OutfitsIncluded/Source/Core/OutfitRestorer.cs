using Database;
using HarmonyLib;
using KSerialization;
using SaffronLib;
using System;
using System.Collections.Generic;
using static ClothingOutfitUtility;

namespace OutfitsIncluded.Core
{
	// https://github.com/aki-art/ONI-Mods/blob/master/SpookyPumpkin/Content/Cmps/SpookyPumpkin_FacadeRestorer.cs#L9
	public class OutfitRestorer : KMonoBehaviour
	{
		[Serialize]
		public Dictionary<OutfitType, List<string>> savedClothingItems;

		// Injects the minion's components.
		// Sometimes they are null and referencing them will crash the game.
		// So we will verify they are not null on every entrance to this script.
#pragma warning disable CS0649 // Not assigned to
		[MyCmpGet] MinionIdentity identity;
		[MyCmpGet] WearableAccessorizer accessorizer;
#pragma warning restore CS0649

		protected override void OnSpawn()
		{
			Log.Info("\nOutfitRestorer:OnSpawn()");
			if (!ValidateComponents()) { return; }

			OIMod.OutfitRestorers.Add(this);
			RestoreOIClothing();
		}

		protected override void OnCleanUp()
		{
			Log.Info("OutfitRestorer:OnCleanUp()");
			OIMod.OutfitRestorers.Remove(this);
		}

		public void OnSaveStarted()
		{
			Log.Info("OutfitRestorer:OnSaveStarted()");
			if (!ValidateComponents()) { return; }
			RemoveOIClothing();
		}

		public void OnSaveFinished()
		{
			Log.Info("OutfitRestorer:OnSaveFinished()");
			if (!ValidateComponents()) { return; }
			RestoreOIClothing();
		}

		private void RemoveOIClothing()
		{
			Log.Info("OutfitRestorer:RemoveOIClothing()");
			Log.Info($"Processing: {identity.name}");

			// Clear old saved items.
			savedClothingItems = new Dictionary<OutfitType, List<string>>();

			Log.Info("Items before:");
			PrintCurrentOutfitItems();

			// We will avoid iterating OutfitType so we don't edit joy responses,
			// or any other future types we haven't explicitly supported.
			RemoveOIClothingByType(OutfitType.Clothing);
			RemoveOIClothingByType(OutfitType.AtmoSuit);

			Log.Info("Items after:");
			PrintCurrentOutfitItems();
			Log.Info("");
		}

		private void RemoveOIClothingByType(OutfitType outfitType)
		{
			// Always returns string[], so we do not need a null check.
			string[] itemIds = accessorizer.GetClothingItemsIds(outfitType);

			foreach (var itemId in itemIds)
			{
				if (itemId.IsNullOrWhiteSpace())
				{
					continue;
				}

				if (!OIMod.OIItemResources.TryGetValue(itemId, out var resource))
				{
					continue;
				}

				Log.Info($"Removing OI item: ({itemId}).");
				SaveClothingItem(outfitType, itemId);
				RemoveClothingItemFromDupe(outfitType, resource);
			}
		}

		private void RestoreOIClothing()
		{
			Log.Info("OutfitRestorer:RestoreOIClothing()");
			Log.Info($"Processing: {identity.name}");
			if (savedClothingItems.IsNullOrDestroyed() || savedClothingItems.Count == 0)
			{
				Log.Info("No saved outfit items to restore.");
				return;
			}

			Log.Info("Items before:");
			PrintCurrentOutfitItems();

			Log.Info("Saved items:");
			foreach ((OutfitType outfitType, List<string> itemIds) in savedClothingItems)
			{
				foreach (string itemId in itemIds)
				{
					if (!OIMod.OIItemResources.TryGetValue(itemId, out var resource))
					{
						Log.Error("No resource found for saved itemId={itemId}.");
						continue;
					}

					Log.Info($"Restoring OI clothing item: {itemId} ({outfitType})");
					AddClothingItemToDupe(outfitType, resource);
				}
			}

			Log.Info("Items after:");
			PrintCurrentOutfitItems();
			Log.Info("");

			RefreshDupeClothing();
		}


		private void SaveClothingItem(OutfitType outfitType, string itemId)
		{
			if (!savedClothingItems.ContainsKey(outfitType))
			{
				savedClothingItems[outfitType] = new List<string>();
			}
			savedClothingItems[outfitType].Add(itemId);
		}

		// We will use ClothingAccessorizer's private functions so we don't trigger
		// the clothing changed animation/sound.
		private void AddClothingItemToDupe(OutfitType outfitType, ClothingItemResource resource)
		{
			Traverse.Create(accessorizer)
				.Method("Internal_ApplyClothingItem",
						new Type[] { typeof(OutfitType), typeof(ClothingItemResource) })
				.GetValue(new object[] { outfitType, resource });
		}

		private void RemoveClothingItemFromDupe(OutfitType outfitType, ClothingItemResource resource)
		{
			Traverse.Create(accessorizer)
					.Method("Internal_RemoveClothingItem",
							new Type[] { typeof(OutfitType), typeof(ClothingItemResource) })
					.GetValue(new object[] { outfitType, resource });
		}

		private void RefreshDupeClothing()
		{
			// Makes changes visible.
			Traverse.Create(accessorizer)
				.Method("ApplyWearable", new Type[] { })
				.GetValue();
		}

		private bool ValidateComponents()
		{
			if (identity == null || accessorizer == null)
			{
				Log.Error("Error: Components not assigned.");
				return false;
			}
			return true;
		}

		private void PrintCurrentOutfitItems()
		{
#if DEBUG
			PrintOutfitItems(accessorizer.GetCustomClothingItems());
#endif
		}

		private static void PrintOutfitItems(Dictionary<OutfitType, List<ResourceRef<ClothingItemResource>>> outfitItems)
		{
#if DEBUG
			foreach (KeyValuePair<OutfitType, List<ResourceRef<ClothingItemResource>>> kvp in outfitItems)
			{
				Log.Info($"\t- {kvp.Key}");
				foreach (ResourceRef<ClothingItemResource> itemRef in kvp.Value)
				{
					ClothingItemResource item = itemRef.Get();
					Log.Info($"\t\t- {item.Id}");
				}
			}
#endif
		}
	}
}
