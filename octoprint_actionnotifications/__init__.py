# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

import re

DEFAULT_ENABLE = True
DEFAULT_TYPE = "info"
DEFAULT_DURATION = 8
DEFAULT_NODUPLICATE = True
DEFAULT_FILTERS = []

class ActionNotificationsPlugin(octoprint.plugin.TemplatePlugin,
			octoprint.plugin.AssetPlugin,
			octoprint.plugin.SettingsPlugin,
			octoprint.plugin.ReloadNeedingPlugin):

	def __init__(self):
		self.enable = False
		self.type = ""
		self.duration = 0
		self.noduplicate = False
		self.filters = []

	def initialize(self):
		self._load_settings()

	def _load_settings(self):
		self.enable = self._settings.get_boolean(["enable"])
		self.type = self._settings.get(["type"])
		self.duration = self._settings.get_int(["duration"])
		self.noduplicate = self._settings.get_boolean(["noduplicate"])
		text_filters = self._settings.get(["filters"])

		if self.type not in ["notice", "info", "success", "error"]:
			self._logger.warning("Invalid type: %s", self.type)

			self.type = DEFAULT_TYPE

		if self.duration < 0 or self.duration > 86400:
			self._logger.warning("Invalid duration: %s", self.duration)

			self.duration = DEFAULT_DURATION

		if not isinstance(text_filters, list):
			self._logger.warning("Invalid filters: %s", text_filters)

			text_filters = DEFAULT_FILTERS

		self._logger.debug("enable: %s", self.enable)
		self._logger.debug("type: %s", self.type)
		self._logger.debug("duration: %s", self.duration)
		self._logger.debug("noduplicate: %s", self.noduplicate)
		self._logger.debug("filters:")

		self.filters = []

		for text_filter in text_filters:
			text_filter = text_filter.strip()

			if not text_filter:
				continue

			try:
				self.filters.append(re.compile(text_filter, re.IGNORECASE))

				self._logger.debug(" - %s", text_filter)
			except re.error as err:
				self._logger.warning("Invalid filter: %s (%s)", text_filter, err)

	#~~ TemplatePlugin

	def get_template_configs(self):
		return [
			dict(
				type = "settings",
				custom_bindings = True
			)
		]

	#~~ AssetPlugin

	def get_assets(self):
		return dict(
			js = [
				"js/actionnotifications.js"
			],
			css = [
				"css/actionnotifications.css"
			]
		)

	#~~ SettingsPlugin

	def get_settings_defaults(self):
		return dict(
			enable = DEFAULT_ENABLE,
			type = DEFAULT_TYPE,
			duration = DEFAULT_DURATION,
			noduplicate = DEFAULT_NODUPLICATE,
			filters = DEFAULT_FILTERS
		)

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		self._load_settings()

	def action_handler(self, comm, line, action, *args, **kwargs):
		if not self.enable:
			return

		if not action.startswith("notification "):
			return

		text = action[13:].strip()

		if not text:
			return

		for regex in self.filters:
			if regex.search(text) is not None:
				return

		self._logger.debug("Sending notification: %s", text)

		self._plugin_manager.send_plugin_message(self._identifier, dict(
			text = text,
			type = self.type,
			duration = self.duration,
			noduplicate = self.noduplicate
		))

__plugin_name__ = "Action Notifications"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	plugin = ActionNotificationsPlugin()

	global __plugin_implementation__
	__plugin_implementation__ = plugin

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.action": plugin.action_handler
	}
