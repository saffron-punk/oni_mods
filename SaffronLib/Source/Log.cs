using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Reflection;

namespace SaffronLib
{
	public static class Log
	{
		public enum LogLevel : ushort
		{
			Trace = 0,
			Debug = 1,
			Info = 2,
			Warning = 3,
			Error = 4,
			None = 5,
		}

		public static LogLevel CurrentLogLevel = LogLevel.Info;

		private static string _modTag;
		public static void SetModName(string modName)
		{
			_modTag = $"[{modName}]";
		}

		public static void WriteTrace(object message)
		{
			if (CurrentLogLevel > LogLevel.Trace) { return; }
			Debug.Log($"(Trace) {_modTag} {message}");
		}

		public static void WriteDebug(object message)
		{
			if (CurrentLogLevel > LogLevel.Debug) { return; }
			Debug.Log($"(Debug) {_modTag} {message}");
		}

		public static void WriteInfo(object message)
		{
			if (CurrentLogLevel > LogLevel.Info) { return; }
			Debug.Log($"{_modTag} {message}");
		}

		public static void WriteWarning(object message)
		{
			if (CurrentLogLevel > LogLevel.Warning) { return; }
			Debug.LogWarning($"{_modTag} {message}");
		}

		public static void WriteError(object message)
		{
			if (CurrentLogLevel > LogLevel.Error) { return; }
			// Use LogWarning instead of LogError, because error will crash game
			// in dev mode.
			Debug.LogWarning($"{_modTag} ERROR: {message}");
		}

		public static void WriteMethodName()
		{
			StackTrace stackTrace = new StackTrace();
			MethodBase method = stackTrace.GetFrame(1).GetMethod();
			string methodName = method.Name;
			string className = method.ReflectedType.Name;

			WriteTrace(className + "." + methodName + "()");
		}

		public static void WriteObject(object obj, LogLevel logLevel = LogLevel.Trace)
		{
			if (CurrentLogLevel > logLevel) { return; }
			Debug.Log($"{_modTag} {obj}:");
			// https://stackoverflow.com/questions/852181/c-printing-all-properties-of-an-object
			foreach (PropertyDescriptor descriptor in TypeDescriptor.GetProperties(obj))
			{
				string name = descriptor.Name;
				object value = descriptor.GetValue(obj);
				Debug.Log($"\t{name}={value}");
			}
		}

		public static void WriteDict(Dictionary<string, string> dict, LogLevel logLevel = LogLevel.Trace)
		{
			if (CurrentLogLevel > logLevel) { return; }
			if (dict == null) { Debug.Log("null"); return; }
			Debug.Log(string.Join(Environment.NewLine, dict.Select(a => $"{a.Key}: {a.Value}")));
		}

	}
}
