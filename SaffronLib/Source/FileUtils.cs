using System;
using System.IO;

namespace SaffronLib
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
				Log.WriteError($"Error loading {filepath}: {e}");
			}
			return s;
		}
	}
}
