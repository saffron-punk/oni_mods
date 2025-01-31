using _SaffronUtils;
using OutfitsIncluded.Core;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OutfitsIncluded.Clothing
{
	public abstract class ClothingData
	{
		public string Id { get; protected set; }
		private bool _valid = true;
		public string Name { get; protected set; }
		public string Description { get; protected set; }
		public string StringIdBase { get; set; }

		public OutfitPacks.OutfitPack OutfitPack { get; set; }

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
				RegisterWarning($"String not found for ID={GetStringIdName()}");
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
				RegisterWarning($"String not found for ID={GetStringIdDescription()}");
				locDesc = Description;
			}

			string descAttr = "";
			if (Strings.TryGet("STRINGS.OUTFITS_INCLUDED.DESCRIPTION_ATTR", out StringEntry attrResult))
			{
				descAttr = attrResult.String;
			}

			if (descAttr.IsNullOrWhiteSpace() || OutfitPack.Name.IsNullOrWhiteSpace())
			{
				RegisterWarning("Unable to add description attribution.");
			}
			else
			{
				descAttr = descAttr
					.Replace(OIConstants.OUTFIT_PACK_NAME_TAG, OutfitPack.Name)
					.Replace(OIConstants.OUTFIT_PACK_COLOR_TAG, OIConstants.DefaultOutfitPackColor);
				locDesc += "\n\n" + descAttr;
			}

			return locDesc;
		}

		protected void RegisterError(string message)
		{
			Log.Error($"Error loading '{Id ?? "null"}': {message}");
			_valid = false;
		}
		protected void RegisterWarning(string message)
		{
			Log.Status($"Warning: '{Id ?? "null"}': {message}");
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
