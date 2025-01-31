using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static OutfitsIncluded.Core.OIConstants;

namespace OutfitsIncluded
{
	public class STRINGS
	{
		public static class OUTFITS_INCLUDED
		{
			public static LocString DESCRIPTION_ATTR = 
				$"Part of " +
				$"<i><color={OUTFIT_PACK_COLOR_TAG}>{OUTFIT_PACK_NAME_TAG}</color></i> " +
				$"(added by <b>Outfits Included</b>).";
		}
	}
}
