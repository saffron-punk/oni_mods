using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _SaffronUtils
{
	public class FileUtils
	{
		public static string LoadAsString(string filepath)
		{
			string s = null;
			try
			{
				using (var r = new StreamReader(filepath))
				{
					s = r.ReadToEnd();
				}

			}
			catch (Exception e)
			{
				Log.Error($"Error loading {filepath}: {e}");
			}
			return s;
		}
	}
}
