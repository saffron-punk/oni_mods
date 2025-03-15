using OutfitsIncluded.Core;
using SaffronLib;


namespace OutfitsIncluded.Clothing
{
	public abstract class ClothingData
	{
		public string Id { get; protected set; }
		private bool _valid = true;
		public string Name { get; protected set; }
		public string Description { get; protected set; }
		public string StringIdBase { get; set; }

		public OutfitPacks.OutfitPack outfitPack { get; set; }

		public string GetStringIdName()
		{
			return StringIdBase + "." + OIConstants.NAME_STRING;
		}

		public string GetStringIdDescription()
		{
			return StringIdBase + "." + OIConstants.DESC_STRING;
		}

		public string GetLocalizedName()
		{
			// If the OutfitPack created the strings correctly,
			// Strings.Get() should always return a value.
			// But we will handle failures in case something went wrong.
			if (Strings.TryGet(GetStringIdName(), out StringEntry result))
			{
				return result.String;
			}
			else
			{
				LogWarning($"String not found for ID={GetStringIdName()}");
				return Name;
			}
		}

		public string GetLocalizedDescription()
		{
			string locDesc;
			if (Strings.TryGet(GetStringIdDescription(), out StringEntry result))
			{
				locDesc = result.String;
			}
			else
			{
				LogWarning($"String not found for ID={GetStringIdDescription()}");
				locDesc = Description;
			}

			string descAttrProp = "STRINGS.OUTFITS_INCLUDED.DESCRIPTION_ATTR";
			if (outfitPack.Mod == OIMod.ModInstance)
			{
				descAttrProp = "STRINGS.OUTFITS_INCLUDED.SELF_DESCRIPTION_ATTR";
			}
			string descAttr = "";
			if (Strings.TryGet(descAttrProp, out StringEntry attrResult))
			{
				descAttr = attrResult.String;
			}

			if (descAttr.IsNullOrWhiteSpace() || outfitPack.Name.IsNullOrWhiteSpace())
			{
				LogWarning("Unable to add description attribution.");
			}
			else
			{
				descAttr = descAttr
					.Replace(OIConstants.OUTFIT_PACK_NAME_TAG, outfitPack.Name)
					.Replace(OIConstants.OUTFIT_PACK_COLOR_TAG, OIConstants.DefaultOutfitPackColor);
				if (locDesc.Length > 0)
				{
					locDesc += "\n\n" + descAttr;
				}
				else
				{
					locDesc = descAttr;
				}
			}

			return locDesc;
		}

		protected void MakeInvalid(string message)
		{
			Log.WriteError($"Error loading '{Id ?? "null"}': {message}");
			_valid = false;
		}
		protected void LogWarning(string message)
		{
			Log.WriteInfo($"Warning: '{Id ?? "null"}': {message}");
		}

		public bool IsValid()
		{
			return _valid;
		}

		public override string ToString()
		{
			return $"[{this.GetType().Name}:{Id}]";
		}

	}
}
