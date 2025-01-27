using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _SaffronUtils
{
	public static class Log
	{
		private static string _modTag;
		public static void SetModName(string modName)
		{
			_modTag = $"[{modName}]";
		}

		public static void Status(object message)
		{
			Debug.Log($"{_modTag} {message}");
		}

		public static void Error(object message)
		{
			Debug.Log($"{_modTag} ERROR: {message}");
		}

		public static void Warning(object message)
		{
#if DEBUG
			Debug.Log($"{_modTag} WARNING: {message}");
#endif
		}

		public static void Info(object message)
		{
#if DEBUG
			Debug.Log($"{_modTag} {message}");
#endif
		}

		public static void ObjectData(object obj)
		{
#if DEBUG
			Debug.Log($"{_modTag} {obj}:");
			// https://stackoverflow.com/questions/852181/c-printing-all-properties-of-an-object
			foreach (PropertyDescriptor descriptor in TypeDescriptor.GetProperties(obj))
			{
				string name = descriptor.Name;
				object value = descriptor.GetValue(obj);
				Debug.Log($"\t{name}={value}");
			}
#endif
		}
	}
}
