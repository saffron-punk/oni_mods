using _SaffronUtils;
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
